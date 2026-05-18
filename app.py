import streamlit as st
import matplotlib.pyplot as plt

# Настройки веб-страницы
st.set_page_config(page_title="Abyss 99 Advanced Financial Model", layout="wide")

st.title("⚓ Расширенная бизнес-модель: «99 Ночей в Бездне»")
st.write("Профессиональный калькулятор доходности с автоматическим дублированием всех показателей в USD ($) и Robux (R$).")

# Фиксированные константы
ROBLOX_TAX = 0.30       # Комиссия платформы Roblox
INVESTMENT = 4500       # Стартовый капитал инвестора

# Боковая панель управления
st.sidebar.header("🎛️ Настройка переменных")
input_mode = st.sidebar.radio("Режим ввода данных:", ("Ползунки", "Ввод вручную"))

st.sidebar.markdown("---")

if input_mode == "Ползунки":
    ccu = st.sidebar.slider("Средний онлайн (CCU):", min_value=0, max_value=30000, value=1500, step=100)
    mau = st.sidebar.slider("Игроков в месяц (MAU):", min_value=10000, max_value=5000000, value=250000, step=10000)
    conv = st.sidebar.slider("Конверсия в донат (%):", min_value=0.0, max_value=10.0, value=2.0, step=0.1, format="%.1f") / 100.0
    arppu = st.sidebar.slider("Средний чек донатера (Robux):", min_value=10, max_value=2000, value=250, step=10)
    devex_rate = st.sidebar.slider("Курс DevEx ($ за 1 Robux):", min_value=0.0010, max_value=0.0100, value=0.0035, step=0.0001, format="%.4f")
    
    st.sidebar.markdown("### 📈 Экономика и Удержание")
    reinvest_rate = st.sidebar.slider("Фонд развития игры (% от прибыли):", min_value=0, max_value=50, value=15, step=5) / 100.0
    tax_rate = st.sidebar.slider("Налог на вывод денег / физлицо (%):", min_value=0, max_value=20, value=6, step=1) / 100.0
    share = st.sidebar.slider("Доля инвестора после ROI (%):", min_value=0, max_value=100, value=35, step=5) / 100.0
else:
    ccu = st.sidebar.number_input("Средний онлайн (CCU):", min_value=0, max_value=100000, value=1500, step=100)
    mau = st.sidebar.number_input("Игроков в месяц (MAU):", min_value=0, max_value=50000000, value=250000, step=10000)
    conv = st.sidebar.number_input("Конверсия в донат (%):", min_value=0.0, max_value=100.0, value=2.0, step=0.1, format="%.1f") / 100.0
    arppu = st.sidebar.number_input("Средний чек донатера (Robux):", min_value=0, max_value=100000, value=250, step=10)
    devex_rate = st.sidebar.number_input("Курс DevEx ($ за 1 Robux):", min_value=0.0010, max_value=0.0100, value=0.0035, step=0.0001, format="%.4f")
    
    st.sidebar.markdown("### 📈 Экономика и Удержание")
    reinvest_rate = st.sidebar.number_input("Фонд развития игры (% от прибыли):", min_value=0, max_value=100, value=15, step=5) / 100.0
    tax_rate = st.sidebar.number_input("Налог на вывод денег / физлицо (%):", min_value=0, max_value=100, value=6, step=1) / 100.0
    share = st.sidebar.number_input("Доля инвестора после ROI (%):", min_value=0, max_value=100, value=35, step=5) / 100.0

# --- РАСЧЕТЫ ЭКОНОМИКИ ---

# Функция перевода USD в Robux по выбранному курсу DevEx
def usd_to_robux(usd, rate):
    return usd / rate if rate > 0 else 0

# 1. Грязный доход (Донаты + Premium Payouts)
paying_users = mau * conv
gross_robux_donates = paying_users * arppu
net_usd_donates = (gross_robux_donates * (1 - ROBLOX_TAX)) * devex_rate

# Базовый Premium Payouts в USD, затем переводим в Robux эквивалент
premium_bonus_usd = ccu * 1.0
total_gross_usd = net_usd_donates + premium_bonus_usd
total_gross_robux = usd_to_robux(total_gross_usd, devex_rate)

# 2. Удержание налогов и фонда развития
tax_usd = total_gross_usd * tax_rate
tax_robux = usd_to_robux(tax_usd, devex_rate)

reinvestment_usd = total_gross_usd * reinvest_rate
reinvestment_robux = usd_to_robux(reinvestment_usd, devex_rate)

total_clear_profit_usd = total_gross_usd - tax_usd - reinvestment_usd
total_clear_profit_robux = usd_to_robux(total_clear_profit_usd, devex_rate)

# 3. Выплаты инвестору
investor_payout_usd = total_clear_profit_usd * share
investor_payout_robux = usd_to_robux(investor_payout_usd, devex_rate)

# 4. Расчет продуктовых метрик плейса
arpu_usd = total_gross_usd / mau if