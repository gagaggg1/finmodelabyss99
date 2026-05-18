import streamlit as st
import matplotlib.pyplot as plt

# Настройки веб-страницы
st.set_page_config(page_title="Abyss 99 Pro Financial Model", layout="wide")

st.title("⚓ Профессиональная бизнес-модель: «99 Ночей в Бездне»")
st.write("Калькулятор доходности с расчетом дневной активности (DAO), коэффициента удержания и продуктовых метрик.")

# Фиксированные константы
ROBLOX_TAX = 0.30       # Комиссия платформы Roblox
INVESTMENT = 4500       # Стартовый капитал инвестора

# 1. Надежная инициализация базовых значений в session_state
if "ccu" not in st.session_state: st.session_state["ccu"] = 1500
if "mau" not in st.session_state: st.session_state["mau"] = 250000
if "dau" not in st.session_state: st.session_state["dau"] = 30000
if "conv" not in st.session_state: st.session_state["conv"] = 2.0
if "arppu" not in st.session_state: st.session_state["arppu"] = 250
if "devex_rate" not in st.session_state: st.session_state["devex_rate"] = 0.0035
if "session_time" not in st.session_state: st.session_state["session_time"] = 35
if "premium_ratio" not in st.session_state: st.session_state["premium_ratio"] = 2.5
if "reinvest_rate" not in st.session_state: st.session_state["reinvest_rate"] = 15
if "tax_rate" not in st.session_state: st.session_state["tax_rate"] = 6
if "share" not in st.session_state: st.session_state["share"] = 35

# Боковая панель управления
st.sidebar.header("🎛️ Настройка переменных")
input_mode = st.sidebar.radio("Режим ввода данных:", ("Ползунки", "Ввод вручную"))

st.sidebar.markdown("---")

# 2. Отрисовка интерфейса (Ползунки или Ручной ввод)
if input_mode == "Ползунки":
    ccu = st.sidebar.slider("Средний онлайн (CCU):", min_value=0, max_value=30000, value=int(st.session_state["ccu"]), step=100, key="ccu_slide")
    mau = st.sidebar.slider("Игроков в месяц (MAU):", min_value=10000, max_value=5000000, value=int(st.session_state["mau"]), step=10000, key="mau_slide")
    dau = st.sidebar.slider("Игроков в день (DAU):", min_value=1000, max_value=500000, value=int(st.session_state["dau"]), step=1000, key="dau_slide")
    conv_pct = st.sidebar.slider("Конверсия в донат (%):", min_value=0.0, max_value=10.0, value=float(st.session_state["conv"]), step=0.1, format="%.1f", key="conv_slide")
    arppu = st.sidebar.slider("Средний чек донатера (Robux):", min_value=10, max_value=2000, value=int(st.session_state["arppu"]), step=10, key="arppu_slide")
    devex_rate = st.sidebar.slider("Курс DevEx ($ за 1 Robux):", min_value=0.0010, max_value=0.0100, value=float(st.session_state["devex_rate"]), step=0.0001, format="%.4f", key="devex_slide")
    
    st.sidebar.markdown("### 🕒 Вовлеченность (Premium Payouts)")
    session_time = st.sidebar.slider("Длина сессии (минут):", min_value=5, max_value=120, value=int(st.session_state["session_time"]), step=5, key="time_slide")
    premium_ratio_pct = st.sidebar.slider("Доля Premium игроков (%):", min_value=0.5, max_value=10.0, value=float(st.session_state["premium_ratio"]), step=0.1, format="%.1f", key="prem_slide")
    
    st.sidebar.markdown("### 📈 Экономика и Распределение")
    reinvest_rate_pct = st.sidebar.slider("Фонд развития игры (% от прибыли):", min_value=0, max_value=50, value=int(st.session_state["reinvest_rate"]), step=5, key="reinvest_slide")
    tax_rate_pct = st.sidebar.slider("Налог на вывод денег (%):", min_value=0, max_value=20, value=int(st.session_state["tax_rate"]), step=1, key="tax_slide")
    share_pct = st.sidebar.slider("Доля инвестора после ROI (%):", min_value=0, max_value=100, value=int(st.session_state["share"]), step=5, key="share_slide")
else:
    ccu = st.sidebar.number_input("Средний онлайн (CCU):", min_value=0, max_value=100000, value=int(st.session_state["ccu"]), step=100, key="ccu_num")
    mau = st.sidebar.number_input("Игроков в месяц (MAU):", min_value=0, max_value=50000000, value=int(st.session_state["mau"]), step=10000, key="mau_num")
    dau = st.sidebar.number_input("Игроков в день (DAU):", min_value=0, max_value=5000000, value=int(st.session_state["dau"]), step=1000, key="dau_num")
    conv_pct = st.sidebar.number_input("Конверсия в донат (%):", min_value=0.0, max_value=100.0, value=float(st.session_state["conv"]), step=0.1, format="%.1f", key="conv_num")
    arppu = st.sidebar.number_input("Средний чек донатера (Robux):", min_value=0, max_value=100000, value=int(st.session_state["arppu"]), step=10, key="arppu_num")
    devex_rate = st.sidebar.number_input("Курс DevEx ($ за 1 Robux):", min_value=0.0010, max_value=0.1000, value=float(st.session_state["devex_rate"]), step=0.0001, format="%.4f", key="devex_num")
    
    st.sidebar.markdown("### 🕒 Вовлеченность (Premium Payouts)")
    session_time = st.sidebar.number_input("Длина сессии (минут):", min_value=1, max_value=240, value=int(st.session_state["session_time"]), step=5, key="time_num")
    premium_ratio_pct = st.sidebar.number_input("Доля Premium игроков (%):", min_value=0.0, max_value=100.0, value=float(st.session_state["premium_ratio"]), step=0.1, format="%.1f", key="prem_num")

    st.sidebar.markdown("### 📈 Экономика и Распределение")
    reinvest_rate_pct = st.sidebar.number_input("Фонд развития игры (% от прибыли):", min_value=0, max_value=100, value=int(st.session_state["reinvest_rate"]), step=5, key="reinvest_num")
    tax_rate_pct = st.sidebar.number_input("Налог на вывод денег (%):", min_value=0, max_value=100, value=int(st.session_state["tax_rate"]), step=1, key="tax_num")
    share_pct = st.sidebar.number_input("Доля инвестора после ROI (%):", min_value=0, max_value=100, value=int(st.session_state["share"]), step=5, key="share_num")

# 3. Синхронизация данных с памятью
st.session_state["ccu"] = ccu
st.session_state["mau"] = mau
st.session_state["dau"] = dau
st.session_state["conv"] = conv_pct
st.session_state["arppu"] = arppu
st.session_state["devex_rate"] = devex_rate
st.session_state["session_time"] = session_time
st.session_state["premium_ratio"] = premium_ratio_pct
st.session_state["reinvest_rate"] = reinvest_rate_pct
st.session_state["tax_rate"] = tax_rate_pct
st.session_state["share"] = share_pct

# Конвертация процентов для формул
conv = float(conv_pct) / 100.0
premium_ratio = float(premium_ratio_pct) / 100.0
reinvest_rate = float(reinvest_rate_pct) / 100.0
tax_rate = float(tax_rate_pct) / 100.0
share = float(share_pct) / 100.0

# --- РАСЧЕТЫ ЭКОНОМИКИ ---
def usd_to_robux(usd, rate):
    return usd / rate if rate > 0 else 0

# Прямые донаты
paying_users = mau * conv
gross_robux_donates = paying_users * arppu
net_usd_donates = (gross_robux_donates * (1.0 - ROBLOX_TAX)) * devex_rate

# Premium Payouts
premium_bonus_usd = ccu * (session_time / 30.0) * (premium_ratio / 0.02)
total_gross_usd = net_usd_donates + premium_bonus_usd
total_gross_robux = usd_to_robux(total_gross_usd, devex_rate)

# Распределение бюджета
tax_usd = total_gross_usd * tax_rate
tax_robux = usd_to_robux(tax_usd, devex_rate)

reinvestment_usd = total_gross_usd * reinvest_rate
reinvestment_robux = usd_to_robux(reinvestment_usd, devex_rate)

total_clear_profit_usd = total_gross_usd - tax_usd - reinvestment_usd
total_clear_profit_robux = usd_to_robux(total_clear_profit_usd, devex_rate)

investor_payout_usd = total_clear_profit_usd * share
investor_payout_robux = usd_to_robux(investor_payout_usd, devex_rate)

# Расчет расширенных метрик (LTV, ARPU, Sticky, ARPDAU)
arpu_usd = total_gross_usd / mau if mau > 0 else 0
arpu_robux = total_gross_robux / mau if mau > 0 else 0
ltv_usd = arpu_usd * 1.5  
ltv_robux = arpu_robux * 1.5

sticky_factor = (dau / mau) * 100.0 if mau > 0 else 0
arpdau_usd = total_gross_usd / 30 / dau if dau > 0 else 0
arpdau_robux = total_gross_robux / 30 / dau if dau > 0 else 0

# Окупаемость
payout_step = investor_payout_usd if share > 0 else total_clear_profit_usd
roi_months = INVESTMENT / payout_step if payout_step > 0 else 99

# --- ИНТЕРФЕЙС ---
st.subheader("💰 Финансовые итоги проекта (в месяц)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Общий оборот проекта", f"${total_gross_usd:,.2f}", f"R$ {int(total_gross_robux):,}")
col2.metric("Фонд обновлений (контент)", f"${reinvestment_usd:,.2f}", f"R$ {int(reinvestment_robux):,}")
col3.metric("Чистая прибыль студии", f"${total_clear_profit_usd:,.2f}", f"R$ {int(total_clear_profit_robux):,}")
col4.metric("Чистый доход инвестора", f"${investor_payout_usd:,.2f}", f"R$ {int(investor_payout_robux):,}")

st.markdown("---")

st.subheader("📊 Расширенные продуктовые метрики плейса")
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Ценность игрока (LTV)", f"${ltv_usd:.4f}", f"R$ {ltv_robux:.2f}", help="Сколько приносит 1 игрок за всё время активности")
m_col2.metric("Доход в день с активного (ARPDAU)", f"${arpdau_usd:.4f}", f"R$ {arpdau_robux:.2f}", help="Средний заработок с одного зашедшего в день")
m_col3.metric("Липучесть игры (Sticky Factor)", f"{sticky_factor:.1f}%", delta="Норма: 8%-20%", help="Какой процент от месячной аудитории заходит в игру каждый день")

if roi_months <= 1:
    m_col4.metric("Окупаемость инвестиций", "1-й месяц!", delta="⚡ Моментально")
else:
    m_col4.metric("Окупаемость инвестиций", f"~ {roi_months:.1f} мес.", delta="После старта релиза")

st.markdown("---")

# График
months = ['М1 (Разработка)', 'М2 (Разработка)', 'М3 (Тест)', 'М4 (Релиз)', 'М5', 'М6']
balance = [-4500, -4500, -4100, -4100 + payout_step, -4100 + (payout_step * 2), -4100 + (payout_step * 3)]

fig, ax = plt.subplots(figsize=(10, 3.2))
ax.axhline(0, color='gray', linewidth=0.8, linestyle='--')
ax.plot(months, balance, marker='o', color='#00e676', linewidth=2.5, label="Баланс")
ax.fill_between(months, balance, 0, where=[b<0 for b in balance], color='#ff1744', alpha=0.15)
ax.fill_between(months, balance, 0, where=[b>=0 for b in balance], color='#00e676', alpha=0.15)
ax.set_ylabel("Капитал ($)")
ax.set_title("График окупаемости стартовых инвестиций")
ax.grid(True, alpha=0.2)

st.pyplot(fig)