import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# --- НАСТРОЙКИ ВЕБ-СТРАНИЦЫ ---
# ==========================================
# Устанавливаем параметры конфигурации для визуализации
st.set_page_config(page_title="Abyss 99 Population Simulation v5.0", layout="wide")

# ==========================================
# --- ЗАГОЛОВОК И ОПИСАНИЕ ---
# ==========================================
st.title("🐙 Симулятор популяции и бизнеса: «99 Ночей в Бездне» (v5.0)")
st.write("Модель: Полная структура с учетом накопления базы (Натуральный MAU) и элитных фильтров.")
st.write("Система теперь работает как открытый поток пользователей.")

# ==========================================
# --- КОНСТАНТЫ СИСТЕМЫ ---
# ==========================================
ROBLOX_TAX = 0.30       # Комиссия платформы при транзакции
INVESTMENT = 4500       # Входной порог инвестиций
TARGET_SESSION = 15.0   # Эталонная длина сессии для расчета

# ==========================================
# --- БОКОВАЯ ПАНЕЛЬ: УПРАВЛЕНИЕ ---
# ==========================================
st.sidebar.header("🚀 1. Acquisition Engine (Приток)")

# Параметры интенсивности притока пользователей
new_users_daily = st.sidebar.slider("Новых игроков в день:", 10, 5000, value=200, step=10)

# Параметры удержания (кривая Retention)
d1_input = st.sidebar.slider("D1 Retention (%):", 1.0, 75.0, value=32.0, step=1.0) / 100.0

st.sidebar.header("🎯 2. Engagement & Filters")

# Параметры вовлеченности аудитории
session_time = st.sidebar.slider("Длина сессии (мин):", 1, 120, value=15, step=1)
vgu_ratio = st.sidebar.slider("Доля Active Spenders (> $10) (%):", 0.1, 20.0, value=7.0, step=0.1) / 100.0
behavioral_filter = st.sidebar.slider("Эффективность фильтра (10+ мин) (%):", 1.0, 50.0, value=12.0, step=0.5) / 100.0

st.sidebar.header("💰 3. Экономика проекта")

# Параметры финансовой конверсии
base_conv = st.sidebar.slider("Базовая конверсия (%):", 0.5, 10.0, value=2.5, step=0.1) / 100.0
base_arppu = st.sidebar.slider("ARPPU (R$):", 50, 2000, value=280, step=10)

# Дополнительные настройки для финансового планирования
st.sidebar.markdown("---")
with st.sidebar.container():
    st.subheader("⚙️ Налоги и Распределение")
    devex_rate = st.sidebar.slider("Курс DevEx ($):", 0.0010, 0.0100, value=0.0035, step=0.0001, format="%.4f")
    tax_rate = st.sidebar.slider("Налог на вывод (%):", 0, 20, value=6, step=1) / 100.0
    reinvest_rate = st.sidebar.slider("Фонд развития (%):", 0, 50, value=15, step=5) / 100.0
    marketing_rate = st.sidebar.slider("Маркетинг (%):", 0, 40, value=10, step=5) / 100.0
    share = st.sidebar.slider("Доля инвестора (%):", 0, 100, value=35, step=5) / 100.0

# ==========================================
# --- ЯДРО РАСЧЕТОВ (Population Engine) ---
# ==========================================
alpha = 0.55  # Коэффициент затухания (decay)
days = np.arange(0, 30)

# Вычисление кривой удержания по формуле затухания
retention_curve = [1.0 if t == 0 else d1_input * (t ** -alpha) for t in days]

# Расчет натурального MAU как суммы накопленных уникальных игроков
natural_mau = new_users_daily * sum(retention_curve)

# Расчет текущего DAU из потока пользователей
current_dau = new_users_daily * sum(retention_curve)

# Вывод CCU через DAU и среднюю сессию
ccu = (current_dau * session_time) / 1440

# Расчет нагрузки (Required Capacity) для инвестора
required_capacity = current_dau * (30 / (1 + sum([d1_input * (t ** -alpha) for t in range(1, 30)])))

# Расчет коэффициента влияния сессии на донат
if session_time > TARGET_SESSION:
    session_mon_factor = 1.0 + ((session_time - TARGET_SESSION) / TARGET_SESSION) ** 0.6
else:
    session_mon_factor = (session_time / TARGET_SESSION) ** 1.2

# Расчет реальных метрик монетизации
real_conv = min(0.15, base_conv * (session_mon_factor ** 0.5))
real_arppu = base_arppu * (session_mon_factor ** 0.7)

# Расчет доходов от внутриигровых покупок
net_usd_donates = (current_dau * real_conv * real_arppu * (1.0 - ROBLOX_TAX)) * devex_rate

# Расчет Creator Rewards (Элитный пул Engagement)
premium_pool = current_dau * vgu_ratio
monthly_rewards_robux = (premium_pool * behavioral_filter * 30) * 6.0
engagement_rewards_usd = (monthly_rewards_robux * (1.0 - ROBLOX_TAX)) * devex_rate

# Суммирование валового дохода
total_gross_usd = net_usd_donates + engagement_rewards_usd

# Расчет чистой прибыли и выплат
total_pool = total_gross_usd * (1.0 - tax_rate - reinvest_rate - marketing_rate)
investor_payout_usd = total_pool * share if total_pool > 0 else 0
clear_profit_usd = total_pool - investor_payout_usd

# ==========================================
# --- ВИЗУАЛИЗАЦИЯ ДАННЫХ (Вывод) ---
# ==========================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Новичков в день", f"{new_users_daily:,}")
col2.metric("Натуральный MAU", f"{int(natural_mau):,}")
col3.metric("Расчетный DAU", f"{int(current_dau):,}")
col4.metric("Результат CCU", f"{int(ccu):,}")

st.markdown("---")
st.subheader("📊 Финансовая модель (в месяц)")

f1, f2, f3, f4 = st.columns(4)
f1.metric("Gross USD", f"${total_gross_usd:,.2f}")
f2.metric("Чистая прибыль", f"${clear_profit_usd:,.2f}")
f3.metric("Выплата инвестору", f"${investor_payout_usd:,.2f}")
f4.metric("Срок ROI", f"{INVESTMENT/investor_payout_usd:.1f} мес" if investor_payout_usd > 0 else "∞")

# Блок с инфой о нагрузке системы
st.info(f"ℹ️ Required Capacity (необходимая емкость для поддержания DAU): {int(required_capacity):,}")

# ==========================================
# --- ГРАФИК УДЕРЖАНИЯ ---
# ==========================================
st.markdown("---")
st.subheader("📉 Волны удержания популяции")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(days, [new_users_daily * r for r in retention_curve], color='#00ff41', linewidth=3)
ax.fill_between(days, [new_users_daily * r for r in retention_curve], color='#00ff41', alpha=0.1)
ax.set_xlabel("Дни после прихода игрока")
ax.set_ylabel("Количество активных игроков")
ax.grid(True, linestyle='--', alpha=0.3)
st.pyplot(fig)