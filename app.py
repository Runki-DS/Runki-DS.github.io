# app.py
import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# ----------------------------------------------------------------------------
# 1. НАСТРОЙКА СТРАНИЦЫ И СТИЛЕЙ (ФИРМЕННЫЙ СТИЛЬ БРУСНИКИ)
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Оценка кредитоспособности | Брусника",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ФИРМЕННЫЕ ЦВЕТА БРУСНИКИ (взят из макета сайта)
BRUSNIKA_GREEN = "#1A3A32"      # Темно-зеленый (акценты, заголовки)
BRUSNIKA_BEIGE = "#F5F0E6"     # Бежевый (фон)
BRUSNIKA_GOLD = "#C5A775"      # Золотистый (акценты)
BRUSNIKA_DARK = "#2C2C2C"      # Почти черный для текста
BRUSNIKA_LIGHT_TEXT = "#FFFFFF" # Белый текст на темном фоне

# ПОДКЛЮЧАЕМ СВОЙ СТИЛЬ CSS
st.markdown(f"""
<style>
    /* Общий фон страницы */
    .stApp {{
        background-color: {BRUSNIKA_BEIGE};
        font-family: 'Helvetica Neue', 'Arial', sans-serif;
    }}
    /* Главный заголовок */
    h1, h2, h3 {{
        color: {BRUSNIKA_GREEN};
        font-weight: 300;
        letter-spacing: 0.02em;
    }}
    /* Стиль карточек */
    .brusnika-card {{
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border-left: 6px solid {BRUSNIKA_GOLD};
        margin: 1.5rem 0;
    }}
    /* Метрики как на сайте Брусники */
    .brusnika-metric {{
        background-color: {BRUSNIKA_GREEN};
        color: {BRUSNIKA_LIGHT_TEXT};
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    .brusnika-metric h3 {{
        color: {BRUSNIKA_LIGHT_TEXT};
        font-weight: 300;
        margin-bottom: 0.5rem;
    }}
    .brusnika-metric .value {{
        font-size: 2.2rem;
        font-weight: 500;
        color: {BRUSNIKA_GOLD};
    }}
    /* Кнопка в стиле Брусники */
    .stButton > button {{
        background-color: {BRUSNIKA_GREEN};
        color: white;
        border: none;
        border-radius: 40px;
        padding: 0.6rem 2.5rem;
        font-weight: 400;
        letter-spacing: 0.03em;
        transition: all 0.2s;
        text-transform: uppercase;
        font-size: 0.9rem;
    }}
    .stButton > button:hover {{
        background-color: #2A5A4A;
        box-shadow: 0 4px 12px rgba(26, 58, 50, 0.3);
        transform: translateY(-2px);
    }}
    /* Поля ввода */
    .stTextInput > div > div > input {{
        border-radius: 40px !important;
        border: 1px solid #ddd !important;
        padding: 0.6rem 1.2rem !important;
        font-size: 1rem !important;
        background-color: white !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {BRUSNIKA_GOLD} !important;
        box-shadow: 0 0 0 2px rgba(197, 167, 117, 0.2) !important;
    }}
    /* Сайдбар скрыт, но оставляем логотип */
    .css-1d391kg {{
        background-color: {BRUSNIKA_GREEN};
    }}
    /* Разделительная линия */
    hr {{
        border: none;
        border-top: 2px solid {BRUSNIKA_GOLD};
        opacity: 0.3;
        margin: 2rem 0;
    }}
    /* Текст */
    p, li, .stMarkdown {{
        color: {BRUSNIKA_DARK};
    }}
    /* Метки статуса */
    .status-badge {{
        display: inline-block;
        padding: 0.2rem 1.2rem;
        border-radius: 40px;
        font-weight: 500;
        font-size: 0.9rem;
        letter-spacing: 0.02em;
    }}
    .status-yes {{
        background-color: {BRUSNIKA_GREEN};
        color: white;
    }}
    .status-no {{
        background-color: #D32F2F;
        color: white;
    }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 2. ЗАГОЛОВОК И ВВОДНАЯ ЧАСТЬ (КАК НА САЙТЕ БРУСНИКИ)
# ----------------------------------------------------------------------------
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown("## 🌲")
with col_title:
    st.markdown("# Брусника. Оценка кредитоспособности")
    st.markdown("*Оценка по данным бухгалтерской отчетности*")

st.markdown("---")

# ----------------------------------------------------------------------------
# 3. БОКОВАЯ ПАНЕЛЬ С ИНФОРМАЦИЕЙ (СТИЛИЗОВАНА)
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"<div style='background-color:{BRUSNIKA_GREEN}; padding:1.5rem; border-radius:12px;'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{BRUSNIKA_LIGHT_TEXT};'>🌲 Брусника</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{BRUSNIKA_LIGHT_TEXT}; font-size:0.9rem;'>Сервис анализирует финансовую отчетность компаний.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Данные обновляются автоматически")
    st.caption("v1.0 | Для внутреннего использования ГК Брусника")

# ----------------------------------------------------------------------------
# 4. ОСНОВНАЯ ЛОГИКА ПРИЛОЖЕНИЯ (ВАШ СКРИПТ)
# ----------------------------------------------------------------------------

# Инициализация состояния
if 'result' not in st.session_state:
    st.session_state.result = None
if 'error' not in st.session_state:
    st.session_state.error = None

# Ввод ИНН
inn_input = st.text_input(
    "Введите ИНН компании",
    placeholder="Например: 6671010101",
    max_chars=12,
    key="inn_input"
)

# Кнопка запуска
col_btn, _ = st.columns([1, 5])
with col_btn:
    analyze_clicked = st.button("Проверить", type="primary", use_container_width=True)

# ----------------------------------------------------------------------------
# 5. ВЫПОЛНЕНИЕ АНАЛИЗА (ПОЛНОСТЬЮ ВАША ЛОГИКА)
# ----------------------------------------------------------------------------
if analyze_clicked:
    if not inn_input:
        st.error("Пожалуйста, введите ИНН")
    elif len(inn_input) not in [10, 12]:
        st.error("ИНН юрлица должен содержать 10 цифр")
    else:
        with st.spinner("Загрузка данных..."):
            try:
                # ЗДЕСЬ ВЕСЬ ВАШ КОД РАСЧЕТОВ (ТОТ ЖЕ, ЧТО В ИСХОДНОМ СКРИПТЕ)
                # Он полностью идентичен вашему коду, я его сократил для наглядности,
                # но вы вставляете свой ПОЛНЫЙ код расчета.

                # ------------------------------------------------------------------
                # ВАШ КОД (полностью из вашего файла, начиная с NDS = 22)
                # ------------------------------------------------------------------
                NDS = 22
                K1 = 1 + NDS/100
                K2 = 0.8
                
                # Загрузка ключа из секретов (как вы и настроили)
                api_key = st.secrets["FOCUS_API_KEY"]
                
                # Ваша логика: парсинг, расчеты, создание df
                # ...
                # (Весь ваш код расчета должен быть здесь)
                # ...
                # В итоге должен получиться DataFrame df
                # ------------------------------------------------------------------
                
                # ПРИМЕР ДЛЯ ДЕМОНСТРАЦИИ (ЗАМЕНИТЕ НА ВАШ КОД):
                # Создаем тестовый df, чтобы показать результат.
                # ВАЖНО: УДАЛИТЕ ЭТУ ЗАГЛУШКУ И ВСТАВЬТЕ СВОЙ КОД!
                data = {
                    'inn': [inn_input],
                    'short_name': ['ООО "Тестовая компания"'],
                    'age': [8],
                    'bo': ['yes'],
                    'year': [2025],
                    'prepay': ['yes'],
                    'max_debt': [1250000],
                    'max_debt_shift': ['+12.5%'],
                    'cred_day': [45],
                    'cred_day_shift': ['-8.2%'],
                    'equity': [5400000]
                }
                df = pd.DataFrame(data)
                # ------------------------------------------------------------------
                
                # Сохраняем результат в сессию
                st.session_state.result = df
                st.session_state.error = None

            except Exception as e:
                st.session_state.error = str(e)
                st.session_state.result = None

# ----------------------------------------------------------------------------
# 6. ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ В СТИЛЕ БРУСНИКИ
# ----------------------------------------------------------------------------
if st.session_state.result is not None:
    df = st.session_state.result
    # Извлекаем данные
    short_name = df.loc[0, 'short_name']
    inn = df.loc[0, 'inn']
    age = df.loc[0, 'age']
    bo = df.loc[0, 'bo']
    year = df.loc[0, 'year']
    prepay = df.loc[0, 'prepay']
    max_debt = df.loc[0, 'max_debt']
    max_debt_shift = df.loc[0, 'max_debt_shift']
    cred_day = df.loc[0, 'cred_day']
    cred_day_shift = df.loc[0, 'cred_day_shift']
    equity = df.loc[0, 'equity']

    # Форматируем суммы
    formatted_max_debt = format(max_debt, ',').replace(',', ' ')
    formatted_equity = format(equity, ',').replace(',', ' ')

    # ------------------------------------------------------------------------
    # КАРТОЧКА РЕЗУЛЬТАТА (В ФИРМЕННОМ СТИЛЕ)
    # ------------------------------------------------------------------------
    st.markdown(f"""
    <div class="brusnika-card">
        <h2 style='margin-top:0;'>{short_name}</h2>
        <p style='font-size:1.1rem; color:{BRUSNIKA_GREEN};'>
            <strong>ИНН:</strong> {inn} &nbsp;|&nbsp; 
            <strong>Возраст:</strong> {age} лет
        </p>
    </div>
    """, unsafe_allow_html=True)

    if bo == 'no':
        st.warning("Данные бухгалтерской отчетности не найдены")
    else:
        st.markdown(f"<p style='text-align:right; font-size:0.9rem; color:#777;'>*Расчет на основе данных {year} года</p>", unsafe_allow_html=True)

        # Метрики в 3 колонки
        col1, col2, col3 = st.columns(3)

        with col1:
            prepay_status = "✅ Допускается" if prepay == 'yes' else "❌ Не допускается"
            badge_class = "status-yes" if prepay == 'yes' else "status-no"
            st.markdown(f"""
            <div style='text-align:center; padding:0.5rem;'>
                <p style='margin-bottom:0.3rem; font-size:0.9rem; color:#555;'>Авансирование</p>
                <span class="status-badge {badge_class}">{prepay_status}</span>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if prepay == 'yes':
                st.markdown(f"""
                <div class="brusnika-metric">
                    <h3>Максимальный аванс</h3>
                    <div class="value">{formatted_max_debt} ₽</div>
                    <p style='margin-top:0.5rem; font-size:0.9rem; color: #ddd;'>{max_debt_shift}</p>
                </div>
                """, unsafe_allow_html=True)

        with col3:
            if prepay == 'yes' and cred_day > 0:
                st.markdown(f"""
                <div class="brusnika-metric">
                    <h3>Срок обязательств</h3>
                    <div class="value">{cred_day} дн.</div>
                    <p style='margin-top:0.5rem; font-size:0.9rem; color: #ddd;'>{cred_day_shift}</p>
                </div>
                """, unsafe_allow_html=True)

        # Дополнительные комментарии
        if prepay == 'yes':
            if cred_day == 0:
                st.info("ℹ️ Срок выполнения обязательств определить не удалось.")
            elif cred_day > 365:
                st.warning(f"⚠️ Высокие риски: срок выполнения обязательств ({cred_day} дней) превышает 1 год.")
            else:
                st.success(f"✅ Ориентировочный срок выполнения обязательств — {cred_day} дней.")

        # Чистые активы
        if equity != 0:
            st.markdown(f"""
            <div style='background-color:white; padding:1.2rem; border-radius:8px; border-left:4px solid {BRUSNIKA_GOLD}; margin-top:1rem;'>
                <p style='margin:0;'><strong>Стоимость чистых активов:</strong> {formatted_equity} ₽</p>
                <p style='margin:0; font-size:0.85rem; color:#777;'>*Для оценки перспектив взыскания</p>
            </div>
            """, unsafe_allow_html=True)

    # Кнопка для нового запроса
    if st.button("🔄 Новый запрос", type="secondary"):
        st.session_state.result = None
        st.rerun()

# Отображение ошибок
if st.session_state.error:
    st.error(f"Произошла ошибка: {st.session_state.error}")

# ----------------------------------------------------------------------------
# 7. ПОДВАЛ (КАК НА САЙТЕ БРУСНИКИ)
# ----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='display:flex; justify-content:space-between; font-size:0.8rem; color:#888; padding:1rem 0;'>
    <span>🌲 Брусника • Анализ контрагентов</span>
    <span>Данные предоставлены для ГК Брусника</span>
</div>
""", unsafe_allow_html=True)
