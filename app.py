import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройки веб-страницы
st.set_page_config(page_title="Abyss 99 Realistic Model v3.0", layout="wide")

# Стилизация под темную тему хоррора
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e2e8f0; }
    h1, h2, h3 { color: #00ffcc !important; text-shadow: 0 0 10px rgba(0,255,204,0.3); }
    .stSlider label { color: #a0aec0 !important; }
    .stNumberInput label { color: #a0aec0 !important; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐙 Реалистичная бизнес-модель: «99 Ночей в Бездне» (v3.0)")
st.write("Целевая сессия для вовлечения пересмотрена до **15 минут**.")

# Константы
ROBLOX_TAX = 0.30
INVESTMENT = 4500
TARGET_SESSION = 15.0  # НОВЫЙ ЛИМИТ

# --- ИНТЕРФЕЙС: БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.header("🎛️ Игровые метрики")
input_mode = st.sidebar.radio("Режим ввода:", ("Ползунки", "Ввод вручную"))

if input_mode == "Ползунки":
    ccu = st.sidebar.slider("Средний онлайн (CCU):", 10, 50000, value=500, step=50)
    session_time = st.sidebar.slider("Длина сессии (минут):", 1, 120, value=15, step=1)
    base_d1 = st.sidebar.slider("Базовый D1 Retention (%):", 10.0, 60.0, value=32.0, step=1.0)
    base_conv = st.sidebar.slider("Базовая конверсия (%):", 0.5, 10.0, value=2.5, step=0.1) / 100.0
    base_arppu = st.sidebar.slider("Базовый чек донатера (R$):", 50, 2000, value=280, step=10)
    devex_rate = st.sidebar.slider("Курс DevEx ($ за 1 R$):", 0.0010, 0.0100, value=0.0035, step=0.0001, format="%.4f")
    premium_ratio = st.sidebar.slider("Доля Premium игроков (%):", 0.5, 15.0, value=3.0, step=0.5) / 100.0
    
    # ПЛАШКА ВНИЗУ САЙДБАРА (ДЛЯ ПОЛЗУНКОВ)
    st.sidebar.markdown("---")
    st.sidebar.subheader("💰 Распределение и Налоги")
    tax_rate = st.sidebar.slider("Налог на вывод (%):", 0, 20, value=6, step=1) / 100.0
    reinvest_rate = st.sidebar.slider("Фонд развития (%):", 0, 50, value=15, step=5) / 100.0
    marketing_rate = st.sidebar.slider("Маркетинг (%):", 0, 40, value=10, step=5) / 100.0
    share = st.sidebar.slider("Доля инвестора (%):", 0, 100, value=35, step=5) / 100.0
else:
    ccu = st.sidebar.number_input("Средний онлайн (CCU):", 0, 100000, value=500, step=100)
    session_time = st.sidebar.number_input("Длина сессии (мин):", 1, 240, value=15, step=1)
    base_d1 = st.sidebar.number_input("Базовый D1 Retention (%):", 0.0, 100.0, value=32.0, step=1.0)
    base_conv = st.sidebar.number_input("Базовая конверсия (%):", 0.0, 100.0, value=2.5, step=0.1) / 100.0
    base_arppu = st.sidebar.number_input("Базовый чек донатера (R$):", 0, 100000, value=280, step=50)
    devex_rate = st.sidebar.number_input("Курс DevEx ($ за 1 R$):", 0.0000, 0.0100, value=0.0035, step=0.0001, format="%.4f")
    premium_ratio = st.sidebar.number_input("Доля Premium (%):", 0.0, 100.0, value=3.0, step=0.5) / 100.0
    
    # ПЛАШКА ВНИЗУ САЙДБАРА (ДЛЯ РУЧНОГО ВВОДА)
    st.sidebar.markdown("---")
    st.sidebar.subheader("💰 Распределение и Налоги")
    tax_rate = st.sidebar.number_input("Налог на вывод (%):", 0, 100, value=6, step=1) / 100.0
    reinvest_rate = st.sidebar.number_input("Фонд развития (%):", 0, 100, value=15, step=5) / 100.0
    marketing_rate = st.sidebar.number_input("Маркетинг (%):", 0, 100, value=10, step=5) / 100.0
    share = st.sidebar.number_input("Доля инвестора (%):", 0, 100, value=35, step=5) / 100.0

# --- ЯДРО РАСЧЕТОВ ---
# Retention с учетом лимита в 15 минут
retention_factor = (session_time / TARGET_SESSION) ** 2 if session_time < TARGET_SESSION else min(1.15, 1.0 + (session_time - TARGET_SESSION) / 100.0)
d1 = max(0.0, min(base_d1 * retention_factor, 75.0))
alpha = 0.55
player_lifetime_days = 1 + sum([(d1/100.0) * (t ** -alpha) for t in range(2, 31)])

# Трафик завязан на базовые 15 минут, чтобы сессия не роняла DAU
dau = (ccu * 1440) / TARGET_SESSION if TARGET_SESSION > 0 else 0
mau = dau * (30 / player_lifetime_days) if player_lifetime_days > 0 else 0

# Монетизация: коэффициенты масштабируются от сессии
session_mon_factor = max(0.02, session_time / TARGET_SESSION)
retention_mon_factor = max(0.1, min(1.0, d1 / base_d1)) if base_d1 > 0 else 0.1

real_conv = min(1.0, base_conv * (session_mon_factor ** 0.5) * retention_mon_factor)
real_arppu = base_arppu * (session_mon_factor ** 0.7)

# Финансы
monthly_paying_users = (dau * real_conv) * player_lifetime_days
gross_robux_donates = monthly_paying_users * real_arppu

# Премиум-выплаты
premium_bonus_usd = ((dau * premium_ratio) * session_time * 30) * 0.00015 * (d1 / 100.0)
net_usd_donates = (gross_robux_donates * (1.0 - ROBLOX_TAX)) * devex_rate
total_gross_usd = net_usd_donates + premium_bonus_usd

# Распределение прибыли
total_pool = total_gross_usd * (1.0 - tax_rate - reinvest_rate - marketing_rate)
investor_payout_usd = total_pool * share if total_pool > 0 else 0
clear_profit_usd = total_pool - investor_payout_usd

# --- ВЫВОД ДАННЫХ НА ОСНОВНОЙ СТРАНИЦЕ ---
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("DAU", f"{int(dau):,}")
col2.metric("MAU", f"{int(mau):,}")
col3.metric("D1 Retention", f"{d1:.1f}%")

st.markdown("---")
st.subheader("📊 Финансы (в месяц)")
f1, f2, f3, f4 = st.columns(4)
f1.metric("Gross USD", f"${total_gross_usd:,.2f}")
f2.metric("Чистая прибыль студии", f"${clear_profit_usd:,.2f}")
f3.metric("Выплата инвестору", f"${investor_payout_usd:,.2f}")
f4.metric("Срок ROI", f"{INVESTMENT/investor_payout_usd:.1f} мес" if investor_payout_usd > 0 else "∞")

# График
st.markdown("---")
st.subheader("📉 Динамика возврата инвестиций (Баланс инвестора)")

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 3.5))
fig.patch.set_facecolor('#0b0f19')
ax.set_facecolor('#111827')

timeline = np.arange(0, 7)
balance_timeline = -INVESTMENT + (investor_payout_usd * timeline)

# Неоновая линия баланса
ax.plot(timeline, balance_timeline, color='#00ffcc', marker='o', linewidth=2.5, zorder=3, label="Баланс инвестора ($)")
ax.plot(timeline, balance_timeline, color='#00ffcc', alpha=0.3, linewidth=6, zorder=2) # Эффект свечения
ax.axhline(0, color='#4a5568', linestyle='--', lw=1, alpha=0.6)

ax.set_xlabel("Месяцы с момента релиза", color='#a0aec0')
ax.set_ylabel("Капитал инвестора ($)", color='#a0aec0')
ax.grid(True, color='#2d3748', alpha=0.4, linestyle=':')
ax.set_xticks(timeline)
ax.legend(facecolor='#111827', edgecolor='#2d3748', loc='upper left')

st.pyplot(fig)