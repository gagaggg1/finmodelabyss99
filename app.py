import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройки веб-страницы
st.set_page_config(page_title="Abyss 99 Business Model Pro", layout="wide")

st.title("🐙 Бизнес-модель: «99 Ночей в Бездне»")
st.write("Профессиональный расчет доходности. Центрировано вокруг CCU с корректным расчетом Retention.")

# Границы для ползунков
MIN_DAU, MAX_DAU = 1000, 5000000
MIN_MAU, MAX_MAU = 10000, 50000000
MIN_CCU, MAX_CCU = 10, 100000

# Фиксированные константы
ROBLOX_TAX = 0.30       # Комиссия платформы Roblox
INVESTMENT = 4500       # Стартовый капитал инвестора

# 1. Инициализация базовых параметров в памяти (session_state)
if "ccu_val" not in st.session_state: st.session_state["ccu_val"] = 500
if "session_time" not in st.session_state: st.session_state["session_time"] = 35
if "retention" not in st.session_state: st.session_state["retention"] = 10.0  # Бывший Sticky Factor

# Производные значения, которые рассчитаются автоматически
if "dau_val" not in st.session_state: st.session_state["dau_val"] = 20571
if "mau_val" not in st.session_state: st.session_state["mau_val"] = 205714

# Экономика
if "conv" not in st.session_state: st.session_state["conv"] = 2.0
if "arppu" not in st.session_state: st.session_state["arppu"] = 250
if "devex_rate" not in st.session_state: st.session_state["devex_rate"] = 0.0035
if "premium_ratio" not in st.session_state: st.session_state["premium_ratio"] = 2.5
if "reinvest_rate" not in st.session_state: st.session_state["reinvest_rate"] = 15
if "marketing_rate" not in st.session_state: st.session_state["marketing_rate"] = 10
if "tax_rate" not in st.session_state: st.session_state["tax_rate"] = 6
if "share" not in st.session_state: st.session_state["share"] = 35

# 2. МАТЕМАТИЧЕСКИЕ КОЛБЭКИ (CCU — главный источник правды)
def sync_from_ccu():
    # Из CCU и длины сессии получаем DAU (сколько человек в день нужно для такого онлайна)
    # Формула: CCU = (DAU * Session) / 1440  =>  DAU = (CCU * 1440) / Session
    sess = st.session_state["session_time"]
    dau_calc = (st.session_state["ccu_val"] * 1440) / sess if sess > 0 else 0
    st.session_state["dau_val"] = max(MIN_DAU, min(int(dau_calc), MAX_DAU))
    
    # Из полученного DAU и Retention получаем необходимый объем MAU
    # Формула: Retention = DAU / MAU  =>  MAU = DAU / Retention
    ret = st.session_state["retention"] / 100.0
    mau_calc = st.session_state["dau_val"] / ret if ret > 0 else 0
    st.session_state["mau_val"] = max(MIN_MAU, min(int(mau_calc), MAX_MAU))

def sync_from_dau():
    # Если пользователь руками меняет DAU, пересчитываем CCU и MAU
    sess = st.session_state["session_time"]
    ccu_calc = (st.session_state["dau_val"] * sess) / 1440
    st.session_state["ccu_val"] = max(MIN_CCU, min(int(ccu_calc), MAX_CCU))
    
    ret = st.session_state["retention"] / 100.0
    mau_calc = st.session_state["dau_val"] / ret if ret > 0 else 0
    st.session_state["mau_val"] = max(MIN_MAU, min(int(mau_calc), MAX_MAU))

def sync_from_mau():
    # Если пользователь руками меняет MAU, адаптируем DAU через Retention, а затем CCU
    ret = st.session_state["retention"] / 100.0
    dau_calc = st.session_state["mau_val"] * ret
    st.session_state["dau_val"] = max(MIN_DAU, min(int(dau_calc), MAX_DAU))
    
    sess = st.session_state["session_time"]
    ccu_calc = (st.session_state["dau_val"] * sess) / 1440
    st.session_state["ccu_val"] = max(MIN_CCU, min(int(ccu_calc), MAX_CCU))

# Первичный запуск синхронизации
if "init" not in st.session_state:
    sync_from_ccu()
    st.session_state["init"] = True

# Боковая панель управления
st.sidebar.header("🎛️ Настройка переменных")
input_mode = st.sidebar.radio("Режим ввода данных:", ("Ползунки", "Ввод вручную"))
st.sidebar.markdown("---")

# 3. Отрисовка интерфейса ввода
if input_mode == "Ползунки":
    st.sidebar.markdown("### 🎯 Главный показатель")
    st.sidebar.slider("Средний онлайн (CCU):", min_value=MIN_CCU, max_value=MAX_CCU, step=50, key="ccu_val", on_change=sync_from_ccu)
    
    st.sidebar.markdown("### 🕒 Удержание и Вовлеченность")
    st.sidebar.slider("Удержание игроков (Retention %):", min_value=5.0, max_value=40.0, step=0.5, format="%.1f", key="retention", on_change=sync_from_ccu)
    st.sidebar.slider("Длина сессии (минут):", min_value=5, max_value=120, step=5, key="session_time", on_change=sync_from_ccu)
    
    st.sidebar.markdown("### 👥 Зависимые метрики (Просмотр)")
    st.sidebar.slider("Игроков в день (DAU):", min_value=MIN_DAU, max_value=MAX_DAU, step=1000, key="dau_val", on_change=sync_from_dau)
    st.sidebar.slider("Игроков в месяц (MAU):", min_value=MIN_MAU, max_value=MAX_MAU, step=10000, key="mau_val", on_change=sync_from_mau)
    
    st.sidebar.markdown("### 💎 Монетизация и Экономика")
    st.sidebar.slider("Конверсия в донат (%):", min_value=0.1, max_value=10.0, step=0.1, format="%.1f", key="conv")
    st.sidebar.slider("Средний чек донатера (Robux):", min_value=10, max_value=2000, step=10, key="arppu")
    st.sidebar.slider("Курс DevEx ($ за 1 Robux):", min_value=0.0010, max_value=0.0100, step=0.0001, format="%.4f", key="devex_rate")
    st.sidebar.slider("Доля Premium игроков (%):", min_value=0.5, max_value=10.0, step=0.1, format="%.1f", key="premium_ratio")
    st.sidebar.slider("Фонд развития игры (%):", min_value=0, max_value=50, step=5, key="reinvest_rate")
    st.sidebar.slider("Маркетинг и реклама (%):", min_value=0, max_value=30, step=5, key="marketing_rate")
    st.sidebar.slider("Налог на вывод денег (%):", min_value=0, max_value=20, step=1, key="tax_rate")
    st.sidebar.slider("Доля инвестора после ROI (%):", min_value=0, max_value=100, step=5, key="share")
else:
    st.sidebar.markdown("### 🎯 Главный показатель")
    st.sidebar.number_input("Средний онлайн (CCU):", min_value=MIN_CCU, max_value=MAX_CCU, step=100, key="ccu_val", on_change=sync_from_ccu)
    
    st.sidebar.markdown("### 🕒 Удержание и Вовлеченность")
    st.sidebar.number_input("Удержание игроков (Retention %):", min_value=1.0, max_value=100.0, step=0.5, format="%.1f", key="retention", on_change=sync_from_ccu)
    st.sidebar.number_input("Длина сессии (минут):", min_value=1, max_value=240, step=5, key="session_time", on_change=sync_from_ccu)
    
    st.sidebar.markdown("### 👥 Зависимые метрики")
    st.sidebar.number_input("Игроков в день (DAU):", min_value=0, max_value=MAX_DAU, step=1000, key="dau_val", on_change=sync_from_dau)
    st.sidebar.number_input("Игроков в месяц (MAU):", min_value=0, max_value=MAX_MAU, step=10000, key="mau_val", on_change=sync_from_mau)
    
    st.sidebar.markdown("### 💎 Монетизация и Экономика")
    st.sidebar.number_input("Конверсия в донат (%):", min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="conv")
    st.sidebar.number_input("Средний чек донатера (Robux):", min_value=0, max_value=100000, step=10, key="arppu")
    st.sidebar.number_input("Курс DevEx ($ за 1 Robux):", min_value=0.0010, max_value=0.1000, step=0.0001, format="%.4f", key="devex_rate")
    st.sidebar.number_input("Доля Premium игроков (%):", min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="premium_ratio")
    st.sidebar.number_input("Фонд развития игры (%):", min_value=0, max_value=100, step=5, key="reinvest_rate")
    st.sidebar.number_input("Маркетинг и реклама (%):", min_value=0, max_value=100, step=5, key="marketing_rate")
    st.sidebar.number_input("Налог на вывод денег (%):", min_value=0, max_value=100, step=1, key="tax_rate")
    st.sidebar.number_input("Доля инвестора после ROI (%):", min_value=0, max_value=100, step=5, key="share")

# Сбор финальных значений переменных
ccu = st.session_state["ccu_val"]
retention_pct = st.session_state["retention"]
session_time = st.session_state["session_time"]
dau = st.session_state["dau_val"]
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
def usd_to_robux(usd, rate):
    return usd / rate if rate > 0 else 0

paying_users = mau * conv
gross_robux_donates = paying_users * arppu
net_usd_donates = (gross_robux_donates * (1.0 - ROBLOX_TAX)) * devex_rate

# Премиум выплаты зависят напрямую от удержания и онлайна
premium_bonus_usd = ccu * (session_time / 30.0) * (premium_ratio / 0.02)
total_gross_usd = net_usd_donates + premium_bonus_usd
total_gross_robux = usd_to_robux(total_gross_usd, devex_rate)

tax_usd = total_gross_usd * tax_rate
tax_robux = usd_to_robux(tax_usd, devex_rate)

reinvestment_usd = total_gross_usd * reinvest_rate
reinvestment_robux = usd_to_robux(reinvestment_usd, devex_rate)

marketing_usd = total_gross_usd * marketing_rate
marketing_robux = usd_to_robux(marketing_usd, devex_rate)

total_clear_profit_usd = total_gross_usd - tax_usd - reinvestment_usd - marketing_usd
total_clear_profit_robux = usd_to_robux(total_clear_profit_usd, devex_rate)

investor_payout_usd = total_clear_profit_usd * share
investor_payout_robux = usd_to_robux(investor_payout_usd, devex_rate)

arpu_usd = total_gross_usd / mau if mau > 0 else 0
arpu_robux = total_gross_robux / mau if mau > 0 else 0
ltv_usd = arpu_usd * 1.5  
ltv_robux = arpu_robux * 1.2
arpdau_usd = total_gross_usd / 30 / dau if dau > 0 else 0
arpdau_robux = total_gross_robux / 30 / dau if dau > 0 else 0

payout_step = investor_payout_usd if share > 0 else total_clear_profit_usd
roi_months = INVESTMENT / payout_step if payout_step > 0 else 99

# --- ИНТЕРФЕЙС И ВЫВОД НА ЭКРАН ---
st.subheader("🖥️ Динамические показатели аудитории")
sys_col1, sys_col2, sys_col3 = st.columns(3)
sys_col1.metric("Активный онлайн (CCU) 🔥", f"{ccu:,} чел.", help="Главная целевая метрика проекта.")
sys_col2.metric("Дневная аудитория (DAU)", f"{dau:,} чел.", f"Retention: {retention_pct}%")
sys_col3.metric("Месячная аудитория (MAU)", f"{mau:,} чел.", "Рассчитано от стабильного онлайна")

st.markdown("---")

st.subheader("💰 Финансовые итоги проекта (в месяц)")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Общий оборот", f"${total_gross_usd:,.2f}", f"R$ {int(total_gross_robux):,}")
col2.metric("Фонд обновлений", f"${reinvestment_usd:,.2f}", f"R$ {int(reinvestment_robux):,}")
col3.metric("Траты на маркетинг", f"${marketing_usd:,.2f}", f"R$ {int(marketing_robux):,}", delta_color="inverse")
col4.metric("Чистая прибыль студии", f"${total_clear_profit_usd:,.2f}", f"R$ {int(total_clear_profit_robux):,}")
col5.metric("Чистый доход инвестора", f"${investor_payout_usd:,.2f}", f"R$ {int(investor_payout_robux):,}")

st.markdown("---")

st.subheader("📊 Продуктовые метрики")
m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("Ценность игрока (LTV)", f"${ltv_usd:.4f}", f"R$ {ltv_robux:.2f}")
m_col2.metric("Доход с активного в день (ARPDAU)", f"${arpdau_usd:.4f}", f"R$ {arpdau_robux:.2f}")

if roi_months <= 1:
    m_col3.metric("Окупаемость $4,500", "1-й месяц релиза!", delta="⚡ Моментально")
else:
    m_col3.metric("Окупаемость $4,500", f"~ {roi_months:.1f} мес.", delta="После старта релиза")

st.markdown("---")

# --- ОТРИСОВКА ГРАФИКА ОКУПАЕМОСТИ ---
st.subheader("🦑 График окупаемости инвестиций (Возврат капитала)")

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

# Неоновое свечение графика
neongreen_glow = '#00ff4110' 
for n in range(1, 10):
    ax.plot(months_numeric, balance, marker='o', color=neongreen_glow, linewidth=3 + (n*1.5), markersize=8+(n), zorder=4)

# Заливка цветом зон дефицита/профицита бюджета
red_zone = '#ff1744'
ax.fill_between(months_numeric, balance, 0, where=[b<0 for b in balance], interpolate=True, color=red_zone, alpha=0.15, zorder=2)
ax.fill_between(months_numeric, balance, 0, where=[b>=0 for b in balance], interpolate=True, color=neongreen, alpha=0.15, zorder=2)

ax.axhline(0, color='#444444', linewidth=1, linestyle='--', zorder=3)
ax.grid(True, axis='y', color='#222222', linestyle='-', linewidth=0.5, alpha=0.5, zorder=1)
ax.grid(False, axis='x')

plt.xticks(months_numeric, months_full, color='#888888', fontsize=10)
plt.yticks(color='#888888', fontsize=9)
ax.set_ylabel("Капитал проекта ($)", color='#aaaaaa', fontsize=11, labelpad=10)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color('#333333')

# Триггер анимации флага окупаемости
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