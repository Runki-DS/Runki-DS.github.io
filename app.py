# app.py
import streamlit as st
import requests
import pandas as pd
import numpy as np

# ----------------------------------------------------------------------------
# 1. НАСТРОЙКА СТРАНИЦЫ
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Брусника — проверка контрагента",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ЦВЕТА
BG_COLOR = "#f8f7f4"
WHITE = "#ffffff"
DARK = "#1e1e1e"
GRAY = "#6b6b6b"
LIGHT_GRAY = "#f0eeea"
BORDER_COLOR = "rgba(0, 0, 0, 0.05)"
GOLD = "#b89b7b"
GREEN = "#1d6b2e"
RED = "#b33a3a"
ORANGE = "#b8681a"

# CSS
st.markdown(f"""
<style>
    /* Общий фон */
    .stApp {{
        background-color: {BG_COLOR};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}
    /* Убираем отступы у контейнера */
    .main > div {{
        padding: 0;
        max-width: 820px;
        margin: 0 auto;
    }}
    /* Скрываем стандартные Streamlit элементы */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display: none;}}
    header {{visibility: hidden;}}
    
    /* Шапка */
    .header {{
        background: {WHITE};
        padding: 20px 24px 12px;
        border-bottom: 1px solid {BORDER_COLOR};
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }}
    .logo {{
        display: flex;
        align-items: center;
        gap: 10px;
        text-decoration: none;
        color: {DARK};
    }}
    .logo-icon {{
        width: 36px;
        height: 36px;
        background: {DARK};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: {WHITE};
        font-weight: 700;
        font-size: 18px;
    }}
    .logo-text {{
        font-weight: 600;
        font-size: 22px;
        letter-spacing: -0.3px;
    }}
    .logo-text span {{
        font-weight: 300;
        color: {GRAY};
    }}
    .header-tag {{
        font-size: 14px;
        color: {GRAY};
        background: {LIGHT_GRAY};
        padding: 6px 16px;
        border-radius: 40px;
    }}
    /* Hero */
    .hero {{
        padding: 48px 24px 32px;
    }}
    .hero h1 {{
        font-size: 36px;
        font-weight: 400;
        letter-spacing: -0.4px;
        margin-bottom: 8px;
        line-height: 1.2;
        color: {DARK};
    }}
    .hero h1 strong {{
        font-weight: 600;
    }}
    .hero .sub {{
        font-size: 18px;
        color: #4a4a4a;
        margin-bottom: 32px;
    }}
    /* Карточка поиска */
    .search-card {{
        background: {WHITE};
        border-radius: 24px;
        padding: 36px 40px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.04);
        border: 1px solid {BORDER_COLOR};
        margin-bottom: 32px;
    }}
    .search-card label {{
        display: block;
        font-weight: 500;
        font-size: 15px;
        margin-bottom: 10px;
        color: {DARK};
    }}
    .search-row {{
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        align-items: center;
    }}
    /* Стили для Streamlit виджетов внутри карточки */
    .search-row .stTextInput {{
        flex: 1;
        min-width: 200px;
        padding: 0 !important;
    }}
    .search-row .stTextInput > div {{
        padding: 0 !important;
    }}
    .search-row .stTextInput > div > div > input {{
        padding: 14px 20px !important;
        border: 1px solid #dcdcdc !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        background: #fcfcfc !important;
        font-family: inherit !important;
        height: auto !important;
        min-height: 52px;
    }}
    .search-row .stTextInput > div > div > input:focus {{
        border-color: {GOLD} !important;
        box-shadow: 0 0 0 3px rgba(184, 155, 123, 0.15) !important;
        background: {WHITE} !important;
    }}
    .search-row .stTextInput > div > div > input::placeholder {{
        color: #aaa;
    }}
    .search-row .stButton {{
        margin: 0;
        padding: 0 !important;
    }}
    .search-row .stButton > button {{
        padding: 14px 40px !important;
        background: {DARK} !important;
        color: {WHITE} !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        font-size: 16px !important;
        cursor: pointer !important;
        transition: background 0.2s, transform 0.1s !important;
        font-family: inherit !important;
        white-space: nowrap !important;
        height: auto !important;
        min-height: 52px !important;
        width: auto !important;
        margin: 0 !important;
    }}
    .search-row .stButton > button:hover {{
        background: #333 !important;
    }}
    .search-row .stButton > button:active {{
        transform: scale(0.97) !important;
    }}
    .search-row .stButton > button:disabled {{
        opacity: 0.8;
        pointer-events: none;
    }}
    /* Результаты */
    .results-card {{
        background: {WHITE};
        border-radius: 24px;
        padding: 36px 40px;
        border: 1px solid {BORDER_COLOR};
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.04);
        margin-top: 8px;
        animation: fadeIn 0.3s ease;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .results-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        flex-wrap: wrap;
        gap: 16px;
        padding-bottom: 20px;
        border-bottom: 1px solid {LIGHT_GRAY};
        margin-bottom: 20px;
    }}
    .company-name {{
        font-size: 26px;
        font-weight: 500;
        letter-spacing: -0.2px;
        color: {DARK};
    }}
    .company-inn {{
        font-size: 17px;
        color: {GRAY};
        font-weight: 400;
        margin-top: 2px;
    }}
    .company-age {{
        background: {LIGHT_GRAY};
        padding: 6px 18px;
        border-radius: 40px;
        font-size: 14px;
        font-weight: 500;
        color: {DARK};
        white-space: nowrap;
    }}
    .result-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 28px 40px;
        margin-top: 6px;
    }}
    .result-item {{
        border-bottom: 1px solid {LIGHT_GRAY};
        padding-bottom: 14px;
    }}
    .result-item .label {{
        font-size: 13px;
        font-weight: 400;
        color: {GRAY};
        text-transform: uppercase;
        letter-spacing: 0.3px;
        margin-bottom: 4px;
    }}
    .result-item .value {{
        font-size: 19px;
        font-weight: 500;
        color: {DARK};
        word-break: break-word;
    }}
    .result-item .value small {{
        font-size: 14px;
        font-weight: 400;
        color: {GRAY};
        margin-left: 6px;
    }}
    .status-badge {{
        display: inline-block;
        padding: 4px 16px;
        border-radius: 40px;
        font-size: 14px;
        font-weight: 500;
        background: #e6f0e6;
        color: {GREEN};
    }}
    .status-badge.warning {{
        background: #fff1e0;
        color: {ORANGE};
    }}
    .status-badge.danger {{
        background: #fce8e8;
        color: {RED};
    }}
    .status-badge.neutral {{
        background: {LIGHT_GRAY};
        color: #4a4a4a;
    }}
    .no-data {{
        padding: 16px 0 8px;
        font-size: 17px;
        color: {GRAY};
        text-align: center;
    }}
    .equity-note {{
        margin-top: 18px;
        padding-top: 18px;
        border-top: 1px solid {LIGHT_GRAY};
        font-size: 15px;
        color: #4a4a4a;
    }}
    .equity-note strong {{
        color: {DARK};
    }}
    /* Футер */
    .footer {{
        margin-top: auto;
        padding: 24px 24px 20px;
        border-top: 1px solid {BORDER_COLOR};
        background: {WHITE};
        text-align: center;
        font-size: 14px;
        color: {GRAY};
    }}
    .footer a {{
        color: {DARK};
        text-decoration: none;
        border-bottom: 1px solid transparent;
        transition: border-color 0.2s;
        margin: 0 12px;
    }}
    .footer a:hover {{
        border-bottom-color: {GOLD};
    }}
    /* Стили для сообщений */
    .stAlert {{
        border-radius: 12px !important;
        border-left: 4px solid {GOLD} !important;
        margin-bottom: 20px !important;
    }}
    .stAlert > div {{
        padding: 12px 18px !important;
    }}
    /* Спиннер */
    .stSpinner {{
        text-align: center;
        padding: 20px 0;
    }}
    /* Адаптив */
    @media (max-width: 640px) {{
        .search-card {{
            padding: 24px 20px;
        }}
        .search-row {{
            flex-direction: column;
            align-items: stretch;
        }}
        .search-row .stButton > button {{
            width: 100% !important;
            justify-content: center !important;
        }}
        .results-card {{
            padding: 24px 20px;
        }}
        .result-grid {{
            grid-template-columns: 1fr;
            gap: 20px;
        }}
        .results-header {{
            flex-direction: column;
            align-items: flex-start;
        }}
        .company-name {{
            font-size: 22px;
        }}
        .hero h1 {{
            font-size: 28px;
        }}
        .hero .sub {{
            font-size: 16px;
        }}
    }}
    @media (max-width: 420px) {{
        .hero {{
            padding: 28px 16px 20px;
        }}
        .hero h1 {{
            font-size: 24px;
        }}
        .header-tag {{
            font-size: 12px;
            padding: 4px 12px;
        }}
        .logo-text {{
            font-size: 18px;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 2. ШАПКА
# ----------------------------------------------------------------------------
st.markdown("""
<div class="header">
    <div class="logo">
        <div class="logo-icon">Б</div>
        <div class="logo-text">Брусника <span>· проверка</span></div>
    </div>
    <span class="header-tag">Оценка контрагента</span>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 3. ОСНОВНОЙ БЛОК
# ----------------------------------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>Проверка <strong>контрагента</strong></h1>
    <p class="sub">Кредитоспособность и риск авансирования по данным ФНС</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 4. КАРТОЧКА ПОИСКА (поле ввода и кнопка внутри белой карточки)
# ----------------------------------------------------------------------------
st.markdown('<div class="search-card">', unsafe_allow_html=True)

with st.form(key="search_form"):
    st.markdown('<label>ИНН компании</label>', unsafe_allow_html=True)
    
    col_input, col_button = st.columns([3, 1])
    with col_input:
        inn = st.text_input(
            "",
            placeholder="Введите 10 или 12 цифр",
            max_chars=12,
            label_visibility="collapsed",
            key="inn_input"
        )
    with col_button:
        check_btn = st.form_submit_button(
            "Проверить",
            use_container_width=True,
            type="primary"
        )

st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 5. ЛОГИКА ПРИЛОЖЕНИЯ
# ----------------------------------------------------------------------------
api_key = st.secrets.get("FOCUS_API_KEY", "")

if 'result' not in st.session_state:
    st.session_state.result = None
if 'error' not in st.session_state:
    st.session_state.error = None
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

def check_counterparty(inn):
    """Основная функция проверки контрагента"""
    if not inn:
        st.session_state.error = "⚠️ Введите ИНН"
        st.session_state.result = None
        return
    
    if len(inn) != 10 and len(inn) != 12:
        st.session_state.error = "⚠️ ИНН должен содержать 10 или 12 цифр"
        st.session_state.result = None
        return
    
    if not api_key:
        st.session_state.error = "⚠️ API ключ не настроен. Добавьте FOCUS_API_KEY в secrets."
        st.session_state.result = None
        return
    
    st.session_state.is_loading = True
    
    try:
        NDS = 22
        K1 = 1 + NDS/100
        K2 = 0.8

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
        req_response = requests.get(req_url, params={"key": api_key, "inn": inn}, timeout=30)
        
        if req_response.status_code != 200:
            st.session_state.error = f"❌ Ошибка API: {req_response.status_code}"
            st.session_state.result = None
            st.session_state.is_loading = False
            return
            
        req_data = req_response.json()

        if req_response.status_code == 200 and req_data:
            df.loc[0, 'inn'] = req_data[0]['inn']
            df.loc[0, 'short_name'] = req_data[0]['UL']['legalName']['short']
            df.loc[0, 'registrationDate'] = req_data[0]['UL']['registrationDate']
            df.loc[0, 'age'] = pd.Timestamp.now().year - pd.to_datetime(req_data[0]['UL']['registrationDate']).year
        else:
            st.session_state.error = "❌ Компания не найдена по указанному ИНН"
            st.session_state.result = None
            st.session_state.is_loading = False
            return

        # Получаем данные по /api3/accountingReports
        buh_url = "https://focus-api.kontur.ru/api3/accountingReports"
        buh_response = requests.get(buh_url, params={"key": api_key, "inn": inn}, timeout=30)
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
            st.session_state.error = None
            st.session_state.is_loading = False
            return

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

        # Рассчеты
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
        st.session_state.error = None
        
    except requests.exceptions.Timeout:
        st.session_state.error = "❌ Превышено время ожидания ответа от API"
        st.session_state.result = None
    except requests.exceptions.RequestException as e:
        st.session_state.error = f"❌ Ошибка сети: {str(e)}"
        st.session_state.result = None
    except Exception as e:
        st.session_state.error = f"❌ Произошла ошибка: {str(e)}"
        st.session_state.result = None
    finally:
        st.session_state.is_loading = False

# Выполняем проверку при нажатии кнопки
if check_btn:
    check_counterparty(inn)

# Отображаем ошибку, если есть
if st.session_state.error:
    st.error(st.session_state.error)

# Отображаем спиннер при загрузке
if st.session_state.is_loading:
    with st.spinner("⏳ Отправка запроса..."):
        st.empty()

# ----------------------------------------------------------------------------
# 6. ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ
# ----------------------------------------------------------------------------
if st.session_state.result is not None:
    df = st.session_state.result
    data = df.loc[0]

    def fmt(num):
        if num is None or num == '' or num != num:
            return '0'
        return format(int(num), ',').replace(',', ' ')

    short_name = data.get('short_name', 'Название не найдено')
    inn_val = data.get('inn', inn)
    age = data.get('age', 0)
    bo = data.get('bo', 'no')
    year = data.get('year', '—')
    prepay = data.get('prepay', 'no')
    max_debt = data.get('max_debt', 0)
    max_debt_shift = data.get('max_debt_shift', '0%')
    cred_day = data.get('cred_day', 0)
    cred_day_shift = data.get('cred_day_shift', '0%')
    equity = data.get('equity', 0)

    # Формируем prepay статус
    if prepay == 'yes':
        prepay_status = 'Авансирование допускается'
        prepay_class = ''
    elif prepay == 'no' and max_debt <= 0:
        prepay_status = 'Авансирование не допускается, отрицательная кредитоспособность'
        prepay_class = 'danger'
    else:
        prepay_status = 'Авансирование не допускается'
        prepay_class = 'warning'

    # bo статус
    bo_status = '✅ Данные найдены' if bo == 'yes' else '❌ Данные бухгалтерской отчетности не найдены'
    bo_class = '' if bo == 'yes' else 'warning'

    # cred_day текст
    if cred_day == 0:
        cred_day_text = 'Срок выполнения обязательств определить не удалось.'
    elif cred_day > 365:
        cred_day_text = 'Слишком большой срок выполнения обязательств, высокие риски нарушения условий договора'
    else:
        cred_day_text = f'Ориентировочный срок выполнения обязательств {cred_day} дней'

    # max_debt_shift текст
    if max_debt_shift and max_debt_shift != '0%':
        is_negative = max_debt_shift.startswith('-')
        direction = 'ухудшение' if is_negative else 'улучшение'
        max_debt_shift_text = f'(изменение {max_debt_shift} {direction})'
    else:
        max_debt_shift_text = f'(изменение {max_debt_shift})'

    # cred_day_shift текст
    if cred_day_shift and cred_day_shift != '0%':
        is_positive = cred_day_shift.startswith('+')
        direction = 'ухудшение' if is_positive else 'улучшение'
        cred_day_shift_text = f'(изменение {cred_day_shift} — {direction})'
    else:
        cred_day_shift_text = f'(изменение {cred_day_shift})'

    # Рендер результатов
    st.markdown(f"""
    <div class="results-card">
        <div class="results-header">
            <div>
                <div class="company-name">{short_name}</div>
                <div class="company-inn">ИНН {inn_val}</div>
            </div>
            <div class="company-age">Возраст компании {age} лет</div>
        </div>
        <div style="margin-bottom: 18px;">
            <span class="status-badge {bo_class}">{bo_status}</span>
        </div>
    """, unsafe_allow_html=True)

    if bo == 'no':
        st.markdown('<div class="no-data">Данные бухгалтерской отчетности не найдены</div>', unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="margin-bottom: 14px; font-weight: 500; color: #1e1e1e;">
            Кредитоспособность рассчитывалась на данных {year} года:
        </div>
        <div class="result-grid">
            <div class="result-item">
                <div class="label">Авансирование</div>
                <div class="value">
                    <span class="status-badge {prepay_class}">{prepay_status}</span>
                </div>
            </div>
            <div class="result-item">
                <div class="label">Сумма допустимого аванса</div>
                <div class="value">{fmt(max_debt)} ₽ <small>{max_debt_shift_text}</small></div>
            </div>
            <div class="result-item">
                <div class="label">Срок выполнения обязательств</div>
                <div class="value" style="font-size: 16px;">{cred_day_text} <small>{cred_day_shift_text}</small></div>
            </div>
        """, unsafe_allow_html=True)

        if equity != 0:
            st.markdown(f"""
            <div class="result-item">
                <div class="label">Стоимость чистых активов</div>
                <div class="value">{fmt(equity)} ₽ <small>(для оценки перспектив взыскания)</small></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    if bo == 'no' and equity != 0:
        st.markdown(f"""
        <div class="equity-note">
            <strong>Чистые активы:</strong> {fmt(equity)} ₽ (для оценки перспектив взыскания)
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 7. ПОДВАЛ
# ----------------------------------------------------------------------------
st.markdown("""
<div class="footer">
    © 2026 Брусника
    <a href="#">Политика конфиденциальности</a>
    <a href="#">Пользовательское соглашение</a>
</div>
""", unsafe_allow_html=True)
