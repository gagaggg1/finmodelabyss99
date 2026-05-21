import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройки
st.set_page_config(page_title="Abyss 99 Professional Model", layout="wide")
st.title("🐙 Бизнес-модель: «99 Ночей в Бездне» (Final Pro)")

# --- ПАРАМЕТРЫ (SIDEBAR) ---
st.sidebar.header("🎛️ Настройка модели")
ccu = st.sidebar.number_input("Текущий CCU:", value=1000, step=100)
session_time = st.sidebar.number_input("Длина сессии (мин):", value=15)
investment = st.sidebar.number_input("Инвестиции ($):", value=4500)

st.sidebar.markdown("---")
st.sidebar.subheader("💎 Воронка Audience Expansion")

# Твои утвержденные коэффициенты (реалистичные)
attr_rate = st.sidebar.slider("1. Attribution Rate (Flow)", 0.3, 0.6, value=0.45)
retention_10min = st.sidebar.slider("2. Retention 10+ min", 0.4, 0.7, value=0.55)
tracking_success = st.sidebar.slider("3. Tracking Success", 0.5, 0.8, value=0.65)
spender_conv = st.sidebar.slider("4. Spender Conv (New Users)", 0.02, 0.05, value=0.035)

avg_spend = st.sidebar.number_input("Средний чек в Roblox ($)", value=15.0)

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Финансовые коэффициенты")
share = st.sidebar.slider("Доля инвестора (%)", 0, 100, value=35) / 100
tax_rate = 0.06
reinvest = 0.15
marketing = 0.10

# --- ЯДРО РАСЧЕТОВ ---
# 1. Трафик
daily_players = (ccu * 1440) / session_time if session_time > 0 else 0

# 2. Воронка AE (Creator Rewards)
# Формула: (Поток) * (Аттр.) * (Удерж.) * (Трекинг) * (Конверсия в плательщика)
eligible_players = daily_players * attr_rate * retention_10min * tracking_success
paying_users = eligible_players * spender_conv

# Доход: 35% от трат пользователя на платформе
monthly_revenue_ae = (paying_users * (avg_spend * 0.35)) * 30

# 3. Базовые донаты (геймпассы)
net_usd_donates = (daily_players * 0.025 * 280 * 0.7) * 0.0035 * 30 

# ИТОГИ
total_gross = net_usd_donates + monthly_revenue_ae
total_pool = total_gross * (1.0 - tax_rate - reinvest - marketing)
investor_payout = total_pool * share
profit_studio = total_pool - investor_payout

# --- ВЫВОД ---
col1, col2, col3 = st.columns(3)
col1.metric("DAU", f"{int(daily_players):,}")
col2.metric("Gross USD/мес", f"${total_gross:,.2f}")
col3.metric("Выплата инвестору", f"${investor_payout:,.2f}")

st.markdown("---")
st.subheader("📊 Детализация дохода")
c1, c2, c3 = st.columns(3)
c1.metric("Revenue от AE (35%)", f"${monthly_revenue_ae:,.2f}")
c2.metric("Game Passes", f"${net_usd_donates:,.2f}")
c3.metric("ROI срок", f"{investment/investor_payout:.1f} мес" if investor_payout > 0 else "∞")

# График
fig, ax = plt.subplots(figsize=(10, 3))
months = np.arange(0, 7)
balance = -investment + (investor_payout * months) if investor_payout > 0 else [-investment]*7
ax.plot(months, balance, color='#00ff41', marker='o', linewidth=2)
ax.axhline(0, color='white', linestyle='--')
ax.set_title("Динамика возврата инвестиций (ROI)")
st.pyplot(fig)