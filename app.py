import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройки веб-страницы
st.set_page_config(page_title="Abyss 99 Accurate Model v4.0", layout="wide")
st.title("🐙 Бизнес-модель: «99 Nights in the Abyss»")

ROBLOX_TAX = 0.30
INVESTMENT = 4500
TARGET_SESSION = 15.0 

# --- ИНТЕРФЕЙС: БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.header("🎛️ Управление симуляцией")
input_mode = st.sidebar.radio("Режим ввода:", ("Ползунки", "Ввод вручную"), key="mode_selector")

# Функция выбора ключа в зависимости от режима
def get_key(base):
    return f"{base}_{'s' if input_mode == 'Ползунки' else 'n'}"

if input_mode == "Ползунки":
    ccu = st.sidebar.slider("Средний онлайн (CCU):", 10, 50000, 500, step=50, key="ccu_s")
    session_time = st.sidebar.slider("Длина сессии (минут):", 1, 120, 15, key="sess_s")
    d1_input = st.sidebar.slider("D1 Retention (%):", 10.0, 75.0, 32.0, key="d1_s")
    st.sidebar.subheader("💸 Монетизация")
    base_conv = st.sidebar.slider("Конверсия доната (%):", 0.5, 10.0, 2.5, key="conv_s") / 100.0
    base_arppu = st.sidebar.slider("Средний чек (R$):", 50, 2000, 280, key="arppu_s")
    st.sidebar.subheader("💎 Creator Rewards")
    vgu_ratio = st.sidebar.slider("Доля Active Spenders (%):", 0.5, 15.0, 7.0, key="vgu_s") / 100.0
    behavioral_filter = st.sidebar.slider("Эффективность фильтра (%):", 1.0, 50.0, 12.0, key="filt_s") / 100.0
    ae_percent = st.sidebar.slider("Audience Expansion :", 0.1, 5.0, 1.0, key="ae_s") / 100.0
    devex_rate = st.sidebar.slider("Курс DevEx:", 0.001, 0.01, 0.0035, format="%.4f", key="dev_s")
    tax_rate = st.sidebar.slider("Налог (%):", 0, 20, 6, key="tax_s") / 100.0
    reinvest_rate = st.sidebar.slider("Поддержка игры (%):", 0, 50, 15, key="rei_s") / 100.0
    marketing_rate = st.sidebar.slider("Маркетинг (%):", 0, 40, 10, key="mkt_s") / 100.0
    share = st.sidebar.slider("Доля инвестора (%):", 0, 100, 35, key="shr_s") / 100.0
else:
    ccu = st.sidebar.number_input("Средний онлайн (CCU):", 0, 100000, 500, key="ccu_n")
    session_time = st.sidebar.number_input("Длина сессии (мин):", 1, 240, 15, key="sess_n")
    d1_input = st.sidebar.number_input("Day 1 Retention (%):", 0.0, 100.0, 32.0, key="d1_n")
    st.sidebar.subheader("💸 Монетизация")
    base_conv = st.sidebar.number_input("Конверсия (%):", 0.0, 100.0, 2.5, key="conv_n") / 100.0
    base_arppu = st.sidebar.number_input("Средний чек (R$):", 0, 100000, 280, key="arppu_n")
    st.sidebar.subheader("💎 Creator Rewards")
    vgu_ratio = st.sidebar.number_input("Доля Active Spenders (%):", 0.0, 100.0, 7.0, key="vgu_n") / 100.0
    behavioral_filter = st.sidebar.number_input("Эффективность фильтра (%):", 0.0, 100.0, 12.0, key="filt_n") / 100.0
    ae_percent = st.sidebar.number_input("Audience Expansion :", 0.1, 5.0, 1.0, key="ae_n") / 100.0
    devex_rate = st.sidebar.number_input("Курс DevEx:", 0.0, 0.01, 0.0035, format="%.4f", key="dev_n")
    tax_rate = st.sidebar.number_input("Налог (%):", 0, 100, 6, key="tax_n") / 100.0
    reinvest_rate = st.sidebar.number_input("Поддержка игры (%):", 0, 100, 15, key="rei_n") / 100.0
    marketing_rate = st.sidebar.number_input("Маркетинг (%):", 0, 100, 10, key="mkt_n") / 100.0
    share = st.sidebar.number_input("Доля инвестора (%):", 0, 100, 35, key="shr_n") / 100.0

# --- ЯДРО РАСЧЕТОВ ---
alpha = 0.55
d1 = d1_input
dau = (ccu * 1440) / TARGET_SESSION if TARGET_SESSION > 0 else 0
player_lifetime_days = 1 + sum([(d1/100.0) * (t ** -alpha) for t in range(2, 31)])
mau = dau * (30 / player_lifetime_days) if player_lifetime_days > 0 else 0
session_mon_factor = (session_time / TARGET_SESSION) ** 1.2 if session_time < TARGET_SESSION else 1.0 + ((session_time - TARGET_SESSION) / TARGET_SESSION) ** 0.6
real_conv = min(0.15, base_conv * (session_mon_factor ** 0.5))
real_arppu = base_arppu * (session_mon_factor ** 0.7)
net_usd_donates = ((dau * real_conv) * player_lifetime_days * real_arppu * (1.0 - ROBLOX_TAX)) * devex_rate
engagement_rewards_usd = ((dau * vgu_ratio) * behavioral_filter * 30 * 6.0 * (1.0 - ROBLOX_TAX)) * devex_rate
affiliate_rewards_usd = (dau * ae_percent * 15.0) * 0.03 * 15.0 * 0.35
total_gross_usd = net_usd_donates + engagement_rewards_usd + affiliate_rewards_usd
investor_payout_usd = (total_gross_usd * (1.0 - tax_rate - reinvest_rate - marketing_rate)) * share if total_gross_usd > 0 else 0

# --- ИНТЕРФЕЙС ---
c1, c2, c3 = st.columns(3)
c1.metric("CCU", f"{int(ccu):,}")
c2.metric("DAU", f"{int(dau):,}")
c3.metric("MAU", f"{int(mau):,}")
st.markdown("---")
f1, f2, f3, f4 = st.columns(4)
f1.metric("Gross USD", f"${total_gross_usd:,.2f}")
f2.metric("Чистая прибыль", f"${(total_gross_usd * (1 - tax_rate - reinvest_rate - marketing_rate)):,.2f}")
f3.metric("Прибыль инвестора", f"${investor_payout_usd:,.2f}")
f4.metric("ROI", f"{INVESTMENT/investor_payout_usd:.1f} мес" if investor_payout_usd > 0 else "∞")

# --- ГРАФИКИ ---
plt.style.use('dark_background')
fig_col1, fig_col2 = st.columns(2)

with fig_col1: # Retention
    st.subheader("🌊 Retention Curve")
    f1, a1 = plt.subplots(figsize=(6, 3)); f1.patch.set_facecolor('#0e1117'); a1.set_facecolor('#1a1d23')
    a1.plot(range(1, 31), [d1] + [d1 * (t**-alpha) for t in range(2, 31)], color='#7d3cff', linewidth=3)
    st.pyplot(f1)

with fig_col2: # Revenue per CCU
    st.subheader("🚀 Revenue per CCU")
    f2, a2 = plt.subplots(figsize=(6, 3)); f2.patch.set_facecolor('#0e1117'); a2.set_facecolor('#1a1d23')
    a2.bar(['100', '500', '1к', '2.5к', '5к'], [c * 0.015 for c in [100, 500, 1000, 2500, 5000]], color='#ffb703')
    st.pyplot(f2)

st.subheader("📉 ROI Timeline")
f3, a3 = plt.subplots(figsize=(10, 3)); f3.patch.set_facecolor('#0e1117'); a3.set_facecolor('#1a1d23')
months = np.arange(0, 7)
a3.plot(months, -INVESTMENT + (investor_payout_usd * months), color='#00f2ff', marker='o', linewidth=3)
a3.axhline(0, color='red', linestyle='--')
st.pyplot(f3)