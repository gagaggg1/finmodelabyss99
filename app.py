import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройки
st.set_page_config(page_title="Abyss 99 Business Model", layout="wide")
st.title("🐙 Abyss 99: Финансовая модель Audience Expansion")

# --- 1. SIDEBAR: УПРАВЛЕНИЕ ---
st.sidebar.header("🎛️ Параметры трафика")
ccu = st.sidebar.number_input("Текущий CCU:", 100, 100000, 1000, 100)
session_time = st.sidebar.number_input("Длина сессии (мин):", 5, 240, 15)
investment = st.sidebar.number_input("Инвестиции ($):", 0, 100000, 4500)

st.sidebar.markdown("---")
st.sidebar.subheader("💎 Воронка Audience Expansion")
attr_rate = st.sidebar.slider("1. Attribution Rate (%)", 10.0, 60.0, 45.0) / 100
retention_10min = st.sidebar.slider("2. Retention 10+ min (%)", 20.0, 80.0, 55.0) / 100
tracking_success = st.sidebar.slider("3. System Eligibility (%)", 30.0, 90.0, 65.0) / 100
qualified_spender_rate = st.sidebar.slider("4. Spender ($10+/60d) Rate (%)", 0.5, 8.0, 3.5, step=0.1) / 100
avg_spend = st.sidebar.number_input("Средний чек пользователя ($)", 5.0, 100.0, 15.0)

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Экономика")
share = st.sidebar.slider("Доля инвестора (%)", 0, 100, 35) / 100

# --- 2. ЯДРО РАСЧЕТОВ ---
# Трафик
daily_players = (ccu * 1440) / session_time if session_time > 0 else 0

# Воронка Revenue (AE)
# Формула: DAU * (Шаги воронки) * (Доля качественных плательщиков) * (Чек) * 35%
qualified_spenders = daily_players * attr_rate * retention_10min * tracking_success * qualified_spender_rate
monthly_revenue_ae = (qualified_spenders * (avg_spend * 0.35)) * 30

# Внутриигровые донаты (База)
net_usd_donates = (daily_players * 0.025 * 280 * 0.7) * 0.0035 * 30

# Финансы
total_gross = net_usd_donates + monthly_revenue_ae
total_pool = total_gross * 0.69 # После вычета 6% налог, 15% развитие, 10% маркетинг
investor_payout = total_pool * share

# --- 3. ИНТЕРФЕЙС: ДАШБОРД ---
col1, col2, col3 = st.columns(3)
col1.metric("DAU (Активные за день)", f"{int(daily_players):,}")
col2.metric("Gross Revenue (мес)", f"${total_gross:,.2f}")
col3.metric("Выплата инвестору", f"${investor_payout:,.2f}")

st.markdown("---")
st.subheader("📊 Детализация")
c1, c2 = st.columns(2)
c1.metric("Revenue от Audience Expansion", f"${monthly_revenue_ae:,.2f}")
c2.metric("ROI (срок окупаемости)", f"{investment/investor_payout:.1f} мес" if investor_payout > 0 else "∞")

# Визуализация воронки
fig, ax = plt.subplots(figsize=(10, 2))
steps = ['DAU', 'Attributed', '10min+', 'Eligible', 'Paying (>$10)']
values = [daily_players, 
          daily_players * attr_rate, 
          daily_players * attr_rate * retention_10min,
          daily_players * attr_rate * retention_10min * tracking_success,
          qualified_spenders * 100] # x100 для наглядности

ax.barh(steps, values, color='#00ff41')
ax.set_title("Воронка квалификации пользователей")
st.pyplot(fig)