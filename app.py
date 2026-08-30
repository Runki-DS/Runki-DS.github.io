# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, send_from_directory
import subprocess
import sys
import os
import tempfile
import re

app = Flask(__name__)

# HTML страница прямо в коде
HTML_PAGE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Проверка кредитоспособности — Брусника</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f3f0ea;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            color: #2c2c2c;
        }

        .container {
            background: #ffffff;
            border-radius: 24px;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.06);
            padding: 48px 40px 32px;
            max-width: 640px;
            width: 100%;
            transition: all 0.2s ease;
        }

        .header {
            text-align: left;
            margin-bottom: 36px;
            border-bottom: 1px solid #e8e3dc;
            padding-bottom: 24px;
        }

        .header h1 {
            font-size: 28px;
            font-weight: 600;
            letter-spacing: -0.02em;
            color: #1a1a1a;
            margin-bottom: 8px;
        }

        .header h1 span {
            color: #a67c52;
        }

        .header .subtitle {
            font-size: 16px;
            color: #6b5f52;
            font-weight: 400;
            letter-spacing: 0.01em;
        }

        .badge {
            display: inline-block;
            background: #e8e3dc;
            color: #4a3f35;
            padding: 4px 14px;
            border-radius: 40px;
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            margin-top: 12px;
        }

        .input-section {
            margin-bottom: 28px;
        }

        .input-group {
            display: flex;
            gap: 12px;
            align-items: stretch;
        }

        .input-group input {
            flex: 1;
            padding: 16px 20px;
            border: 1px solid #d6cfc6;
            border-radius: 60px;
            font-size: 16px;
            font-weight: 400;
            background: #faf8f6;
            color: #1a1a1a;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
            outline: none;
            font-family: inherit;
        }

        .input-group input::placeholder {
            color: #a89b8c;
        }

        .input-group input:focus {
            border-color: #a67c52;
            box-shadow: 0 0 0 3px rgba(166, 124, 82, 0.12);
            background: #ffffff;
        }

        .input-group input:disabled {
            background: #f0ece6;
            cursor: not-allowed;
        }

        .input-group button {
            padding: 0 32px;
            background: #1a1a1a;
            color: white;
            border: none;
            border-radius: 60px;
            font-size: 16px;
            font-weight: 500;
            letter-spacing: 0.02em;
            cursor: pointer;
            transition: background 0.2s ease, transform 0.1s ease;
            white-space: nowrap;
            font-family: inherit;
            min-height: 58px;
        }

        .input-group button:hover:not(:disabled) {
            background: #2c2c2c;
        }

        .input-group button:active:not(:disabled) {
            transform: scale(0.97);
        }

        .input-group button:disabled {
            background: #b5aaa0;
            cursor: not-allowed;
            opacity: 0.7;
        }

        .input-hint {
            margin-top: 10px;
            font-size: 13px;
            color: #8a7e71;
            padding-left: 8px;
            letter-spacing: 0.01em;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 32px 0 16px;
        }

        .loading.show {
            display: block;
        }

        .spinner {
            display: inline-block;
            width: 36px;
            height: 36px;
            border: 3px solid #e8e3dc;
            border-top: 3px solid #a67c52;
            border-radius: 50%;
            animation: spin 0.9s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            margin-top: 14px;
            color: #6b5f52;
            font-size: 15px;
            font-weight: 400;
            letter-spacing: 0.01em;
        }

        .result {
            margin-top: 24px;
            display: none;
        }

        .result.show {
            display: block;
            animation: fadeUp 0.4s ease;
        }

        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .result-card {
            background: #faf8f6;
            border-radius: 20px;
            padding: 28px 28px 24px;
            border: 1px solid #e8e3dc;
        }

        .result-card.error {
            border-left: 4px solid #c0392b;
        }

        .result-card.success {
            border-left: 4px solid #2e7d5e;
        }

        .result-card.warning {
            border-left: 4px solid #b8860b;
        }

        .company-header {
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid #e8e3dc;
        }

        .company-name {
            font-size: 20px;
            font-weight: 600;
            color: #1a1a1a;
            letter-spacing: -0.01em;
        }

        .company-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px 18px;
            margin-top: 6px;
            font-size: 14px;
            color: #6b5f52;
        }

        .company-meta span {
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        .info-grid {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #ede8e2;
        }

        .info-row:last-child {
            border-bottom: none;
        }

        .label {
            font-size: 15px;
            color: #6b5f52;
            font-weight: 400;
        }

        .value {
            font-weight: 500;
            color: #1a1a1a;
            text-align: right;
            font-size: 15px;
        }

        .value.green {
            color: #2e7d5e;
        }

        .value.red {
            color: #c0392b;
        }

        .value.gold {
            color: #b8860b;
        }

        .value.bold {
            font-weight: 600;
        }

        .alert {
            padding: 14px 18px;
            border-radius: 12px;
            margin: 12px 0 8px;
            font-size: 14px;
            line-height: 1.5;
            background: #f8f5f0;
            border: 1px solid #e8e3dc;
        }

        .alert-success {
            background: #edf5f0;
            border-color: #c5ddd0;
            color: #1a4a3a;
        }

        .alert-danger {
            background: #f5edec;
            border-color: #e8d5d2;
            color: #7a3a32;
        }

        .alert-warning {
            background: #f5f0e8;
            border-color: #e8ddd0;
            color: #7a6a3a;
        }

        .alert-info {
            background: #f0f2f5;
            border-color: #d5dae8;
            color: #3a4a6a;
        }

        .small-note {
            font-size: 12px;
            color: #8a7e71;
            text-align: right;
            margin-top: 4px;
            letter-spacing: 0.01em;
        }

        .toggle-output {
            margin-top: 18px;
            color: #8a7e71;
            cursor: pointer;
            font-size: 13px;
            text-align: center;
            user-select: none;
            padding: 8px 0;
            border-top: 1px solid #ede8e2;
            transition: color 0.2s ease;
            letter-spacing: 0.01em;
        }

        .toggle-output:hover {
            color: #4a3f35;
        }

        .raw-output {
            display: none;
            margin-top: 14px;
            padding: 16px 18px;
            background: #f0ece6;
            border-radius: 12px;
            font-family: 'SF Mono', 'Menlo', 'Monaco', monospace;
            font-size: 12px;
            line-height: 1.7;
            white-space: pre-wrap;
            max-height: 260px;
            overflow: auto;
            color: #3a3a3a;
            border: 1px solid #e0d9d0;
        }

        .raw-output.show {
            display: block;
        }

        .footer {
            text-align: center;
            margin-top: 32px;
            padding-top: 20px;
            border-top: 1px solid #e8e3dc;
            font-size: 13px;
            color: #8a7e71;
            letter-spacing: 0.01em;
        }

        @media (max-width: 600px) {
            .container {
                padding: 28px 18px 24px;
                border-radius: 18px;
            }

            .header h1 {
                font-size: 24px;
            }

            .input-group {
                flex-direction: column;
                gap: 10px;
            }

            .input-group input {
                border-radius: 40px;
                padding: 14px 18px;
            }

            .input-group button {
                width: 100%;
                padding: 14px;
                min-height: 52px;
                border-radius: 40px;
            }

            .result-card {
                padding: 20px 16px;
            }

            .info-row {
                flex-direction: column;
                align-items: flex-start;
                gap: 4px;
                padding: 10px 0;
            }

            .value {
                text-align: left;
                width: 100%;
            }

            .company-meta {
                flex-direction: column;
                gap: 4px;
            }
        }

        @media (max-width: 400px) {
            .container {
                padding: 20px 12px;
            }

            .header h1 {
                font-size: 20px;
            }

            .badge {
                font-size: 10px;
                padding: 3px 12px;
            }
        }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>Проверка <span>кредитоспособности</span></h1>
        <p class="subtitle">Оцените возможность авансирования для вашего контрагента</p>
        <div class="badge">Брусника</div>
    </div>

    <div class="input-section">
        <div class="input-group">
            <input type="text" id="innInput" placeholder="Введите ИНН (10 или 12 цифр)" maxlength="12">
            <button id="checkBtn" onclick="checkCompany()">Проверить</button>
        </div>
        <div class="input-hint">Например: 7707083893</div>
    </div>

    <div class="loading" id="loading">
        <div class="spinner"></div>
        <div class="loading-text">Загружаем данные...<br><span style="font-size: 13px; color: #a89b8c;">Обычно это занимает 5–10 секунд</span></div>
    </div>

    <div class="result" id="result"></div>

    <div class="footer">
        Данные предоставлены сервисом Контур.Фокус
    </div>
</div>

<script>
    const innInput = document.getElementById('innInput');
    const checkBtn = document.getElementById('checkBtn');
    const loading = document.getElementById('loading');
    const resultDiv = document.getElementById('result');

    innInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') checkCompany();
    });

    innInput.addEventListener('input', function() {
        this.value = this.value.replace(/\\D/g, '');
    });

    async function checkCompany() {
        const inn = innInput.value.trim();

        if (!inn) {
            showResult('Пожалуйста, введите ИНН', 'error');
            innInput.focus();
            return;
        }

        if (!/^\\d{10}$|^\\d{12}$/.test(inn)) {
            showResult('ИНН должен содержать 10 или 12 цифр', 'error');
            innInput.focus();
            return;
        }

        checkBtn.disabled = true;
        checkBtn.textContent = '⏳';
        loading.classList.add('show');
        resultDiv.classList.remove('show');

        try {
            const formData = new FormData();
            formData.append('inn', inn);

            const response = await fetch('/check', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                showResult(data.error, 'error');
            } else {
                displayResult(data);
            }
        } catch (error) {
            showResult('Ошибка соединения. Убедитесь, что сервер запущен: python app.py', 'error');
        } finally {
            checkBtn.disabled = false;
            checkBtn.textContent = 'Проверить';
            loading.classList.remove('show');
        }
    }

    function showResult(message, type = 'info') {
        let icon = 'ℹ️';
        let className = 'result-card';

        if (type === 'error') {
            icon = '❌';
            className += ' error';
        } else if (type === 'success') {
            icon = '✅';
            className += ' success';
        } else if (type === 'warning') {
            icon = '⚠️';
            className += ' warning';
        }

        resultDiv.innerHTML = `
            <div class="${className}">
                <div class="alert alert-${type === 'error' ? 'danger' : type === 'warning' ? 'warning' : 'info'}">
                    ${icon} ${message}
                </div>
            </div>
        `;
        resultDiv.classList.add('show');
    }

    function displayResult(data) {
        let html = '<div class="result-card">';

        if (data.company_name) {
            html += `
                <div class="company-header">
                    <div class="company-name">${data.company_name}</div>
                    <div class="company-meta">
                        <span>ИНН: ${data.inn || '—'}</span>
                        ${data.age ? `<span>Возраст: ${data.age} лет</span>` : ''}
                    </div>
                </div>
            `;
        }

        if (data.error && data.error !== 'Данные бухгалтерской отчетности не найдены') {
            html += `<div class="alert alert-danger">❌ ${data.error}</div>`;
        }

        if (data.bo === 'no') {
            html += `
                <div class="alert alert-warning">
                    ⚠️ Данные бухгалтерской отчетности не найдены
                </div>
            `;
        } else if (data.prepay) {
            if (data.prepay === 'yes') {
                html += `
                    <div class="alert alert-success">✅ Авансирование допускается</div>
                `;

                if (data.max_debt) {
                    html += `
                        <div class="info-row">
                            <span class="label">Сумма допустимого аванса</span>
                            <span class="value green bold">${data.max_debt} ₽</span>
                        </div>
                    `;
                }

                if (data.cred_day) {
                    const isWarning = data.cred_day_warning || parseInt(data.cred_day) > 365;
                    html += `
                        <div class="info-row">
                            <span class="label">Срок выполнения обязательств</span>
                            <span class="value ${isWarning ? 'gold' : ''} bold">${data.cred_day} дней</span>
                        </div>
                    `;

                    if (isWarning) {
                        html += `
                            <div class="alert alert-warning" style="margin-top: 8px;">
                                ⚠️ Слишком большой срок, высокие риски нарушения условий договора
                            </div>
                        `;
                    }
                }
            } else if (data.prepay === 'no') {
                html += `
                    <div class="alert alert-danger">❌ Авансирование не допускается</div>
                    <div style="color: #6b5f52; font-size: 14px; margin-top: 6px;">Отрицательная кредитоспособность</div>
                `;
            }

            if (data.equity && data.equity !== '0') {
                html += `
                    <div class="info-row" style="margin-top: 12px; border-top: 1px solid #e8e3dc; padding-top: 14px;">
                        <span class="label">Стоимость чистых активов</span>
                        <span class="value bold">${data.equity} ₽</span>
                    </div>
                    <div class="small-note">для оценки перспектив взыскания</div>
                `;
            }
        }

        if (data.output) {
            const escaped = data.output
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');

            html += `
                <div class="toggle-output" onclick="toggleRaw()">▼ Показать полный вывод скрипта</div>
                <div class="raw-output" id="rawOutput">${escaped}</div>
            `;
        }

        html += '</div>';

        resultDiv.innerHTML = html;
        resultDiv.classList.add('show');

        if (resultDiv.scrollIntoView) {
            resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    function toggleRaw() {
        const raw = document.getElementById('rawOutput');
        const btn = document.querySelector('.toggle-output');
        if (raw) {
            if (raw.classList.contains('show')) {
                raw.classList.remove('show');
                btn.textContent = '▼ Показать полный вывод скрипта';
            } else {
                raw.classList.add('show');
                btn.textContent = '▲ Скрыть полный вывод скрипта';
            }
        }
    }
</script>

</body>
</html>
'''

@app.route('/')
def index():
    return HTML_PAGE

@app.route('/check', methods=['POST'])
def check_company():
    inn = request.form.get('inn', '').strip()
    
    if not inn:
        return jsonify({'error': 'Пожалуйста, введите ИНН'})
    
    if len(inn) != 10 and len(inn) != 12:
        return jsonify({'error': 'ИНН должен содержать 10 или 12 цифр'})
    
    if not inn.isdigit():
        return jsonify({'error': 'ИНН должен содержать только цифры'})
    
    try:
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp:
            tmp_path = tmp.name
        
        process = subprocess.Popen(
            [sys.executable, 'brusnika_prepay.py'],
            stdin=subprocess.PIPE,
            stdout=open(tmp_path, 'w'),
            stderr=subprocess.PIPE,
            text=True
        )
        
        process.stdin.write(inn + '\n')
        process.stdin.close()
        process.wait(timeout=30)
        
        with open(tmp_path, 'r', encoding='utf-8') as f:
            output = f.read()
        
        os.unlink(tmp_path)
        
        if process.returncode != 0:
            return jsonify({'error': 'Ошибка при выполнении скрипта'})
        
        result = {
            'output': output,
            'lines': output.strip().split('\n')
        }
        
        parsed = parse_output(output)
        result.update(parsed)
        
        return jsonify(result)
        
    except subprocess.TimeoutExpired:
        process.kill()
        return jsonify({'error': 'Превышено время ожидания (30 секунд)'})
    except Exception as e:
        return jsonify({'error': f'Ошибка: {str(e)}'})

def parse_output(output):
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
            match = re.search(r'(\d[\d\s]+)₽', line)
            if match:
                result['max_debt'] = match.group(1).strip()
            else:
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
    
    return result

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Сервер запущен!")
    print("📱 Откройте в браузере: http://localhost:5000")
    print("🛑 Нажмите Ctrl+C для остановки")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)