import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройки веб-страницы
st.set_page_config(page_title="Abyss 99 Business Model Pro", layout="wide")

st.title("🐙 Бизнес-модель: «99 Ночей в Бездне» (Исправленная версия)")
st.write("Логика перестроена: базой расчетов является трафик (DAU). Длина сессии теперь адекватно растит онлайн и доход.")

# Границы для ползунков аудитории
MIN_DAU, MAX_DAU = 1000, 5000000
MIN_MAU, MAX_MAU = 10000, 50000000
MIN_CCU, MAX_CCU = 10, 100000

# Фиксированные константы
ROBLOX_TAX = 0.30       # Комиссия платформы Roblox
INVESTMENT = 4500       # Стартовый капитал инвестора

# 1. Инициализация базовых параметров в памяти (session_state)
if "dau_val" not in st.session_state: st.session_state["dau_val"] = 25000 # Теперь DAU — главная база
if "session_time" not in st.session_state: st.session_state["session_time"] = 35
if "retention_d1" not in st.session_state: st.session_state["retention_d1"] = 30.0  # Базовый D1

# Производные значения, которые рассчитаются автоматически
if "ccu_val" not in st.session_state: st.session_state["ccu_val"] = 607
if "mau_val" not in st.session_state: st.session_state["mau_val"] = 250000

# Экономика
if "conv" not in st.session_state: st.session_state["conv"] = 2.0
if "arppu" not in st.session_state: st.session_state["arppu"] = 250
if "devex_rate" not in st.session_state: st.session_state["devex_rate"] = 0.0035
if "premium_ratio" not in st.session_state: st.session_state["premium_ratio"] = 2.5
if "reinvest_rate" not in st.session_state: st.session_state["reinvest_rate"] = 15
if "marketing_rate" not in st.session_state: st.session_state["marketing_rate"] = 10
if "tax_rate" not in st.session_state: st.session_state["tax_rate"] = 6
if "share" not in st.session_state: st.session_state["share"] = 35

# 2. МАТЕМАТИЧЕСКИЕ КОЛБЭКИ И ЗАВИСИМОСТИ RETENTION
def calculate_retention_curve(d1_pct):
    """Рассчитывает D7 и D30 на основе D1, используя степенной закон затухания (Power Law)"""
    r1 = d1_pct / 100.0
    if r1 <= 0:
        return 0.0, 0.0, 0.0
    
    alpha = 0.55 # Коэффициент затухания удержания
    r7 = r1 * (7 ** -alpha)
    r30 = r1 * (30 ** -alpha)
    
    # Интеграл кривой удержания за 30 дней (сколько дней внутри месяца живет средний игрок)
    lifetime_days = 1 + sum([r1 * (t ** -alpha) for t in range(2, 31)])
    return r7 * 100.0, r30 * 100.0, lifetime_days

def sync_from_dau():
    """Пересчет CCU и MAU на основе заданного DAU (Правильная логика)"""
    sess = st.session_state["session_time"]
    # CCU зависит от DAU и длины сессии: больше сессия -> выше онлайн при том же трафике
    ccu_calc = (st.session_state["dau_val"] * sess) / 1440
    st.session_state["ccu_val"] = max(MIN_CCU, min(int(ccu_calc), MAX_CCU))
    
    _, _, lifetime = calculate_retention_curve(st.session_state["retention_d1"])
    # MAU рассчитывается через коэффициент накопления базы игроков
    mau_calc = st.session_state["dau_val"] * (30 / lifetime) if lifetime > 0 else st.session_state["dau_val"] * 10
    st.session_state["mau_val"] = max(MIN_MAU, min(int(mau_calc), MAX_MAU))

def sync_from_ccu():
    """Если пользователь решил изменить CCU напрямую"""
    sess = st.session_state["session_time"]
    dau_calc = (st.session_state["ccu_val"] * 1440) / sess if sess > 0 else 0
    st.session_state["dau_val"] = max(MIN_DAU, min(int(dau_calc), MAX_DAU))
    
    _, _, lifetime = calculate_retention_curve(st.session_state["retention_d1"])
    mau_calc = st.session_state["dau_val"] * (30 / lifetime) if lifetime > 0 else st.session_state["dau_val"] * 10
    st.session_state["mau_val"] = max(MIN_MAU, min(int(mau_calc), MAX_MAU))

def sync_from_mau():
    """Если пользователь решил изменить MAU напрямую"""
    _, _, lifetime = calculate_retention_curve(st.session_state["retention_d1"])
    dau_calc = st.session_state["mau_val"] / (30 / lifetime) if lifetime > 0 else st.session_state["mau_val"] / 10
    st.session_state["dau_val"] = max(MIN_DAU, min(int(dau_calc), MAX_DAU))
    
    sess = st.session_state["session_time"]
    ccu_calc = (st.session_state["dau_val"] * sess) / 1440
    st.session_state["ccu_val"] = max(MIN_CCU, min(int(ccu_calc), MAX_CCU))

if "init" not in st.session_state:
    sync_from_dau()
    st.session_state["init"] = True

# Динамически получаем связанные значения удержания для расчетов
d1 = st.session_state["retention_d1"]
d7, d30, player_lifetime = calculate_retention_curve(d1)

# Панель управления
st.sidebar.header("🎛️ Настройка переменных")
input_mode = st.sidebar.radio("Режим ввода данных:", ("Ползунки", "Ввод вручную"))
st.sidebar.markdown("---")

if input_mode == "Ползунки":
    st.sidebar.markdown("### 🎯 Главный показатель (База)")
    st.sidebar.slider("Игроков в день (DAU):", min_value=MIN_DAU, max_value=MAX_DAU, step=1000, key="dau_val", on_change=sync_from_dau)
    
    st.sidebar.markdown("### 🕒 Вовлеченность и Удержание")
    st.sidebar.slider("Длина сессии (минут):", min_value=5, max_value=120, step=5, key="session_time", on_change=sync_from_dau)
    st.sidebar.slider("D1 Retention (Удержание 1-го дня %):", min_value=10.0, max_value=60.0, step=1.0, format="%.1f", key="retention_d1", on_change=sync_from_dau)
    
    st.sidebar.info(f"📋 **Рассчитанные метрики удержания:**\n* **D7 (Weekly):** {d7:.1f}%\n* **D30 (Monthly):** {d30:.1f}%\n* **Lifetime (Дней в игре):** {player_lifetime:.2f} дн.")
    
    st.sidebar.markdown("### 👥 Зависимые метрики (Просмотр)")
    st.sidebar.slider("Средний онлайн (CCU):", min_value=MIN_CCU, max_value=MAX_CCU, step=50, key="ccu_val", on_change=sync_from_ccu)
    st.sidebar.slider("Игроков в месяц (MAU):", min_value=MIN_MAU, max_value=MAX_MAU, step=10000, key="mau_val", on_change=sync_from_mau)
    
    st.sidebar.markdown("### 💎 Монетизация")
    st.sidebar.slider("Конверсия в донат (%):", min_value=0.1, max_value=10.0, step=0.1, format="%.1f", key="conv")
    st.sidebar.slider("Средний чек донатера (Robux):", min_value=10, max_value=2000, step=10, key="arppu")
    st.sidebar.slider("Курс DevEx ($ за 1 Robux):", min_value=0.0010, max_value=0.0100, step=0.0001, format="%.4f", key="devex_rate")
    st.sidebar.slider("Доля Premium игроков (%):", min_value=0.5, max_value=10.0, step=0.1, format="%.1f", key="premium_ratio")
    st.sidebar.slider("Фонд развития игры (%):", min_value=0, max_value=50, step=5, key="reinvest_rate")
    st.sidebar.slider("Маркетинг и реклама (%):", min_value=0, max_value=30, step=5, key="marketing_rate")
    st.sidebar.slider("Налог на вывод денег (%):", min_value=0, max_value=20, step=1, key="tax_rate")
    st.sidebar.slider("Доля инвестора после ROI (%):", min_value=0, max_value=100, step=5, key="share")
else:
    st.sidebar.markdown("### 🎯 Главный показатель (База)")
    st.sidebar.number_input("Игроков в день (DAU):", min_value=0, max_value=MAX_DAU, step=1000, key="dau_val", on_change=sync_from_dau)
    st.sidebar.markdown("### 🕒 Вовлеченность")
    st.sidebar.number_input("Длина сессии (минут):", min_value=1, max_value=240, step=5, key="session_time", on_change=sync_from_dau)
    st.sidebar.number_input("D1 Retention (Удержание 1-го дня %):", min_value=1.0, max_value=100.0, step=0.5, format="%.1f", key="retention_d1", on_change=sync_from_dau)
    st.sidebar.info(f"📋 **Зависимые метрики:**\n* **D7 (Weekly):** {d7:.1f}%\n* **D30 (Monthly):** {d30:.1f}%\n* **Lifetime:** {player_lifetime:.2f} дн.")
    st.sidebar.markdown("### 👥 Зависимые метрики")
    st.sidebar.number_input("Средний онлайн (CCU):", min_value=MIN_CCU, max_value=MAX_CCU, step=100, key="ccu_val", on_change=sync_from_ccu)
    st.sidebar.number_input("Игроков в месяц (MAU):", min_value=0, max_value=MAX_MAU, step=10000, key="mau_val", on_change=sync_from_mau)
    st.sidebar.markdown("### 💎 Монетизация")
    st.sidebar.number_input("Конверсия в донат (%):", min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="conv")
    st.sidebar.number_input("Средний чек донатера (Robux):", min_value=0, max_value=100000, step=10, key="arppu")
    st.sidebar.number_input("Курс DevEx ($ за 1 Robux):", min_value=0.0010, max_value=0.1000, step=0.0001, format="%.4f", key="devex_rate")
    st.sidebar.number_input("Доля Premium игроков (%):", min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="premium_ratio")
    st.sidebar.number_input("Фонд развития игры (%):", min_value=0, max_value=100, step=5, key="reinvest_rate")
    st.sidebar.number_input("Маркетинг и реклама (%):", min_value=0, max_value=100, step=5, key="marketing_rate")
    st.sidebar.number_input("Налог на вывод денег (%):", min_value=0, max_value=100, step=1, key="tax_rate")
    st.sidebar.number_input("Доля инвестора после ROI (%):", min_value=0, max_value=100, step=5, key="share")

dau = st.session_state["dau_val"]
ccu = st.session_state["ccu_val"]
session_time = st.session_state["session_time"]
mau = st.session_state["mau_val"]

conv = float(st.session_state["conv"]) / 100.0
arppu = st.session_state["arppu"]
devex_rate = st.session_state["devex_rate"]
premium_ratio = float(st.session_state["premium_ratio"]) / 100.0
reinvest_rate = float(st.session_state["reinvest_rate"]) / 100.0
marketing_rate = float(st.session_state["marketing_rate"]) / 100.0
tax_rate = float(st.session_state["tax_rate"]) / 100.0
share = float(st.session_state["share"]) / 100.0

# --- РАСЧЕТЫ ЭКОНОМИКИ ДОХОДОВ ---
# 1. Донаты (Gamepasses / Developer Products)
daily_paying_users = dau * conv
monthly_transaction_volume = daily_paying_users * 30 * (1 + (d30 / 100.0)) 
gross_robux_donates = monthly_transaction_volume * arppu

# 2. Roblox Premium Payouts (Engagement-Based)
# Считается от суммарных минут, которые Premium-игроки провели в игре за месяц.
total_premium_minutes_monthly = (dau * premium_ratio) * session_time * 30
# Примерная ставка Roblox: ~0.00015 $ за минуту премиум-времени (зависит от региона, берем среднее)
premium_bonus_usd = total_premium_minutes_monthly * 0.00015 * (1 + (d7 / 100.0))
premium_bonus_robux_equivalent = premium_bonus_usd / devex_rate if devex_rate > 0 else 0

# Общий Gross оборот с учетом налога платформы на чистые покупки
total_gross_robux = gross_robux_donates + (premium_bonus_robux_equivalent / (1.0 - ROBLOX_TAX))

# Конвертация донатов в USD с учетом 30% комиссии Roblox
net_usd_donates = (gross_robux_donates * (1.0 - ROBLOX_TAX)) * devex_rate
total_gross_usd = net_usd_donates + premium_bonus_usd

# --- РАСЧЕТЫ РАСХОДОВ И ЧИСТОЙ ПРИБЫЛИ ---
tax_usd = total_gross_usd * tax_rate
reinvestment_usd = total_gross_usd * reinvest_rate
marketing_usd = total_gross_usd * marketing_rate

total_pool_before_payout = total_gross_usd - tax_usd - reinvestment_usd - marketing_usd

investor_payout_usd = total_pool_before_payout * share
investor_payout_robux = investor_payout_usd / devex_rate if devex_rate > 0 else 0

total_clear_profit_usd = total_pool_before_payout - investor_payout_usd
total_clear_profit_robux = total_clear_profit_usd / devex_rate if devex_rate > 0 else 0

payout_step = investor_payout_usd
roi_months = INVESTMENT / payout_step if payout_step > 0 else 99

# --- ПРОДУКТОВЫЕ МЕТРИКИ ---
arpu_usd = total_gross_usd / mau if mau > 0 else 0
arpu_robux = total_gross_robux / mau if mau > 0 else 0

# LTV привязан к времени жизни игрока в игре
lifetime_months = player_lifetime / 30.0
ltv_usd = arpu_usd * (1 + lifetime_months)  
ltv_robux = arpu_robux * (1 + lifetime_months)

arpdau_usd = total_gross_usd / 30 / dau if dau > 0 else 0
arpdau_robux = total_gross_robux / 30 / dau if dau > 0 else 0

# --- ИНТЕРФЕЙС И ВЫВОД НА ЭКРАН ---
st.subheader("🖥️ Мониторинг вовлеченности аудитории")
sys_col1, sys_col2, sys_col3 = st.columns(3)
sys_col1.metric("Дневная аудитория (DAU) 👥", f"{dau:,} чел.", "Главная база расчетов")
sys_col2.metric("Средний онлайн (CCU) 🔥", f"{ccu:,} чел.", f"При сессии в {session_time} мин.")
sys_col3.metric("Месячная аудитория (MAU)", f"{mau:,} чел.", f"Ежемесячный Sticky Factor: {int((dau/mau)*100) if mau > 0 else 0}%")

st.markdown("##### Текущее состояние воронки удержания:")
r_col1, r_col2, r_col3, r_col4 = st.columns(4)
r_col1.info(f"**D1 (Daily):** {d1:.1f}%  \n*Первое впечатление*")
r_col2.info(f"**D7 (Weekly):** {d7:.1f}%  \n*Глубина контента*")
r_col3.info(f"**D30 (Monthly):** {d30:.1f}%  \n*Эндгейм и привычка*")
r_col4.success(f"**Игрок живет в игре:**  \n⚡ **{player_lifetime:.2f} дней** за месяц")

st.markdown("---")

st.subheader("💰 Финансовые итоги проекта (в месяц)")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Общий оборот (Gross)", f"${total_gross_usd:,.2f}", f"R$ {int(total_gross_robux):,}")
col2.metric("Фонд обновлений", f"${reinvestment_usd:,.2f}", f"R$ {int(reinvestment_usd / devex_rate):,}")
col3.metric("Траты на маркетинг", f"${marketing_usd:,.2f}", f"R$ {int(marketing_usd / devex_rate):,}", delta_color="inverse")
col4.metric("Чистая прибыль студии", f"${total_clear_profit_usd:,.2f}", f"R$ {int(total_clear_profit_robux):,}")
col5.metric("Чистый доход инвестора", f"${investor_payout_usd:,.2f}", f"R$ {int(investor_payout_robux):,}")

st.markdown("---")

st.subheader("📊 Продуктовые метрики")
m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("Ценность игрока (LTV)", f"${ltv_usd:.4f}", f"R$ {ltv_robux:.2f}", help="Динамически масштабируется от Lifetime игрока.")
m_col2.metric("Доход с активного в день (ARPDAU)", f"${arpdau_usd:.4f}", f"R$ {arpdau_robux:.2f}")

if roi_months <= 1:
    m_col3.metric("Окупаемость $4,500", "1-й месяц релиза!", delta="⚡ Моментально")
else:
    m_col3.metric("Окупаемость $4,500", f"~ {roi_months:.1f} мес.", delta="После старта релиза")

st.markdown("---")

# --- ОТРИСОВКА ГРАФИКА ОКУПАЕМОСТИ ---
st.subheader("Squid График окупаемости инвестиций (Возврат капитала)")

plt.style.use('dark_background') 
fig, ax = plt.subplots(figsize=(12, 4.5), dpi=120)

months_full = ['M1 (Dev)', 'M2 (Dev)', 'M3 (Test)', 'M4 (Релиз)', 'M5', 'M6']
months_numeric = np.array([1, 2, 3, 4, 5, 6])

balance = np.array([
    -INVESTMENT,
    -INVESTMENT,
    -INVESTMENT,
    -INVESTMENT + payout_step,
    -INVESTMENT + (payout_step * 2),
    -INVESTMENT + (payout_step * 3)
])

neongreen = '#00ff41' 
line, = ax.plot(months_numeric, balance, marker='o', color=neongreen, linewidth=3, markersize=8, label="Текущий капитал", zorder=5)

neongreen_glow = '#00ff4110' 
for n in range(1, 10):
    ax.plot(months_numeric, balance, marker='o', color=neongreen_glow, linewidth=3 + (n*1.5), markersize=8+(n), zorder=4)

red_zone = '#ff1744'
ax.fill_between(months_numeric, balance, 0, where=[b<0 for b in balance], interpolate=True, color=red_zone, alpha=0.15, zorder=2)
ax.fill_between(months_numeric, balance, 0, where=[b>=0 for b in balance], interpolate=True, color=neongreen, alpha=0.15, zorder=2)

ax.axhline(0, color='#444444', linewidth=1, linestyle='--', zorder=3)
ax.grid(True, axis='y', color='#222222', linestyle='-', linewidth=0.5, alpha=0.5, zorder=1)

plt.xticks(months_numeric, months_full, color='#888888', fontsize=10)
plt.yticks(color='#888888', fontsize=9)
ax.set_ylabel("Капитал проекта ($)", color='#aaaaaa', fontsize=11, labelpad=10)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color('#333333')

if payout_step > 0 and not all(b < 0 for b in balance):
    breakeven_idx = np.where(balance >= 0)[0]
    if len(breakeven_idx) > 0:
        idx = breakeven_idx[0]
        ax.scatter(months_numeric[idx], balance[idx], color=neongreen, s=200, marker='H', edgecolor='#ffffff', linewidth=1.5, zorder=10)
        for n in range(1, 15):
            ax.scatter(months_numeric[idx], balance[idx], color=neongreen_glow, s=200 + (n*15), marker='H', zorder=9)
        
        p_mon = months_numeric[idx]
        p_bal = balance[idx]
        ax.annotate('ROI ПОЛУЧЕН! 🎉', xy=(p_mon, p_bal), xytext=(p_mon, p_bal + 500),
                    textcoords='data', color='#ffffff', fontsize=11, fontweight='bold',
                    arrowprops=dict(arrowstyle='-', color='#aaaaaa', connectionstyle="arc3,rad=-0.1"),
                    horizontalalignment='center', zorder=11)

st.pyplot(fig)