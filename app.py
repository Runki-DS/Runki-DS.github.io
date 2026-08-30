# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import subprocess
import sys
import os
import tempfile
import re

app = Flask(__name__)

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_company():
    """Запускает brusnika_prepay.py с переданным ИНН"""
    
    inn = request.form.get('inn', '').strip()
    
    if not inn:
        return jsonify({'error': 'Пожалуйста, введите ИНН'})
    
    if len(inn) != 10 and len(inn) != 12:
        return jsonify({'error': 'ИНН должен содержать 10 или 12 цифр'})
    
    if not inn.isdigit():
        return jsonify({'error': 'ИНН должен содержать только цифры'})
    
    try:
        # Создаем временный файл для вывода
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp:
            tmp_path = tmp.name
        
        # Запускаем скрипт
        process = subprocess.Popen(
            [sys.executable, 'brusnika_prepay.py'],
            stdin=subprocess.PIPE,
            stdout=open(tmp_path, 'w'),
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Передаем ИНН в скрипт (как в оригинале)
        process.stdin.write(inn + '\n')
        process.stdin.close()
        
        # Ждем завершения (максимум 30 секунд)
        process.wait(timeout=30)
        
        # Читаем результат
        with open(tmp_path, 'r', encoding='utf-8') as f:
            output = f.read()
        
        # Удаляем временный файл
        os.unlink(tmp_path)
        
        # Проверяем ошибки
        if process.returncode != 0:
            error_output = process.stderr.read()
            return jsonify({'error': f'Ошибка скрипта: {error_output}'})
        
        # Формируем результат
        result = {
            'output': output,
            'lines': output.strip().split('\n')
        }
        
        # Парсим вывод для структурированного отображения
        parsed = parse_output(output)
        result.update(parsed)
        
        return jsonify(result)
        
    except subprocess.TimeoutExpired:
        process.kill()
        return jsonify({'error': 'Превышено время ожидания (30 секунд)'})
    except Exception as e:
        return jsonify({'error': f'Ошибка: {str(e)}'})

def parse_output(output):
    """Парсит вывод скрипта"""
    
    result = {}
    lines = output.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        
        if 'Проверяемая компания' in line:
            parts = line.replace('Проверяемая компания', '').strip()
            if 'ИНН' in parts:
                name_parts = parts.split('ИНН')
                result['company_name'] = name_parts[0].strip()
                result['inn'] = name_parts[1].strip() if len(name_parts) > 1 else ''
                
        elif 'Возраст компании' in line:
            age_match = re.search(r'(\d+)', line)
            if age_match:
                result['age'] = age_match.group(1)
                
        elif 'Данные бухгалтерской отчетности не найдены' in line:
            result['bo'] = 'no'
            result['error'] = 'Данные бухгалтерской отчетности не найдены'
            
        elif 'Авансирование допускается' in line:
            result['prepay'] = 'yes'
            
        elif 'Авансирование не допускается' in line:
            result['prepay'] = 'no'
            
        elif 'Сумма допустимого аванса' in line:
            # Ищем цифры с пробелами и ₽
            match = re.search(r'(\d[\d\s]+)₽', line)
            if match:
                result['max_debt'] = match.group(1).strip()
            else:
                # Пробуем найти просто цифры
                match = re.search(r'(\d+[\d\s]*\d+)', line)
                if match:
                    result['max_debt'] = match.group(1).strip()
                    
        elif 'Ориентировочный срок выполнения обязательств' in line:
            match = re.search(r'(\d+)', line)
            if match:
                result['cred_day'] = match.group(1)
                
        elif 'Слишком большой срок выполнения обязательств' in line:
            result['cred_day_warning'] = True
            match = re.search(r'(\d+)', line)
            if match:
                result['cred_day'] = match.group(1)
                
        elif 'Стоимость чистых активов' in line:
            match = re.search(r'(\d[\d\s]+)₽', line)
            if match:
                result['equity'] = match.group(1).strip()
    
    # Если данные бухгалтерской отчетности есть, но нет prepay
    if not result.get('bo') == 'no' and not result.get('prepay'):
        result['error'] = 'Не удалось определить кредитоспособность'
    
    return result

if __name__ == '__main__':
    print("🚀 Сервер запущен на http://localhost:5000")
    print("Нажмите Ctrl+C для остановки")
    app.run(debug=True, host='0.0.0.0', port=5000)