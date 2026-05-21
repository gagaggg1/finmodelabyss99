import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройки веб-страницы
st.set_page_config(page_title="Abyss 99 Production-Ready Model", layout="wide")

st.title("🐙 Реалистичная бизнес-модель: «99 Ночей в Бездне» (v2.0)")
st.write("Калькулятор защищен от критических ошибок, деления на ноль и некорректных экстремальных значений ввода.")

# Константы платформы
ROBLOX_TAX = 0.30       # Комиссия платформы Roblox
INVESTMENT = 4500       # Стартовый капитал инвестора
TARGET_SESSION = 35.0  # Оптимальное время сессии для раскрытия хоррора

# --- ИНТЕРФЕЙС: БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.header("🎛️ Управление симуляцией")
input_mode = st.sidebar.radio("Режим ввода:", ("Ползунки", "Ввод вручную"))
st.sidebar.markdown("---")

if input_mode == "Ползунки":
    st.sidebar.markdown("### 🎯 Главный показатель")
    ccu = st.sidebar.slider("Средний онлайн (CCU):", 10, 50000, value=500, step=50)
    
    st.sidebar.markdown("### 🕒 Геймплей и Базовое удержание")
    session_time = st.sidebar.slider("Длина сессии (минут):", 5, 120, value=35, step=5)
    base_d1 = st.sidebar.slider("Базовый D1 Retention (% при идеальной сессии):", 10.0, 60.0, value=32.0, step=1.0)
    
    st.sidebar.markdown("### 💎 Базовая монетизация")
    base_conv = st.sidebar.slider("Базовая конверсия (%):", 0.5, 10.0, value=2.5, step=0.1) / 100.0
    base_arppu = st.sidebar.slider("Базовый чек донатера (Robux):", 50, 2000, value=280, step=10)
    devex_rate = st.sidebar.slider("Курс DevEx ($ за 1 R$):", 0.0010, 0.0100, value=0.0035, step=0.0001, format="%.4f")
    premium_ratio = st.sidebar.slider("Доля Premium игроков (%):", 0.5, 15.0, value=3.0, step=0.5) / 100.0

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Распределение бюджета и ROI")
    tax_rate = st.sidebar.slider("Налог на вывод денег (%):", 0, 20, value=6, step=1) / 100.0
    reinvest_rate = st.sidebar.slider("Фонд развития игры (%):", 0, 50, value=15, step=5) / 100.0
    marketing_rate = st.sidebar.slider("Маркетинг и реклама (%):", 0, 40, value=10, step=5) / 100.0
    share = st.sidebar.slider("Доля инвестора после ROI (%):", 0, 100, value=35, step=5) / 100.0
else:
    st.sidebar.markdown("### 🎯 Главный показатель")
    ccu = st.sidebar.number_input("Средний онлайн (CCU):", min_value=0, max_value=100000, value=500, step=100)
    st.sidebar.markdown("### 🕒 Геймплей")
    session_time = st.sidebar.number_input("Длина сессии (минут):", min_value=0, max_value=240, value=35, step=5)
    base_d1 = st.sidebar.number_input("Базовый D1 Retention (%):", min_value=0.0, max_value=100.0, value=32.0, step=1.0)
    st.sidebar.markdown("### 💎 Монетизация")
    base_conv = st.sidebar.number_input("Базовая конверсия (%):", min_value=0.0, max_value=100.0, value=2.5, step=0.1) / 100.0
    base_arppu = st.sidebar.number_input("Базовый чек донатера (Robux):", min_value=0, max_value=100000, value=280, step=50)
    devex_rate = st.sidebar.number_input("Курс DevEx ($ за 1 R$):", min_value=0.0000, max_value=0.0100, value=0.0035, step=0.0001, format="%.4f")
    premium_ratio = st.sidebar.number_input("Доля Premium игроков (%):", min_value=0.0, max_value=100.0, value=3.0, step=0.5) / 100.0

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Распределение бюджета и ROI")
    tax_rate = st.sidebar.number_input("Налог на вывод денег (%):", min_value=0, max_value=100, value=6, step=1) / 100.0
    reinvest_rate = st.sidebar.number_input("Фонд развития игры (%):", min_value=0, max_value=100, value=15, step=5) / 100.0
    marketing_rate = st.sidebar.number_input("Маркетинг и реклама (%):", min_value=0, max_value=100, value=10, step=5) / 100.0
    share = st.sidebar.number_input("Доля инвестора после ROI (%):", min_value=0, max_value=100, value=35, step=5) / 100.0


# --- ЯДРО ДИНАМИЧЕСКИХ МАТЕМАТИЧЕСКИХ ЗАВИСИМОСТЕЙ ---

# 1. Зависимость Retention от Длины Сессии (Штраф за короткую игру)
if session_time < TARGET_SESSION:
    # Защита от деления на ноль при сессии = 0
    retention_factor = (session_time / TARGET_SESSION) ** 2 if session_time > 0 else 0
else:
    retention_factor = min(1.15, 1.0 + (session_time - TARGET_SESSION) / 200.0)

# Реальный расчет кривой Retention на основе качества сессии
d1 = max(0.0, min(base_d1 * retention_factor, 75.0))
alpha = 0.55  # Степень затухания интереса аудитории
d7 = d1 * (7 ** -alpha)
d30 = d1 * (30 ** -alpha)

# Сколько дней в течение месяца играет средний вернувшийся юзер (Lifetime)
player_lifetime_days = 1 + sum([ (d1/100.0) * (t ** -alpha) for t in range(2, 31)])

# 2. Пересчет Трафика от CCU и Сессии
dau = (ccu * 1440) / session_time if session_time > 0 else 0
mau = dau * (30 / player_lifetime_days) if player_lifetime_days > 0 else 0

# 3. Зависимость Монетизации от Вовлечения (Штраф за «пятиминутки»)
session_mon_factor = max(0.02, min(1.0, session_time / TARGET_SESSION)) if TARGET_SESSION > 0 else 0.02
retention_mon_factor = max(0.1, min(1.0, d1 / base_d1)) if base_d1 > 0 else 0.1

# Итоговые скорректированные показатели монетизации
real_conv = base_conv * session_mon_factor * retention_mon_factor
real_arppu = base_arppu * session_mon_factor

# --- ФИНАНСОВЫЙ РАСЧЕТ ---

# Донаты
daily_paying_users = dau * real_conv
monthly_paying_users = daily_paying_users * player_lifetime_days
gross_robux_donates = monthly_paying_users * real_arppu

# Премиум-выплаты
total_premium_minutes_monthly = (dau * premium_ratio) * session_time * 30
premium_bonus_usd = total_premium_minutes_monthly * 0.00015 * (d1 / 100.0)
premium_bonus_robux_equivalent = premium_bonus_usd / devex_rate if devex_rate > 0 else 0

# Итоги Gross
total_gross_robux = gross_robux_donates + (premium_bonus_robux_equivalent / (1.0 - ROBLOX_TAX))
net_usd_donates = (gross_robux_donates * (1.0 - ROBLOX_TAX)) * devex_rate
total_gross_usd = net_usd_donates + premium_bonus_usd

# --- РАСПРЕДЕЛЕНИЕ БЮДЖЕТА И ЧИСТАЯ ПРИБЫЛЬ ---
tax_usd = total_gross_usd * tax_rate
reinvestment_usd = total_gross_usd * reinvest_rate
marketing_usd = total_gross_usd * marketing_rate

total_pool_before_payout = total_gross_usd - tax_usd - reinvestment_usd - marketing_usd

if total_pool_before_payout > 0:
    investor_payout_usd = total_pool_before_payout * share
    total_clear_profit_usd = total_pool_before_payout - investor_payout_usd
else:
    investor_payout_usd = 0.0
    total_clear_profit_usd = total_pool_before_payout 

investor_payout_robux = investor_payout_usd / devex_rate if devex_rate > 0 else 0
total_clear_profit_robux = total_clear_profit_usd / devex_rate if devex_rate > 0 else 0

# Окупаемость
roi_months = INVESTMENT / investor_payout_usd if investor_payout_usd > 0 else 99

# Продуктовые метрики на одного пользователя
arpu_usd = total_gross_usd / mau if mau > 0 else 0
arpu_robux = total_gross_robux / mau if mau > 0 else 0
ltv_usd = arpu_usd * (1 + (player_lifetime_days / 30.0))
ltv_robux = arpu_robux * (1 + (player_lifetime_days / 30.0))
arpdau_usd = total_gross_usd / 30 / dau if dau > 0 else 0
arpdau_robux = total_gross_robux / 30 / dau if dau > 0 else 0


# --- ИНТЕРФЕЙСНЫЙ ВЫВОД ДАННЫХ ---

st.subheader("🖥️ Метрики вовлеченности и удержания аудитории")
sys_col1, sys_col2, sys_col3 = st.columns(3)
sys_col1.metric("Заданный онлайн (CCU) 🔥", f"{int(ccu):,} чел.", "Главный ориентир")
sys_col2.metric("Дневной поток (DAU) 👥", f"{int(dau):,} чел.", f"Сессия: {session_time} мин.")
sys_col3.metric("Месячный охват (MAU) 🌐", f"{int(mau):,} чел.", f"Коэф. удержания базы: {int((dau/mau)*100) if mau > 0 else 0}%")

st.markdown("##### Реальное состояние воронки удержания (с учетом длины сессии):")
r_col1, r_col2, r_col3, r_col4 = st.columns(4)
r_col1.info(f"**D1 Retention:** {d1:.1f}%  \n*Эффект первого захода*")
r_col2.info(f"**D7 Retention:** {d7:.1f}%  \n*Интерес к контенту*")
r_col3.info(f"**D30 Retention:** {d30:.1f}%  \n*Формирование привычки*")
r_col4.success(f"**Активных дней в месяц:**  \n⚡ **{player_lifetime_days:.2f} дн.**")

st.markdown("---")

st.subheader("💰 Экономика монетизации (С поправкой на качество сессии)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Реальная Конверсия в донат", f"{real_conv*100:.2f}%", f"Базовая: {base_conv*100:.1f}%")
m2.metric("Реальный чек донатера", f"R$ {int(real_arppu):,}", f"Базовый: R$ {base_arppu}")
m3.metric("Ценность игрока (LTV)", f"${ltv_usd:.4f}", f"R$ {ltv_robux:.2f}")
m4.metric("Метрика ARPDAU", f"${arpdau_usd:.4f}", f"R$ {arpdau_robux:.2f}")

st.markdown("---")

st.subheader("📊 Распределение чистой прибыли и Финансы (в месяц)")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Общий Gross оборот плейса", f"${total_gross_usd:,.2f}", f"R$ {int(total_gross_robux):,}")
col2.metric("Налоги и комиссии вывода", f"${tax_usd:,.2f}", f"R$ {int(tax_usd / devex_rate) if devex_rate > 0 else 0:,}", delta_color="inverse")
col3.metric("Фонд развития (Реинвест)", f"${reinvestment_usd:,.2f}", f"R$ {int(reinvestment_usd / devex_rate) if devex_rate > 0 else 0:,}")
col4.metric("Чистая прибыль студии", f"${total_clear_profit_usd:,.2f}", f"R$ {int(total_clear_profit_robux):,}")
col5.metric("Доход инвестора", f"${investor_payout_usd:,.2f}", f"R$ {int(investor_payout_robux):,}")

st.markdown("---")

# График окупаемости
st.subheader("📈 График возврата инвестиций ($4,500)")

plt.style.use('dark_background') 
fig, ax = plt.subplots(figsize=(12, 4), dpi=120)

months_labels = ['M1 (Dev)', 'M2 (Dev)', 'M3 (Test)', 'M4 (Релиз)', 'M5', 'M6']
months_num = np.array([1, 2, 3, 4, 5, 6])

# Честный расчет баланса без забегания вперед по ROI
balance = np.array([
    -INVESTMENT,
    -INVESTMENT,
    -INVESTMENT,
    -INVESTMENT,                       # M4 (Релиз) — точка старта без мгновенной выплаты
    -INVESTMENT + investor_payout_usd, # M5 — конец 1-го месяца окупаемости
    -INVESTMENT + (investor_payout_usd * 2)
])

# Отрисовка неонового графика
ax.plot(months_num, balance, marker='o', color='#00ff41', linewidth=3, markersize=8, zorder=5)
for n in range(1, 8):
    ax.plot(months_num, balance, marker='o', color='#00ff4110', linewidth=3 + (n*1.5), markersize=8+n, zorder=4)

ax.fill_between(months_num, balance, 0, where=[b<0 for b in balance], color='#ff1744', alpha=0.1, zorder=2)
ax.fill_between(months_num, balance, 0, where=[b>=0 for b in balance], color='#00ff41', alpha=0.1, zorder=2)
ax.axhline(0, color='#444444', linewidth=1, linestyle='--', zorder=3)

plt.xticks(months_num, months_labels, color='#888888')
plt.yticks(color='#888888')
ax.set_ylabel("Баланс инвестора ($)", color='#aaaaaa')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

# Безопасная проверка на существование точки окупаемости на графике
if investor_payout_usd > 0 and not all(b < 0 for b in balance):
    positive_indices = np.where(balance >= 0)[0]
    if len(positive_indices) > 0:
        idx = positive_indices[0]
        ax.scatter(months_num[idx], balance[idx], color='#00ff41', s=150, marker='H', zorder=10)
        ax.annotate('ROI ПОЛУЧЕН! 🎉', xy=(months_num[idx], balance[idx]), xytext=(months_num[idx], balance[idx] + (INVESTMENT*0.1)),
                    color='#ffffff', fontsize=10, fontweight='bold', horizontalalignment='center',
                    arrowprops=dict(arrowstyle='->', color='#aaaaaa'))

st.pyplot(fig)