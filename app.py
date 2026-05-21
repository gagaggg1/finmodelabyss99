import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройки
st.set_page_config(page_title="Abyss 99 Realistic Model", layout="wide")
st.title("🐙 Бизнес-модель: «99 Ночей в Бездне» (Realistic Funnel)")

# --- ПАРАМЕТРЫ (SIDEBAR) ---
st.sidebar.header("🎛️ Настройка воронки")

# Основные данные
ccu = st.sidebar.number_input("Текущий CCU:", 0, 100000, value=1000, step=100)
session_time = st.sidebar.number_input("Длина сессии (мин):", 1, 240, value=15, step=1)

# Твоя 4-шаговая воронка
st.sidebar.markdown("---")
st.sidebar.subheader("💎 Воронка Audience Expansion")
attr_rate = st.sidebar.slider("1. Attribution Rate (30-60%)", 0.3, 0.6, value=0.45)
retention_10min = st.sidebar.slider("2. Retention 10+ min (40-70%)", 0.4, 0.7, value=0.55)
tracking_success = st.sidebar.slider("3. Tracking Success (50-80%)", 0.5, 0.8, value=0.65)
spender_conv = st.sidebar.slider("4. Spender Conv (2-5%)", 0.02, 0.05, value=0.035)
avg_spend = st.sidebar.number_input("Средний чек в Roblox ($):", 5.0, 100.0, value=15.0)

# --- ЯДРО РАСЧЕТОВ ---
# 1. Трафик
daily_players = (ccu * 1440) / session_time if session_time > 0 else 0

# 2. Расчет по твоей воронке (Audience Expansion)
# Сколько игроков реально квалифицируются
eligible_players = daily_players * attr_rate * retention_10min * tracking_success
# Сколько из них платят
paying_users = eligible_players * spender_conv
# Доход (35% от трат)
daily_revenue_ae = paying_users * (avg_spend * 0.35)
monthly_revenue_ae = daily_revenue_ae * 30

# 3. Внутриигровые донаты (оставляем базу)
net_usd_donates = (daily_players * 0.025 * 280 * 0.7) * 0.0035 * 30 # Упрощенная база

# --- ИТОГИ ---
total_monthly_gross = net_usd_donates + monthly_revenue_ae

# --- ВЫВОД НА ЭКРАН ---
col1, col2, col3 = st.columns(3)
col1.metric("Текущий CCU", f"{int(ccu):,}")
col2.metric("DAU", f"{int(daily_players):,}")
col3.metric("Eligible Users (Daily)", f"{int(eligible_players):,}")

st.markdown("---")
st.subheader("📊 Финансовый итог (в месяц)")
c1, c2 = st.columns(2)
c1.metric("Доход от Audience Expansion", f"${monthly_revenue_ae:,.2f}")
c2.metric("Доход от Геймпасов (База)", f"${net_usd_donates:,.2f}")

st.info(f"💡 **Вывод:** При CCU {ccu}, через Audience Expansion проходит {int(paying_users)} платящих игроков ежедневно. "
        f"Это приносит ${monthly_revenue_ae:,.2f} в месяц чистыми.")

# График эффективности
fig, ax = plt.subplots(figsize=(10, 2))
labels = ['Total Players', 'Attributed', '10+ Min Play', 'Tracked', 'Paying']
values = [daily_players, 
          daily_players * attr_rate, 
          daily_players * attr_rate * retention_10min,
          eligible_players,
          paying_users * 100] # Умножаем на 100 для видимости на графике

ax.barh(labels, values, color='#00ff41')
ax.set_title("Воронка фильтрации игроков (ежедневно)")
st.pyplot(fig)