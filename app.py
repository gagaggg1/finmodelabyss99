import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройки
st.set_page_config(page_title="Abyss 99 Professional Model", layout="wide")
st.title("🐙 Бизнес-модель: «99 Ночей в Бездне»")

# --- ПАРАМЕТРЫ ---
st.sidebar.header("🎛️ Параметры модели")
ccu = st.sidebar.number_input("Средний онлайн (CCU):", 0, 100000, value=500, step=100)
session_time = st.sidebar.number_input("Длина сессии (мин):", 1, 240, value=15, step=1)
d1_input = st.sidebar.number_input("D1 Retention (%):", 0.0, 100.0, value=32.0, step=1.0)
base_conv = st.sidebar.number_input("Конверсия в донат (%):", 0.0, 100.0, value=2.5, step=0.1) / 100.0
base_arppu = st.sidebar.number_input("Чек донатера (R$):", 0, 100000, value=280, step=50)

st.sidebar.markdown("---")
st.sidebar.subheader("💎 Creator Rewards")
vgu_ratio = st.sidebar.number_input("Доля Active Spenders (%):", 0.0, 100.0, value=7.0, step=0.5) / 100.0
new_or_returned_ratio = st.sidebar.number_input("Приток новичков от MAU (%):", 0.0, 10.0, value=1.0, step=0.1) / 100.0
affiliate_pay_conv = st.sidebar.number_input("Конверсия новичка в донат на платформе (%):", 0.0, 10.0, value=1.5, step=0.1) / 100.0

# --- ЯДРО РАСЧЕТОВ ---
ROBLOX_TAX = 0.30
INVESTMENT = 4500
TARGET_SESSION = 15.0  
alpha = 0.55

# Расчет трафика
dau = (ccu * 1440) / TARGET_SESSION if TARGET_SESSION > 0 else 0
player_lifetime_days = 1 + sum([(d1_input/100.0) * (t ** -alpha) for t in range(2, 31)])
mau = dau * (30 / player_lifetime_days) if player_lifetime_days > 0 else 0

# Донаты в игру
session_mon_factor = 1.0 + ((session_time - TARGET_SESSION) / TARGET_SESSION) ** 0.6 if session_time > TARGET_SESSION else (session_time / TARGET_SESSION) ** 1.2
real_conv = min(0.15, base_conv * (session_mon_factor ** 0.5))
real_arppu = base_arppu * (session_mon_factor ** 0.7)
net_usd_donates = (((dau * real_conv) * player_lifetime_days * real_arppu) * (1.0 - ROBLOX_TAX)) * 0.0035

# Creator Rewards
monthly_qualified_engagement = (dau * vgu_ratio * 0.015) * 30
engagement_rewards_usd = (monthly_qualified_engagement * 5.0 * (1.0 - ROBLOX_TAX)) * 0.0035
monthly_paying_affiliates = (mau * new_or_returned_ratio) * affiliate_pay_conv
affiliate_rewards_usd = monthly_paying_affiliates * (25.0 * 0.35)
awards_bonus_usd = engagement_rewards_usd + affiliate_rewards_usd

# Итоги
total_gross_usd = net_usd_donates + awards_bonus_usd
total_pool = total_gross_usd * (1.0 - 0.06 - 0.15 - 0.10)
investor_payout = total_pool * 0.35

# --- ВЫВОД ---
col1, col2, col3 = st.columns(3)
col1.metric("Текущий онлайн (CCU)", f"{int(ccu):,}")
col2.metric("Активные за день (DAU)", f"{int(dau):,}")
col3.metric("Активные за месяц (MAU)", f"{int(mau):,}")

st.markdown("---")
st.subheader("📊 Финансовый прогноз")
st.metric("Чистая прибыль инвестора (в месяц)", f"${investor_payout:,.2f}")
st.info(f"ℹ️ Доход от Creator Rewards: ${awards_bonus_usd:,.2f} в месяц.")

fig, ax = plt.subplots(figsize=(10, 3))
ax.plot(np.arange(0, 7), -INVESTMENT + (investor_payout * np.arange(0, 7)), color='#00ff41', marker='o')
ax.axhline(0, color='white', lw=1, linestyle='--')
st.pyplot(fig)