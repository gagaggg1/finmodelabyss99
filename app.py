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
arpu_usd = total_gross_usd / mau if mau > 0 else 0
arpu_robux = total_gross_robux / mau if mau > 0 else 0

ltv_usd = arpu_usd * 1.5  # Среднее время жизни игрока (1.5 месяца)
ltv_robux = arpu_robux * 1.5

# Срок окупаемости (ROI)
payout_step = investor_payout_usd if share > 0 else total_clear_profit_usd
roi_months = INVESTMENT / payout_step if payout_step > 0 else 99

# --- ИНТЕРФЕЙС И ВЫВОД ДАННЫХ ---

st.subheader("💰 Финансовые итоги проекта (в месяц)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Общий оборот проекта", f"${total_gross_usd:,.2f}", f"R$ {int(total_gross_robux):,}")
col2.metric("Фонд обновлений (контент)", f"${reinvestment_usd:,.2f}", f"R$ {int(reinvestment_robux):,}")
col3.metric("Чистая прибыль студии", f"${total_clear_profit_usd:,.2f}", f"R$ {int(total_clear_profit_robux):,}")
col4.metric("Чистый доход инвестора", f"${investor_payout_usd:,.2f}", f"R$ {int(investor_payout_robux):,}")

st.markdown("---")

st.subheader("📊 Важнейшие продуктовые метрики плейса")
m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("Доход со всех зашедших (ARPU)", f"${arpu_usd:.4f}", f"R$ {arpu_robux:.2f}", help="Сколько приносит один абсолютно любой игрок в месяц (включая неплатящих)")
m_col2.metric("Ценность игрока (LTV)", f"${ltv_usd:.4f}", f"R$ {ltv_robux:.2f}", help="Сколько игрок приносит за всё время активности в игре")

if roi_months <= 1:
    m_col3.metric("Окупаемость $4,500", "1-й месяц!", delta="⚡ Сверхбыстрый возврат капитала")
else:
    m_col3.metric("Окупаемость $4,500", f"~ {roi_months:.1f} мес.", delta="После старта релиза")

st.markdown("---")

# Построение графика
months = ['М1 (Разработка)', 'М2 (Разработка)', 'М3 (Тест)', 'М4 (Релиз)', 'М5', 'М6']
balance = [-4500, -4500, -4100, 
           -4100 + payout_step, 
           -4100 + (payout_step * 2), 
           -4100 + (payout_step * 3)]

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.axhline(0, color='gray', linewidth=0.8, linestyle='--')
ax.plot(months, balance, marker='o', color='#00e676', linewidth=2.5, label="Баланс")
ax.fill_between(months, balance, 0, where=[b<0 for b in balance], color='#ff1744', alpha=0.15)
ax.fill_between(months, balance, 0, where=[b>=0 for b in balance], color='#00e676', alpha=0.15)
ax.set_ylabel("Капитал ($)")
ax.set_title("График окупаемости стартовых инвестиций")
ax.grid(True, alpha=0.2)

st.pyplot(fig)