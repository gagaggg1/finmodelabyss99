import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройки веб-страницы
st.set_page_config(page_title="Abyss 99 Accurate Model v4.1", layout="wide")

st.title("🐙 Бизнес-модель: «99 Ночей в Бездне» (v4.1)")
st.write("Модель обновлена: VGU переведен в мультипликатор качества донатов, Engagement пересчитан через сессионный фактор.")

# Константы
ROBLOX_TAX = 0.30
INVESTMENT = 4500
TARGET_SESSION = 15.0  

# --- ИНТЕРФЕЙС: БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.header("🎛️ Управление симуляцией")
ccu = st.sidebar.slider("Средний онлайн (CCU):", 10, 50000, value=500, step=50)
session_time = st.sidebar.slider("Длина сессии (минут):", 1, 120, value=15, step=1)
d1_input = st.sidebar.slider("D1 Retention (%):", 10.0, 75.0, value=32.0, step=1.0)
st.sidebar.markdown("---")

base_conv = st.sidebar.slider("Базовая конверсия в донат (%):", 0.5, 10.0, value=2.5, step=0.1) / 100.0
base_arppu = st.sidebar.slider("Базовый чек донатера (R$):", 50, 2000, value=280, step=10)

st.sidebar.subheader("💎 Качество и Привлечение")
# vgu_ratio теперь влияет на качество монетизации, а не на триггер наград
vgu_ratio = st.sidebar.slider("Доля 'качественных' (VGU) игроков (%):", 0.0, 50.0, value=7.0, step=0.5) / 100.0
ae_percent = st.sidebar.slider("Audience Expansion (Qualified %):", 0.1, 5.0, value=1.0, step=0.1) / 100.0

st.sidebar.markdown("---")
with st.sidebar.container():
    st.subheader("💰 Налоги, Курс и Распределение")
    devex_rate = st.sidebar.slider("Курс DevEx ($ за 1 R$):", 0.0010, 0.0100, value=0.0035, step=0.0001, format="%.4f")
    tax_rate = st.sidebar.slider("Налог на вывод (%):", 0, 20, value=6, step=1) / 100.0
    reinvest_rate = st.sidebar.slider("Фонд развития (%):", 0, 50, value=15, step=5) / 100.0
    marketing_rate = st.sidebar.slider("Маркетинг (%):", 0, 40, value=10, step=5) / 100.0
    share = st.sidebar.slider("Доля инвестора (%):", 0, 100, value=35, step=5) / 100.0

# --- ЯДРО РАСЧЕТОВ ---
alpha = 0.55
dau = (ccu * 1440) / TARGET_SESSION if TARGET_SESSION > 0 else 0
player_lifetime_days = 1 + sum([(d1_input/100.0) * (t ** -alpha) for t in range(2, 31)])

if session_time < TARGET_SESSION:
    session_mon_factor = (session_time / TARGET_SESSION) ** 1.2
else:
    session_mon_factor = 1.0 + ((session_time - TARGET_SESSION) / TARGET_SESSION) ** 0.6

# Инженерный апгрейд: VGU влияет на Payer Rate и ARPPU
effective_payer_rate = base_conv * (1.0 + vgu_ratio * 0.5)
effective_arppu = base_arppu * (1.0 + vgu_ratio * 0.3)

# 1. Донаты
monthly_paying_users = (dau * min(0.20, effective_payer_rate * (session_mon_factor ** 0.5))) * player_lifetime_days
net_usd_donates = (monthly_paying_users * effective_arppu * (1.0 - ROBLOX_TAX)) * devex_rate

# 2. РАСЧЕТ CREATOR REWARDS
# А) Daily Engagement: теперь зависит от Session Quality, а не VGU
session_quality_factor = 0.12 # 12% активных сессий проходят фильтр Roblox
engagement_rewards_usd = ((dau * session_quality_factor * 30) * 5.0 * (1.0 - ROBLOX_TAX)) * devex_rate

# Б) Affiliate Rewards: когортная модель с исправленным коэффициентом
qualified_decay = 15.0 
monthly_qualified_users = dau * ae_percent * qualified_decay
ae_payer_rate = 0.03 
affiliate_rewards_usd = monthly_qualified_users * ae_payer_rate * 15.0 * 0.35

awards_bonus_usd = engagement_rewards_usd + affiliate_rewards_usd
total_gross_usd = net_usd_donates + awards_bonus_usd

total_pool = total_gross_usd * (1.0 - tax_rate - reinvest_rate - marketing_rate)
investor_payout_usd = total_pool * share if total_pool > 0 else 0
clear_profit_usd = total_pool - investor_payout_usd

# --- ВЫВОД ---
col1, col2, col3 = st.columns(3)
col1.metric("DAU", f"{int(dau):,}")
col2.metric("Gross USD", f"${total_gross_usd:,.2f}")
col3.metric("Выплата инвестору", f"${investor_payout_usd:,.2f}")

st.info(f"ℹ️ Доход от Creator Rewards: ${awards_bonus_usd:,.2f} (Engagement: ${engagement_rewards_usd:,.2f} | Affiliate: ${affiliate_rewards_usd:,.2f})")

# График
fig, ax = plt.subplots(figsize=(10, 3.5))
months = np.arange(0, 7)
ax.plot(months, -INVESTMENT + (investor_payout_usd * months), color='#00ff41', marker='o', linewidth=2)
ax.axhline(0, color='white', lw=1, linestyle='--')
st.pyplot(fig)