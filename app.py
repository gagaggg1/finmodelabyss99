import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройки веб-страницы
st.set_page_config(page_title="Abyss 99 Accurate Model v4.0", layout="wide")

st.title("🐙 Бизнес-модель: «99 Ночей в Бездне» (v4.0)")
st.write("Модель исправлена: учтены прямые долларовые выплаты **35% Affiliate Share** за новичков.")

# Константы
ROBLOX_TAX = 0.30
INVESTMENT = 4500
TARGET_SESSION = 15.0  

# --- ИНТЕРФЕЙС: БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.header("🎛️ Управление симуляцией")
input_mode = st.sidebar.radio("Режим ввода:", ("Ползунки", "Ввод вручную"))

if input_mode == "Ползунки":
    ccu = st.sidebar.slider("Средний онлайн (CCU):", 10, 50000, value=500, step=50)
    session_time = st.sidebar.slider("Длина сессии (минут):", 1, 120, value=15, step=1)
    
    # Фиксированный D1 напрямую от пользователя
    d1_input = st.sidebar.slider("D1 Retention (%):", 10.0, 75.0, value=32.0, step=1.0)
    
    alpha = 0.55
    d7_calc = d1_input * (7 ** -alpha)
    d30_calc = d1_input * (30 ** -alpha)
    
    st.sidebar.text(f"📊 Зафиксированный D1: {d1_input:.1f}%")
    st.sidebar.text(f"📈 Расчетный D7: {d7_calc:.1f}%")
    st.sidebar.text(f"📉 Расчетный D30: {d30_calc:.1f}%")
    st.sidebar.markdown("---")

    base_conv = st.sidebar.slider("Базовая конверсия в донат (%):", 0.5, 10.0, value=2.5, step=0.1) / 100.0
    base_arppu = st.sidebar.slider("Базовый чек донатера (R$):", 50, 2000, value=280, step=10)
    
    # БЛОК НАСТРОЕК CREATOR REWARDS
    st.sidebar.subheader("💎 Creator Rewards")
    vgu_ratio = st.sidebar.slider("Доля Active Spenders на платформе (%):", 0.5, 15.0, value=7.0, step=0.5) / 100.0
    ae_independent = st.sidebar.slider("Audience Expansion:", 0.1, 10.0, value=1.0, step=0.1)
    
    st.sidebar.markdown("---")
    with st.sidebar.container():
        st.subheader("💰 Налоги, Курс и Распределение")
        devex_rate = st.sidebar.slider("Курс DevEx ($ за 1 R$):", 0.0010, 0.0100, value=0.0035, step=0.0001, format="%.4f")
        tax_rate = st.sidebar.slider("Налог на вывод (%):", 0, 20, value=6, step=1) / 100.0
        reinvest_rate = st.sidebar.slider("Поддержка игры / Фонд развития (%):", 0, 50, value=15, step=5) / 100.0
        marketing_rate = st.sidebar.slider("Маркетинг (%):", 0, 40, value=10, step=5) / 100.0
        share = st.sidebar.slider("Доля инвестора (%):", 0, 100, value=35, step=5) / 100.0
else:
    ccu = st.sidebar.number_input("Средний онлайн (CCU):", 0, 100000, value=500, step=100)
    session_time = st.sidebar.number_input("Длина сессии (мин):", 1, 240, value=15, step=1)
    
    d1_input = st.sidebar.number_input("D1 Retention (%):", 0.0, 100.0, value=32.0, step=1.0)
    
    alpha = 0.55
    d7_calc = d1_input * (7 ** -alpha)
    d30_calc = d1_input * (30 ** -alpha)
    
    st.sidebar.text(f"📊 Зафиксированный D1: {d1_input:.1f}%")
    st.sidebar.text(f"📈 Расчетный D7: {d7_calc:.1f}%")
    st.sidebar.text(f"📉 Расчетный D30: {d30_calc:.1f}%")
    st.sidebar.markdown("---")

    base_conv = st.sidebar.number_input("Базовая конверсия в донат (%):", 0.0, 100.0, value=2.5, step=0.1) / 100.0
    base_arppu = st.sidebar.number_input("Базовый чек донатера (R$):", 0, 100000, value=280, step=50)
    
    st.sidebar.subheader("💎 Creator Rewards")
    vgu_ratio = st.sidebar.number_input("Доля Active Spenders (%):", 0.0, 100.0, value=7.0, step=0.5) / 100.0
    ae_independent = st.sidebar.number_input("Audience Expansion:", 0.1, 10.0, value=1.0, step=0.1)
    
    st.sidebar.markdown("---")
    with st.sidebar.container():
        st.subheader("💰 Налоги, Курс and Распределение")
        devex_rate = st.sidebar.number_input("Курс DevEx ($ за 1 R$):", 0.0000, 0.0100, value=0.0035, step=0.0001, format="%.4f")
        tax_rate = st.sidebar.number_input("Налог на вывод (%):", 0, 100, value=6, step=1) / 100.0
        reinvest_rate = st.sidebar.number_input("Поддержка игры / Фонд развития (%):", 0, 100, value=15, step=5) / 100.0
        marketing_rate = st.sidebar.number_input("Маркетинг (%):", 0, 100, value=10, step=5) / 100.0
        share = st.sidebar.number_input("Доля инвестора (%):", 0, 100, value=35, step=5) / 100.0

# --- ЯДРО РАСЧЕТОВ ---
d1 = d1_input

# Определение суточного потока (DAU) на основе удерживаемого CCU
dau = (ccu * 1440) / TARGET_SESSION if TARGET_SESSION > 0 else 0

# Жизненный цикл игрока и MAU
player_lifetime_days = 1 + sum([(d1/100.0) * (t ** -alpha) for t in range(2, 31)])
mau = dau * (30 / player_lifetime_days) if player_lifetime_days > 0 else 0

# Влияние длины сессии на монетизацию донатов
if session_time < TARGET_SESSION:
    session_mon_factor = (session_time / TARGET_SESSION) ** 1.2
else:
    session_mon_factor = 1.0 + ((session_time - TARGET_SESSION) / TARGET_SESSION) ** 0.6

real_conv = min(0.15, base_conv * (session_mon_factor ** 0.5))
real_arppu = base_arppu * (session_mon_factor ** 0.7)

# 1. Расчет внутриигровых донатов (Геймпассы, валюта)
monthly_paying_users = (dau * real_conv) * player_lifetime_days
gross_robux_donates = monthly_paying_users * real_arppu
net_usd_donates = (gross_robux_donates * (1.0 - ROBLOX_TAX)) * devex_rate

# 2. РАСЧЕТ CREATOR REWARDS
# Часть А: Daily Engagement Rewards (5 R$ за топ-3 запуск от Active Spender)
daily_active_spenders = dau * vgu_ratio
top3_filter_ratio = 0.015  # Консервативные 1.5% прохождения фильтра топ-3 за сутки
monthly_qualified_engagement = (daily_active_spenders * top3_filter_ratio) * 30
rewards_from_engagement_robux = monthly_qualified_engagement * 5.0

# Переводим Часть А в USD через налог платформы и DevEx
engagement_rewards_usd = (rewards_from_engagement_robux * (1.0 - ROBLOX_TAX)) * devex_rate

# Часть Б: Affiliate Rewards (35% от первых $100 трат новых/вернувшихся юзеров = до $35 за человека ЧИСТЫМИ)
# Берем ультраконсервативный процент камбэков/регистраций (0.01% от месячного трафика)
new_or_returned_ratio = 0.0001  
monthly_qualified_affiliates = mau * new_or_returned_ratio
# Прямая выплата в USD от Roblox, без DevEx конвертации
affiliate_rewards_usd = monthly_qualified_affiliates * 35.0

# Итоговый суммарный доход от Creator Rewards в долларах
awards_bonus_usd = engagement_rewards_usd + affiliate_rewards_usd

# Общие финансовые итоги симуляции
total_gross_usd = net_usd_donates + awards_bonus_usd

total_pool = total_gross_usd * (1.0 - tax_rate - reinvest_rate - marketing_rate)
investor_payout_usd = total_pool * share if total_pool > 0 else 0
clear_profit_usd = total_pool - investor_payout_usd

# --- ВЫВОД ДАННЫХ НА ЭКРАН ---
col1, col2, col3 = st.columns(3)
col1.metric("Текущий онлайн (CCU)", f"{int(ccu):,}")
col2.metric("Активные за день (DAU)", f"{int(dau):,}")
col3.metric("Активные за месяц (MAU)", f"{int(mau):,}")

st.markdown("---")
st.subheader("📊 Финансы (в месяц)")
f1, f2, f3, f4 = st.columns(4)
f1.metric("Gross USD (Донаты + Creator Rewards)", f"${total_gross_usd:,.2f}")
f2.metric("Чистая прибыль студии", f"${clear_profit_usd:,.2f}")
f3.metric("Выплата инвестору", f"${investor_payout_usd:,.2f}")
f4.metric("Срок ROI", f"{INVESTMENT/investor_payout_usd:.1f} мес" if investor_payout_usd > 0 else "∞")

# Прозрачная плашка с точным разбором Creator Rewards
st.info(f"ℹ️ Доход от Creator Rewards: ${awards_bonus_usd:,.2f} в месяц. "
        f"(Из них Daily Engagement: ${engagement_rewards_usd:,.2f}; "
        f"Прямой долларовый Affiliate бонус за новичков: ${affiliate_rewards_usd:,.2f})")

# --- ГРАФИК ОКУПАЕМОСТИ ---
st.markdown("---")
st.subheader("📉 Динамика возврата инвестиций (Баланс инвестора)")

fig, ax = plt.subplots(figsize=(10, 3.5))

months = np.arange(0, 7)
balance_timeline = -INVESTMENT + (investor_payout_usd * months)

ax.plot(months, balance_timeline, color='#00ff41', marker='o', linewidth=2, label="Баланс инвестора ($)")
ax.axhline(0, color='white', lw=1, linestyle='--')

ax.set_xlabel("Месяцы после инвестирования")
ax.set_ylabel("Текущий баланс ($)")
ax.set_xticks(months)
ax.grid(True, alpha=0.2)
ax.legend()

st.pyplot(fig)