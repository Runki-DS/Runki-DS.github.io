# app.py
import streamlit as st
import gdown
import requests
import pandas as pd
import numpy as np

# ----------------------------------------------------------------------------
# 1. НАСТРОЙКА СТРАНИЦЫ И СТИЛЕЙ (ФИРМЕННЫЙ СТИЛЬ БРУСНИКИ)
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Анализ контрагентов | Брусника",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ФИРМЕННЫЕ ЦВЕТА БРУСНИКИ
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
    /* Стиль для предупреждений и информации */
    .stAlert {{
        border-radius: 8px;
        border-left: 4px solid {BRUSNIKA_GOLD};
    }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 2. ЗАГОЛОВОК (КАК НА САЙТЕ БРУСНИКИ)
# ----------------------------------------------------------------------------
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown("## 🌲")
with col_title:
    st.markdown("# Анализ контрагентов")
    st.markdown("*Оценка кредитоспособности по данным ФНС*")

st.markdown("---")

# ----------------------------------------------------------------------------
# 3. БОКОВАЯ ПАНЕЛЬ С ИНФОРМАЦИЕЙ
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"<div style='background-color:{BRUSNIKA_GREEN}; padding:1.5rem; border-radius:12px;'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{BRUSNIKA_LIGHT_TEXT};'>🌲 Брусника</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{BRUSNIKA_LIGHT_TEXT}; font-size:0.9rem;'>Сервис анализирует финансовую отчетность компаний через API Контур.Фокуса.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### ℹ️ Что анализируется")
    st.markdown("""
    - Финансовая отчетность  
    - Кредиторская задолженность  
    - Сроки выполнения обязательств  
    - Чистые активы  
    """)
    st.markdown("---")
    st.caption("Данные обновляются автоматически")
    st.caption("v1.0 | Для внутреннего использования")

# ----------------------------------------------------------------------------
# 4. ОСНОВНАЯ ЛОГИКА ПРИЛОЖЕНИЯ (ВАШ ПОЛНЫЙ СКРИПТ)
# ----------------------------------------------------------------------------

# Загружаем API ключ из secrets
api_key = st.secrets["FOCUS_API_KEY"]

# Инициализация сессии
if 'result' not in st.session_state:
    st.session_state.result = None

# Ввод ИНН
inn = st.text_input(
    "Введите ИНН проверяемой компании:",
    placeholder="Например: 6671010101",
    max_chars=12
)

# Кнопка для запуска анализа
if st.button("🔍 Проверить компанию", type="primary"):
    if not inn:
        st.error("Пожалуйста, введите ИНН")
    elif len(inn) != 10 and len(inn) != 12:
        st.error("ИНН должен содержать 10 или 12 цифр")
    else:
        with st.spinner("Загрузка данных..."):
            try:
                # ------------------------------------------------------------------
                # ВАШ ПОЛНЫЙ КОД АНАЛИЗА (ВЗЯТ ИЗ ВАШЕГО ФАЙЛА)
                # ------------------------------------------------------------------
                NDS = 22
                K1 = 1 + NDS/100
                K2 = 0.8

                # Параметры для API
                params = {
                    "key": api_key,
                    "inn": inn
                }

                # Создаем DataFrame
                columns = [
                    'inn', 'short_name', 'registrationDate', 'age', 'year', 'bo',
                    'eV_1210', 'sV_1210', 'eV_1220', 'sV_1220', 
                    'eV_1230', 'sV_1230', 'eV_1250', 'sV_1250',
                    'eV_1510', 'sV_1510', 'eV_1520', 'sV_1520',
                    'eV_1400', 'eV_1500', 'eV_1600',
                    'eV_2110', 'sV_2110', 'eV_2400', 'sV_2400',
                    'max_debt', 'max_debt_shift', 'cred_day', 'cred_day_shift',
                    'equity', 'prepay'
                ]
                df = pd.DataFrame(columns=columns)

                # Получаем данные по /api3/req
                req_url = "https://focus-api.kontur.ru/api3/req"
                req_response = requests.get(req_url, params={"key": api_key, "inn": inn})
                req_data = req_response.json()

                if req_response.status_code == 200 and req_data:
                    df.loc[0, 'inn'] = req_data[0]['inn']
                    df.loc[0, 'short_name'] = req_data[0]['UL']['legalName']['short']
                    df.loc[0, 'registrationDate'] = req_data[0]['UL']['registrationDate']
                    df.loc[0, 'age'] = pd.Timestamp.now().year - pd.to_datetime(req_data[0]['UL']['registrationDate']).year

                # Получаем данные по /api3/accountingReports
                buh_url = "https://focus-api.kontur.ru/api3/accountingReports"
                buh_response = requests.get(buh_url, params={"key": api_key, "inn": inn})
                buh_data = buh_response.json()

                if buh_response.status_code == 200 and buh_data and len(buh_data) > 0:
                    df.loc[0, 'bo'] = 'yes'
                    buh_forms = buh_data[0].get('buhForms', [])
                else:
                    df.loc[0, 'bo'] = 'no'
                    numeric_cols = ['eV_1210', 'sV_1210', 'eV_1220', 'sV_1220', 'eV_1230', 'sV_1230',
                                    'eV_1250', 'sV_1250', 'eV_1510', 'sV_1510', 'eV_1520', 'sV_1520',
                                    'eV_1400', 'eV_1500', 'eV_1600',
                                    'eV_2110', 'sV_2110', 'eV_2400', 'sV_2400']
                    df[numeric_cols] = 0
                    df[['max_debt', 'cred_day', 'prepay']] = 0
                    df[['max_debt_shift', 'cred_day_shift']] = '0%'
                    st.session_state.result = df
                    st.warning("Данные бухгалтерской отчетности не найдены")
                    st.stop()

                # Определяем последний и предпоследний годы
                if buh_forms:
                    years = sorted([f.get('year') for f in buh_forms if f.get('year')], reverse=True)
                    if len(years) >= 2:
                        last_year = years[0]
                        prev_year = years[1]
                    else:
                        last_year = years[0] if years else None
                        prev_year = None
                else:
                    last_year = None
                    prev_year = None

                df.loc[0, 'year'] = last_year

                # Функция для поиска значения
                def get_value(form_data, code, value_type='endValue'):
                    for item in form_data:
                        if item.get('code') == code:
                            return item.get(value_type, 0)
                    return 0

                # Загружаем данные последнего года
                if last_year:
                    latest_form = next((f for f in buh_forms if f.get('year') == last_year), None)
                    if latest_form:
                        form1 = latest_form.get('form1', [])
                        form2 = latest_form.get('form2', [])
                        df.loc[0, 'eV_1210'] = get_value(form1, 1210, 'endValue')
                        df.loc[0, 'sV_1210'] = get_value(form1, 1210, 'startValue')
                        df.loc[0, 'eV_1220'] = get_value(form1, 1220, 'endValue')
                        df.loc[0, 'sV_1220'] = get_value(form1, 1220, 'startValue')
                        df.loc[0, 'eV_1230'] = get_value(form1, 1230, 'endValue')
                        df.loc[0, 'sV_1230'] = get_value(form1, 1230, 'startValue')
                        df.loc[0, 'eV_1250'] = get_value(form1, 1250, 'endValue')
                        df.loc[0, 'sV_1250'] = get_value(form1, 1250, 'startValue')
                        df.loc[0, 'eV_1510'] = get_value(form1, 1510, 'endValue')
                        df.loc[0, 'sV_1510'] = get_value(form1, 1510, 'startValue')
                        df.loc[0, 'eV_1520'] = get_value(form1, 1520, 'endValue')
                        df.loc[0, 'sV_1520'] = get_value(form1, 1520, 'startValue')
                        df.loc[0, 'eV_1400'] = get_value(form1, 1400, 'endValue')
                        df.loc[0, 'eV_1500'] = get_value(form1, 1500, 'endValue')
                        df.loc[0, 'eV_1600'] = get_value(form1, 1600, 'endValue')
                        df.loc[0, 'eV_2110'] = get_value(form2, 2110, 'endValue')
                        df.loc[0, 'sV_2110'] = get_value(form2, 2110, 'startValue')
                        df.loc[0, 'eV_2400'] = get_value(form2, 2400, 'endValue')
                        df.loc[0, 'sV_2400'] = get_value(form2, 2400, 'startValue')

                # Загружаем данные предпоследнего года
                if prev_year:
                    prev_form = next((f for f in buh_forms if f.get('year') == prev_year), None)
                    if prev_form:
                        form1_prev = prev_form.get('form1', [])
                        form2_prev = prev_form.get('form2', [])
                        df.loc[0, 'eV_1210_prev'] = get_value(form1_prev, 1210, 'endValue')
                        df.loc[0, 'sV_1210_prev'] = get_value(form1_prev, 1210, 'startValue')
                        df.loc[0, 'eV_1220_prev'] = get_value(form1_prev, 1220, 'endValue')
                        df.loc[0, 'sV_1220_prev'] = get_value(form1_prev, 1220, 'startValue')
                        df.loc[0, 'eV_1230_prev'] = get_value(form1_prev, 1230, 'endValue')
                        df.loc[0, 'sV_1230_prev'] = get_value(form1_prev, 1230, 'startValue')
                        df.loc[0, 'eV_1250_prev'] = get_value(form1_prev, 1250, 'endValue')
                        df.loc[0, 'sV_1250_prev'] = get_value(form1_prev, 1250, 'startValue')
                        df.loc[0, 'eV_1510_prev'] = get_value(form1_prev, 1510, 'endValue')
                        df.loc[0, 'sV_1510_prev'] = get_value(form1_prev, 1510, 'startValue')
                        df.loc[0, 'eV_1520_prev'] = get_value(form1_prev, 1520, 'endValue')
                        df.loc[0, 'sV_1520_prev'] = get_value(form1_prev, 1520, 'startValue')
                        df.loc[0, 'eV_1400_prev'] = get_value(form1_prev, 1400, 'endValue')
                        df.loc[0, 'eV_1500_prev'] = get_value(form1_prev, 1500, 'endValue')
                        df.loc[0, 'eV_1600_prev'] = get_value(form1_prev, 1600, 'endValue')
                        df.loc[0, 'eV_2110_prev'] = get_value(form2_prev, 2110, 'endValue')
                        df.loc[0, 'sV_2110_prev'] = get_value(form2_prev, 2110, 'startValue')
                        df.loc[0, 'eV_2400_prev'] = get_value(form2_prev, 2400, 'endValue')
                        df.loc[0, 'sV_2400_prev'] = get_value(form2_prev, 2400, 'startValue')
                else:
                    for col in ['eV_1210_prev', 'sV_1210_prev', 'eV_1220_prev', 'sV_1220_prev',
                                'eV_1230_prev', 'sV_1230_prev', 'eV_1250_prev', 'sV_1250_prev',
                                'eV_1510_prev', 'sV_1510_prev', 'eV_1520_prev', 'sV_1520_prev',
                                'eV_1400_prev', 'eV_1500_prev', 'eV_1600_prev',
                                'eV_2110_prev', 'sV_2110_prev', 'eV_2400_prev', 'sV_2400_prev']:
                        df.loc[0, col] = 0

                df = df.fillna(0)

                # Рассчеты...
                df.loc[0, 'max_debt'] = (
                    ((df.loc[0, 'eV_1230'] + df.loc[0, 'eV_2110'] * K1 * K2) - (
                        (df.loc[0, 'eV_1520'] - df.loc[0, 'eV_1520_prev']) +
                        ((df.loc[0, 'eV_1210'] + df.loc[0, 'eV_1220']) -
                         (df.loc[0, 'eV_1210_prev'] + df.loc[0, 'eV_1220_prev'])) -
                        (df.loc[0, 'eV_2110'] - df.loc[0, 'eV_2400']) -
                        df.loc[0, 'eV_1250'] +
                        df.loc[0, 'eV_1510']
                    )) / 12 * 0.6
                ).astype(int)

                df.loc[0, 'max_debt_prev'] = (
                    ((df.loc[0, 'eV_1230_prev'] + df.loc[0, 'eV_2110_prev'] * K1 * K2) - (
                        (df.loc[0, 'eV_1520_prev'] - df.loc[0, 'eV_1520']) +
                        ((df.loc[0, 'eV_1210_prev'] + df.loc[0, 'eV_1220_prev']) -
                         (df.loc[0, 'eV_1210'] + df.loc[0, 'eV_1220'])) -
                        (df.loc[0, 'eV_2110_prev'] - df.loc[0, 'eV_2400_prev']) -
                        df.loc[0, 'eV_1250_prev'] +
                        df.loc[0, 'eV_1510_prev']
                    )) / 12 * 0.6
                ).astype(int)

                if df.loc[0, 'max_debt_prev'] != 0:
                    change = ((df.loc[0, 'max_debt'] - df.loc[0, 'max_debt_prev']) / abs(df.loc[0, 'max_debt_prev'])) * 100
                    df.loc[0, 'max_debt_shift'] = f"{'+' if change >= 0 else ''}{change:.1f}%"
                else:
                    df.loc[0, 'max_debt_shift'] = '0%'

                if df.loc[0, 'eV_2110'] > 0:
                    df.loc[0, 'cred_day'] = (
                        ((df.loc[0, 'eV_1520_prev'] + df.loc[0, 'eV_1520']) / 2) /
                        df.loc[0, 'eV_2110'] * 365
                    ).astype(int)
                else:
                    df.loc[0, 'cred_day'] = 0

                if df.loc[0, 'eV_2110_prev'] > 0:
                    df.loc[0, 'cred_day_prev'] = (
                        ((df.loc[0, 'eV_1520'] + df.loc[0, 'eV_1520_prev']) / 2) /
                        df.loc[0, 'eV_2110_prev'] * 365
                    ).astype(int)
                else:
                    df.loc[0, 'cred_day_prev'] = 0

                if df.loc[0, 'cred_day_prev'] != 0:
                    change = ((df.loc[0, 'cred_day'] - df.loc[0, 'cred_day_prev']) / abs(df.loc[0, 'cred_day_prev'])) * 100
                    df.loc[0, 'cred_day_shift'] = f"{'+' if change >= 0 else ''}{change:.1f}%"
                else:
                    df.loc[0, 'cred_day_shift'] = '0%'

                df.loc[0, 'equity'] = df.loc[0, 'eV_1600'] - (df.loc[0, 'eV_1400'] + df.loc[0, 'eV_1500'])
                df.loc[0, 'prepay'] = 'no' if df.loc[0, 'max_debt'] <= 0 else 'yes'

                cols_to_drop = [col for col in df.columns if col.endswith('_prev')]
                df = df.drop(columns=cols_to_drop, errors='ignore')

                st.session_state.result = df

            except Exception as e:
                st.error(f"Произошла ошибка: {str(e)}")

# ----------------------------------------------------------------------------
# 5. ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ В СТИЛЕ БРУСНИКИ
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

# ----------------------------------------------------------------------------
# 6. ПОДВАЛ (КАК НА САЙТЕ БРУСНИКИ)
# ----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='display:flex; justify-content:space-between; font-size:0.8rem; color:#888; padding:1rem 0;'>
    <span>🌲 Брусника • Анализ контрагентов</span>
    <span>Данные предоставлены Контур.Фокус</span>
</div>
""", unsafe_allow_html=True)
