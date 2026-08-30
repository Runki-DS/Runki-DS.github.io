# app.py
import streamlit as st
import gdown
import requests
import pandas as pd
import numpy as np

# Настройка страницы
st.set_page_config(
    page_title="Оценка кредитоспособности",
    layout="wide"
)

st.title("Оценка кредитоспособности контрагента")
st.markdown("---")

# Загружаем API ключ из secrets
api_key = st.secrets["FOCUS_API_KEY"]

# Инициализация сессии
if 'result' not in st.session_state:
    st.session_state.result = None

# Ввод ИНН
inn = st.text_input("Введите ИНН проверяемой компании:", max_chars=12)

# Кнопка для запуска анализа
if st.button("🔍 Проверить компанию", type="primary"):
    if not inn:
        st.error("Пожалуйста, введите ИНН")
    elif len(inn) != 10 and len(inn) != 12:
        st.error("ИНН юрлица должен содержать 10 цифр")
    else:
        with st.spinner("Загрузка данных..."):
            try:
                # Здесь ваш код анализа
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
                    )) * 1000 / 12 * 0.6
                ).astype(int)

                df.loc[0, 'max_debt_prev'] = (
                    ((df.loc[0, 'eV_1230_prev'] + df.loc[0, 'eV_2110_prev'] * K1 * K2) - (
                        (df.loc[0, 'eV_1520_prev'] - df.loc[0, 'eV_1520']) +
                        ((df.loc[0, 'eV_1210_prev'] + df.loc[0, 'eV_1220_prev']) -
                         (df.loc[0, 'eV_1210'] + df.loc[0, 'eV_1220'])) -
                        (df.loc[0, 'eV_2110_prev'] - df.loc[0, 'eV_2400_prev']) -
                        df.loc[0, 'eV_1250_prev'] +
                        df.loc[0, 'eV_1510_prev']
                    )) * 1000 / 12 * 0.6
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

# Отображение результатов
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

    # Форматируем
    formatted_max_debt = format(max_debt, ',').replace(',', ' ')
    formatted_equity = format(equity, ',').replace(',', ' ')

    # Стилизуем вывод
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 📊 {short_name}")
        st.markdown(f"**ИНН:** {inn}")
        st.markdown(f"**Возраст компании:** {age} лет")
    
    with col2:
        if prepay == 'yes':
            st.success("✅ Авансирование допускается")
        else:
            st.error("❌ Авансирование не допускается")

    if bo == 'no':
        st.warning("Данные бухгалтерской отчетности не найдены")
    else:
        st.markdown(f"**Кредитоспособность рассчитывалась на данных {year} года:**")
        
        if prepay == 'yes':
            st.metric(
                "Сумма допустимого аванса",
                f"{formatted_max_debt} ₽",
                delta=max_debt_shift,
                delta_color="normal"
            )
            
            if cred_day == 0:
                st.info("ℹ️ Срок выполнения обязательств определить не удалось.")
            elif cred_day > 365:
                st.warning(f"⚠️ Слишком большой срок выполнения обязательств ({cred_day} дней) - высокие риски нарушения условий договора {cred_day_shift}")
            else:
                st.success(f"✅ Ориентировочный срок выполнения обязательств {cred_day} дней {cred_day_shift}")

        if equity != 0:
            st.metric("Стоимость чистых активов", f"{formatted_equity} ₽", help="Для оценки перспектив взыскания")

    # Кнопка для нового поиска
    if st.button("🔄 Новый поиск"):
        st.session_state.result = None
        st.rerun()

# Добавляем информацию в сайдбар
with st.sidebar:
    st.markdown("### ℹ️ О сервисе")
    st.markdown("""
    Сервис анализирует кредитоспособность компании на основе данных бухгалтерской отчетности.
    
    **Что анализируется:**
    - Финансовая отчетность
    - Кредиторская задолженность
    - Сроки выполнения обязательств
    - Чистые активы
    
    **Источник данных:** Бухгалтерская отченость
    """)
    
    st.markdown("---")
    st.caption("Разработано для анализа контрагентов Брусники")