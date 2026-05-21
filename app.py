import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройки веб-страницы
st.set_page_config(page_title="Abyss 99 Realistic Model v3.2", layout="wide")

st.title("🐙 Бизнес-модель: «99 Ночей в Бездне» (v3.2)")
st.write("Целевая сессия для вовлечения пересмотрена до **15 минут**.")

# Константы
ROBLOX_TAX = 0.30
INVESTMENT = 4500
TARGET_SESSION = 15.0  
PREMIUM_ROBUX_PER_MINUTE = 0.7  # Реалистичный средний рейт Roblox Payouts

# --- ИНТЕРФЕЙС: БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.header("🎛️ Управление симуляцией")
input_mode = st.sidebar.radio("Режим ввода:", ("Ползунки", "Ввод вручную"))

if input_mode == "Ползунки":
    ccu = st.sidebar.slider("Средний онлайн (CCU):", 10, 50000, value=500, step=50)
    session_time = st.sidebar.slider("Длина сессии (минут):", 1, 120, value=15, step=1)
    base_d1 = st.sidebar.slider("Базовый D1 Retention (%):", 10.0, 60.0, value=32.0, step=1.0)
    
    # Расчет удержания для вывода слева
    retention_factor = (session_time / TARGET_SESSION) ** 1.5 if session_time < TARGET_SESSION else min(1.2, 1.0 + (session_time - TARGET_SESSION) / 120.0)
    d1_calc = max(0.0, min(base_d1 * retention_factor, 75.0))
    alpha = 0.55
    d7_calc = d1_calc * (7 ** -alpha)
    d30_calc = d1_calc * (30 ** -alpha)
    
    # Блок удержания на левой панели
    st.sidebar.text(f"📊 Текущий D1: {d1_calc:.1f}%")
    st.sidebar.text(f"📈 Расчетный D7: {d7_calc:.1f}%")
    st.sidebar.text(f"📉 Расчетный D30: {d30_calc:.1f}%")
    st.sidebar.markdown("---")

    base_conv = st.sidebar.slider("Базовая конверсия (%):", 0.5, 10.0, value=2.5, step=0.1) / 100.0
    base_arppu = st.sidebar.slider("Базовый чек донатера (R$):", 50, 2000, value=280, step=10)
    devex_rate = st.sidebar.slider("Курс DevEx ($ за 1 R$):", 0.0010, 0.0100, value=0.0035, step=0.0001, format="%.4f")
    premium_ratio = st.sidebar.slider("Доля Premium игроков (%):", 0.5, 15.0, value=3.0, step=0.5) / 100.0
    
    st.sidebar.markdown("---")
    with st.sidebar.container():
        st.subheader("💰 Налоги и Распределение")
        tax_rate = st.sidebar.slider("Налог на вывод (%):", 0, 20, value=6, step=1) / 100.0
        reinvest_rate = st.sidebar.slider("Поддержка игры / Фонд развития (%):", 0, 50, value=15, step=5) / 100.0
        marketing_rate = st.sidebar.slider("Маркетинг (%):", 0, 40, value=10, step=5) / 100.0
        share = st.sidebar.slider("Доля инвестора (%):", 0, 100, value=35, step=5) / 100.0
else:
    ccu = st.sidebar.number_input("Средний онлайн (CCU):", 0, 100000, value=500, step=100)
    session_time = st.sidebar.number_input("Длина сессии (мин):", 1, 240, value=15, step=1)
    base_d1 = st.sidebar.number_input("Базовый D1 Retention (%):", 0.0, 100.0, value=32.0, step=1.0)
    
    retention_factor = (session_time / TARGET_SESSION) ** 1.5 if session_time < TARGET_SESSION else min(1.2, 1.0 + (session_time - TARGET_SESSION) / 120.0)
    d1_calc = max(0.0, min(base_d1 * retention_factor, 75.0))
    alpha = 0.55
    d7_calc = d1_calc * (7 ** -alpha)
    d30_calc = d1_calc * (30 ** -alpha)
    
    st.sidebar.text(f"📊 Текущий D1: {d1_calc:.1f}%")
    st.sidebar.text(f"📈 Расчетный D7: {d7_calc:.1f}%")
    st.sidebar.text(f"📉 Расчетный D30: {d30_calc:.1f}%")
    st.sidebar.markdown("---")

    base_conv = st.sidebar.number_input("Базовая конверсия (%):", 0.0, 100.0, value=2.5, step=0.1) / 100.0
    base_arppu = st.sidebar.number_input("Базовый чек донатера (R$):", 0, 100000, value=280, step=50)
    devex_rate = st.sidebar.number_input("Курс DevEx ($ за 1 R$):", 0.0000, 0.0100, value=0.0035, step=0.0001, format="%.4f")
    premium_ratio = st.sidebar.number_input("Доля Premium (%):", 0.0, 100.0, value=3.0, step=0.5) / 100.0
    
    st.sidebar.markdown("---")
    with st.sidebar.container():
        st.subheader("💰 Налоги и Распределение")
        tax_rate = st.sidebar.number_input("Налог на вывод (%):", 0, 100, value=6, step=1) / 100.0
        reinvest_rate = st.sidebar.number_input("Поддержка игры / Фонд развития (%):", 0, 100, value=15, step=5) / 100.0
        marketing_rate = st.sidebar.number_input("Маркетинг (%):", 0, 100, value=10, step=5) / 100.0
        share = st.sidebar.number_input("Доля инвестора (%):", 0, 100, value=35, step=5) / 100.0

# --- ЯДРО РАСЧЕТОВ ---
dau = (ccu * 1440) / TARGET_SESSION if TARGET_SESSION > 0 else 0
d1 = d1_calc

player_lifetime_days = 1 + sum([(d1/100.0) * (t ** -alpha) for t in range(2, 31)])
mau = dau * (30 / player_lifetime_days) if player_lifetime_days > 0 else 0

# Монетизация донатов
if session_time < TARGET_SESSION:
    session_mon_factor = (session_time / TARGET_SESSION) ** 1.2
else:
    session_mon_factor = 1.0 + ((session_time - TARGET_SESSION) / TARGET_SESSION) ** 0.6

retention_mon_factor = max(0.1, min(1.2, d1 / base_d1)) if base_d1 > 0 else 0.1

real_conv = min(0.15, base_conv * (session_mon_factor ** 0.5) * retention_mon_factor)
real_arppu = base_arppu * (session_mon_factor ** 0.7)

# Финансы (Донаты)
monthly_paying_users = (dau * real_conv) * player_lifetime_days
gross_robux_donates = monthly_paying_users * real_arppu
net_usd_donates = (gross_robux_donates * (1.0 - ROBLOX_TAX)) * devex_rate

# Расчет Premium Payouts (на основе общего времени онлайна за месяц)
total_minutes_monthly = ccu * 60 * 24 * 30
premium_minutes_monthly = total_minutes_monthly * premium_ratio
gross_premium_robux = premium_minutes_monthly * PREMIUM_ROBUX_PER_MINUTE
premium_bonus_usd = (gross_premium_robux * (1.0 - ROBLOX_TAX)) * devex_rate

# Общий итог
total_gross_usd = net_usd_donates + premium_bonus_usd

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
f1.metric("Gross USD (Донаты + Премиум)", f"${total_gross_usd:,.2f}")
f2.metric("Чистая прибыль студии", f"${clear_profit_usd:,.2f}")
f3.metric("Выплата инвестору", f"${investor_payout_usd:,.2f}")
f4.metric("Срок ROI", f"{INVESTMENT/investor_payout_usd:.1f} мес" if investor_payout_usd > 0 else "∞")

# Инфо-плашка для прозрачности премиум дохода
st.info(f"ℹ️ В том числе чистый доход от Premium Payouts: ${premium_bonus_usd:,.2f} в месяц ({int(gross_premium_robux):,} R$)")

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