import streamlit as st
import matplotlib.pyplot as plt

# Настройки веб-страницы
st.set_page_config(page_title="Abyss 99 Business Model", layout="wide")

st.title("🐙 Бизнес-модель: «99 Ночей в Бездне»")
st.write("Профессиональный расчет доходности. Все показатели связаны: изменение вовлеченности автоматически меняет онлайн и прибыль.")

# Фиксированные константы
ROBLOX_TAX = 0.30       # Комиссия платформы Roblox
INVESTMENT = 4500       # Стартовый капитал инвестора

# 1. Инициализация базовых параметров в памяти (session_state)
if "dau" not in st.session_state: st.session_state["dau"] = 20000
if "sticky_factor" not in st.session_state: st.session_state["sticky_factor"] = 10.0
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
    st.sidebar.markdown("### 👥 Аудитория и Удержание")
    dau = st.sidebar.slider("Уникальные игроки в день (DAU):", min_value=1000, max_value=500000, value=int(st.session_state["dau"]), step=1000, key="dau_slide")
    sticky_factor_pct = st.sidebar.slider("Липучесть игры (Sticky Factor %):", min_value=5.0, max_value=30.0, value=float(st.session_state["sticky_factor"]), step=0.5, format="%.1f", key="sticky_slide")
    
    st.sidebar.markdown("### 🕒 Вовлеченность")
    session_time = st.sidebar.slider("Длина сессии (минут):", min_value=5, max_value=120, value=int(st.session_state["session_time"]), step=5, key="time_slide")
    premium_ratio_pct = st.sidebar.slider("Доля Premium игроков (%):", min_value=0.5, max_value=10.0, value=float(st.session_state["premium_ratio"]), step=0.1, format="%.1f", key="prem_slide")
    
    st.sidebar.markdown("### 💎 Монетизация")
    conv_pct = st.sidebar.slider("Конверсия в донат (%):", min_value=0.1, max_value=10.0, value=float(st.session_state["conv"]), step=0.1, format="%.1f", key="conv_slide")
    arppu = st.sidebar.slider("Средний чек донатера (Robux):", min_value=10, max_value=2000, value=int(st.session_state["arppu"]), step=10, key="arppu_slide")
    devex_rate = st.sidebar.slider("Курс DevEx ($ за 1 Robux):", min_value=0.0010, max_value=0.0100, value=float(st.session_state["devex_rate"]), step=0.0001, format="%.4f", key="devex_slide")
    
    st.sidebar.markdown("### 📈 Распределение прибыли")
    reinvest_rate_pct = st.sidebar.slider("Фонд развития игры (%):", min_value=0, max_value=50, value=int(st.session_state["reinvest_rate"]), step=5, key="reinvest_slide")
    tax_rate_pct = st.sidebar.slider("Налог на вывод денег (%):", min_value=0, max_value=20, value=int(st.session_state["tax_rate"]), step=1, key="tax_slide")
    share_pct = st.sidebar.slider("Доля инвестора после ROI (%):", min_value=0, max_value=100, value=int(st.session_state["share"]), step=5, key="share_slide")
else:
    st.sidebar.markdown("### 👥 Аудитория и Удержание")
    dau = st.sidebar.number_input("Уникальные игроки в день (DAU):", min_value=0, max_value=5000000, value=int(st.session_state["dau"]), step=1000, key="dau_num")
    sticky_factor_pct = st.sidebar.number_input("Липучесть игры (Sticky Factor %):", min_value=1.0, max_value=100.0, value=float(st.session_state["sticky_factor"]), step=0.5, format="%.1f", key="sticky_num")
    
    st.sidebar.markdown("### 🕒 Вовлеченность")
    session_time = st.sidebar.number_input("Длина сессии (минут):", min_value=1, max_value=240, value=int(st.session_state["session_time"]), step=5, key="time_num")
    premium_ratio_pct = st.sidebar.number_input("Доля Premium игроков (%):", min_value=0.0, max_value=100.0, value=float(st.session_state["premium_ratio"]), step=0.1, format="%.1f", key="prem_num")

    st.sidebar.markdown("### 💎 Монетизация")
    conv_pct = st.sidebar.number_input("Конверсия в донат (%):", min_value=0.0, max_value=100.0, value=float(st.session_state["conv"]), step=0.1, format="%.1f", key="conv_num")
    arppu = st.sidebar.number_input("Средний чек донатера (Robux):", min_value=0, max_value=100000, value=int(st.session_state["arppu"]), step=10, key="arppu_num")
    devex_rate = st.sidebar.number_input("Курс DevEx ($ за 1 Robux):", min_value=0.0010, max_value=0.1000, value=float(st.session_state["devex_rate"]), step=0.0001, format="%.4f", key="devex_num")

    st.sidebar.markdown("### 📈 Распределение прибыли")
    reinvest_rate_pct = st.sidebar.number_input("Фонд развития игры (%):", min_value=0, max_value=100, value=int(st.session_state["reinvest_rate"]), step=5, key="reinvest_num")
    tax_rate_pct = st.sidebar.number_input("Налог на вывод денег (%):", min_value=0, max_value=100, value=int(st.session_state["tax_rate"]), step=1, key="tax_num")
    share_pct = st.sidebar.number_input("Доля инвестора после ROI (%):", min_value=0, max_value=100, value=int(st.session_state["share"]), step=5, key="share_num")

# 3. Синхронизация данных с оперативной памятью
st.session_state["dau"] = dau
st.session_state["sticky_factor"] = sticky_factor_pct
st.session_state["conv"] = conv_pct
st.session_state["arppu"] = arppu
st.session_state["devex_rate"] = devex_rate
st.session_state["session_time"] = session_time
st.session_state["premium_ratio"] = premium_ratio_pct
st.session_state["reinvest_rate"] = reinvest_rate_pct
st.session_state["tax_rate"] = tax_rate_pct
st.session_state["share"] = share_pct

# Конвертация процентов для формул
sticky_factor = float(sticky_factor_pct) / 100.0
conv = float(conv_pct) / 100.0
premium_ratio = float(premium_ratio_pct) / 100.0
reinvest_rate = float(reinvest_rate_pct) / 100.0
tax_rate = float(tax_rate_pct) / 100.0
share = float(share_pct) / 100.0

# --- СЛОЖНЫЕ ЗАВИСИМЫЕ РАСЧЕТЫ ---

# 1. Автоматический расчет MAU (DAU / Sticky Factor)
mau = int(dau / sticky_factor) if sticky_factor > 0 else 0

# 2. Автоматический расчет онлайна (CCU) на основе DAU и времени сессии
ccu = int((dau * session_time) / 1440)

def usd_to_robux(usd, rate):
    return usd / rate if rate > 0 else 0

# Прямые донаты (зависят от MAU)
paying_users = mau * conv
gross_robux_donates = paying_users * arppu
net_usd_donates = (gross_robux_donates * (1.0 - ROBLOX_TAX)) * devex_rate

# Premium Payouts (зависят от рассчитанного CCU)
premium_bonus_usd = ccu * (session_time / 30.0) * (premium_ratio / 0.02)
total_gross_usd = net_usd_donates + premium_bonus_usd
total_gross_robux = usd_to_robux(total_gross_usd, devex_rate)

# Экономика расходов и выплат
tax_usd = total_gross_usd * tax_rate
tax_robux = usd_to_robux(tax_usd, devex_rate)

reinvestment_usd = total_gross_usd * reinvest_rate
reinvestment_robux = usd_to_robux(reinvestment_usd, devex_rate)

total_clear_profit_usd = total_gross_usd - tax_usd - reinvestment_usd
total_clear_profit_robux = usd_to_robux(total_clear_profit_usd, devex_rate)

investor_payout_usd = total_clear_profit_usd * share
investor_payout_robux = usd_to_robux(investor_payout_usd, devex_rate)

# Метрики продукта
arpu_usd = total_gross_usd / mau if mau > 0 else 0
arpu_robux = total_gross_robux / mau if mau > 0 else 0
ltv_usd = arpu_usd * 1.5  
ltv_robux = arpu_robux * 1.5
arpdau_usd = total_gross_usd / 30 / dau if dau > 0 else 0
arpdau_robux = total_gross_robux / 30 / dau if dau > 0 else 0

# Окупаемость
payout_step = investor_payout_usd if share > 0 else total_clear_profit_usd
roi_months = INVESTMENT / payout_step if payout_step > 0 else 99

# --- ИНТЕРФЕЙС И ВЫВОД ---

st.subheader("🖥️ Динамические показатели платформы")
sys_col1, sys_col2, sys_col3 = st.columns(3)
sys_col1.metric("Средний онлайн (CCU)", f"{ccu:,} чел.", help="Среднее кол-во людей в игре одновременно. Рассчитано автоматически.")
sys_col2.metric("Аудитория за месяц (MAU)", f"{mau:,} чел.", help="Общее кол-во уникальных игроков за месяц. Рассчитано автоматически.")
sys_col3.metric("Доход в день с активного (ARPDAU)", f"${arpdau_usd:.4f}", f"R$ {arpdau_robux:.2f}")

st.markdown("---")

st.subheader("💰 Финансовые итоги проекта (в месяц)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Общий оборот проекта", f"${total_gross_usd:,.2f}", f"R$ {int(total_gross_robux):,}")
col2.metric("Фонд обновлений", f"${reinvestment_usd:,.2f}", f"R$ {int(reinvestment_robux):,}")
col3.metric("Чистая прибыль студии", f"${total_clear_profit_usd:,.2f}", f"R$ {int(total_clear_profit_robux):,}")
col4.metric("Чистый доход инвестора", f"${investor_payout_usd:,.2f}", f"R$ {int(investor_payout_robux):,}")

st.markdown("---")

st.subheader("📊 Продуктовые метрики")
m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("Ценность игрока (LTV)", f"${ltv_usd:.4f}", f"R$ {ltv_robux:.2f}")
m_col2.metric("Sticky Factor", f"{sticky_factor_pct:.1f}%", help="Удержание аудитории.")

if roi_months <= 1:
    m_col3.metric("Окупаемость $4,500", "1-й месяц релиза!", delta="⚡ Моментально")
else:
    m_col3