import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройка страницы
st.set_page_config(
    page_title="Roblox Horror Game Economics Simulator",
    page_icon="🦑",
    layout="wide"
)

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

st.title("🦑 Deep Water Horror: Экономический Симулятор")
st.caption("Полная бизнес-модель и симуляция LTV/ROI для Roblox проекта")

# --- ИНИЦИАЛИЗАЦИЯ STATE (ВСЕ ТВОИ ПЕРЕМЕННЫЕ) ---
if "ccu_val" not in st.session_state: st.session_state["ccu_val"] = 500
if "dau_val" not in st.session_state: st.session_state["dau_val"] = 24000
if "mau_val" not in st.session_state: st.session_state["mau_val"] = 360000

# Функции синхронизации (теперь используют базовую сессию для связи, чтобы не ломать трафик)
def sync_from_ccu():
    sess = st.session_state["sess_val"] if "sess_val" in st.session_state else 45.0
    # Считаем базовый DAU от CCU через фиксированную базу в 30 мин, чтобы рост сессии не ронял игроков
    st.session_state["dau_val"] = int((st.session_state["ccu_val"] * 1440) / 30.0)
    st.session_state["mau_val"] = int(st.session_state["dau_val"] * 15)

def sync_from_dau():
    sess = st.session_state["sess_val"] if "sess_val" in st.session_state else 45.0
    st.session_state["ccu_val"] = int((st.session_state["dau_val"] * 30.0) / 1440)
    st.session_state["mau_val"] = int(st.session_state["dau_val"] * 15)

def sync_from_mau():
    st.session_state["dau_val"] = int(st.session_state["mau_val"] / 15)
    st.session_state["ccu_val"] = int((st.session_state["dau_val"] * 30.0) / 1440)

# --- ИНТЕРФЕЙС: ТРИ КОЛОНКИ НАСТРОЕК ---
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    st.subheader("🛸 Трафик и Удержание")
    ccu = st.number_input("Средний онлайн (CCU)", min_value=1, max_value=100000, key="ccu_val", on_change=sync_from_ccu)
    dau = st.number_input("Суточный охват (DAU)", min_value=1, max_value=10000000, key="dau_val", on_change=sync_from_dau)
    mau = st.number_input("Месячный охват (MAU)", min_value=1, max_value=100000000, key="mau_val", on_change=sync_from_mau)
    
    session_time = st.slider("Длина сессии (минут)", 10.0, 180.0, 45.0, step=5.0, key="sess_val")
    
    d1 = st.slider("Day 1 Retention (%)", 0.0, 100.0, 35.0, step=1.0)
    # Степенной закон затухания для D7 и D30
    alpha = -np.log(d1/100.0)/np.log(2) if d1 > 0 else 1.0
    pred_d7 = float(np.clip((d1/100.0)*(7**-alpha)*100, 0.0, d1)) if d1 > 0 else 10.0
    pred_d30 = float(np.clip((d1/100.0)*(30**-alpha)*100, 0.0, pred_d7)) if d1 > 0 else 2.0
    
    d7 = st.slider("Day 7 Retention (%)", 0.0, 100.0, pred_d7, step=0.5)
    d30 = st.slider("Day 30 Retention (%)", 0.0, 100.0, pred_d30, step=0.1)

with col_in2:
    st.subheader("💰 Монетизация и Premium")
    conv = st.slider("Конверсия в донат (%)", 0.0, 100.0, 2.5, step=0.1)
    arppu = st.number_input("Средний чек платящего (ARPPU в Robux)", 1, 100000, 450)
    premium_share = st.slider("Доля Premium-игроков (%)", 0.0, 100.0, 15.0, step=0.5)
    robux_per_min = st.number_input("Выплата за Premium-минуту (Robux)", 0.00001, 0.01, 0.00015, format="%.5f")
    
    st.subheader("📊 Налоги и Платформа")
    roblox_tax = st.slider("Комиссия Roblox на донаты (%)", 0, 100, 30)
    devex_rate = st.number_input("Курс DevEx ($ за 1 Robux)", 0.0001, 0.01, 0.0035, format="%.4f")

with col_in3:
    st.subheader("🤝 Инвестиции и Распределение")
    investment = st.number_input("Сумма инвестиций ($)", 0, 1000000, 7000)
    investor_share = st.slider("Доля инвестора в прибыли (%)", 0, 100, 35)
    reinvest_share = st.slider("Процент на реинвестирование (%)", 0, 100, 20)
    team_share = st.slider("Доля команды (от остатка, %)", 0, 100, 100)
    
    st.subheader("📉 Постоянные расходы")
    monthly_costs = st.number_input("Фиксированные расходы в месяц ($)", 0, 50000, 500)

# --- МАТЕМАТИЧЕСКИЙ РАСЧЕТ С ТВОИМИ ПЕРЕМЕННЫМИ ---

# Рост длины сессии относительно базовой (30 мин) увеличивает вовлечение
base_session = 30.0
session_factor = session_time / base_session

# Монетизация растет от длины сессии (больше времени — выше шанс покупки и чек)
dynamic_conv = min((conv / 100.0) * (session_factor ** 0.5), 1.0)
dynamic_arppu = arppu * (session_factor ** 0.7)

# 1. Расчет внутриигровых донатов
daily_paying_users = dau * dynamic_conv
gross_robux_donates = daily_paying_users * 30 * (1 + (d30 / 100.0)) * dynamic_arppu
net_robux_donates = gross_robux_donates * (1 - roblox_tax / 100.0)

# 2. Расчет Premium-выплат (на них налог 30% не распространяется)
total_engagement_minutes_monthly = dau * 30 * session_time
premium_minutes_monthly = total_engagement_minutes_monthly * (premium_share / 100.0)
# Добавляем твою логику зависимости премиума от удержания D7
dynamic_premium_rate = robux_per_min * (1 + (d7 / 100.0))
gross_robux_premium = premium_minutes_monthly * dynamic_premium_rate
net_robux_premium = gross_robux_premium  # Чистые выплаты платформы

# 3. Перевод в фиат ($)
donate_usd = net_robux_donates * devex_rate
premium_usd = net_robux_premium * devex_rate
total_net_developer_usd = donate_usd + premium_usd

# 4. Расчет чистой прибыли с учетом постоянных затрат
net_profit_after_costs = max(0.0, total_net_developer_usd - monthly_costs)

# 5. Распределение по твоим долям
investor_payout = net_profit_after_costs * (investor_share / 100.0)
pool_after_investor = net_profit_after_costs - investor_payout

reinvest_pool = pool_after_investor * (reinvest_share / 100.0)
pool_after_reinvest = pool_after_investor - reinvest_pool

studio_profit = pool_after_reinvest * (team_share / 100.0)

# 6. Честный интегральный расчет Lifetime (LT) игрока за 30 дней
player_lifetime = 1.0 + sum([(d1 / 100.0) * (t ** -alpha) for t in range(2, 31)]) if d1 > 0 else 1.0
arpdau_usd = (total_net_developer_usd / 30.0) / max(dau, 1)
ltv_usd = arpdau_usd * player_lifetime

# --- ВЫВОД МЕТРИК ---
st.write("---")
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    st.metric("Общий чистый доход проекта (Net)", f"${total_net_developer_usd:,.2f}")
    st.metric("Выплата инвестору / мес", f"${investor_payout:,.2f}")
with m_col2:
    st.metric("Чистая прибыль после расходов", f"${net_profit_after_costs:,.2f}")
    st.metric("В фонд реинвестирования", f"${reinvest_pool:,.2f}")
with m_col3:
    st.metric("Чистый профит команды/студии", f"${studio_profit:,.2f}")
    st.metric("Расходы на содержание игры", f"${monthly_costs:,.2f}")
with m_col4:
    st.metric("Расчетный LTV игрока", f"${ltv_usd:.4f}")
    if investor_payout > 0:
        roi = investment / investor_payout
        st.metric("Срок окупаемости ROI", f"{roi:.1f} мес." if roi < 36 else "> 3 лет")
    else:
        st.metric("Срок окупаемости ROI", "∞ (0% инвестору)")

# --- ГРАФИКИ ---
st.write("---")
st.subheader("📊 Моделирование окупаемости и распределения")

tab1, tab2 = st.tabs(["📉 Динамика ROI", "🍕 Структура распределения Net USD"])

with tab1:
    months = np.arange(0, 13)
    investor_cumulative = -investment + (investor_payout * months)
    studio_cumulative = studio_profit * months
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('#0b0f19')
    ax.set_facecolor('#111827')
    
    # Неоновые линии баланса
    ax.plot(months, investor_cumulative, color='#00ffcc', label='Баланс инвестора ($)', linewidth=2.5, zorder=3)
    ax.plot(months, investor_cumulative, color='#00ffcc', alpha=0.25, linewidth=6, zorder=2)
    ax.plot(months, studio_cumulative, color='#ff007f', label='Накопленная прибыль студии ($)', linewidth=2, linestyle='--')
    
    ax.axhline(0, color='#4a5568', linestyle='-', linewidth=1, alpha=0.5)
    
    if investor_payout > 0:
        cross_month = investment / investor_payout
        if 0 <= cross_month <= 12:
            ax.scatter(cross_month, 0, color='#ffea00', s=100, zorder=5)
            # Безопасное относительное смещение в пикселях без жестких координат по Y
            ax.annotate('ROI достигнут! 🎉', xy=(cross_month, 0), 
                        xytext=(15, 12), textcoords='offset points',
                        color='#ffea00', weight='bold',
                        arrowprops=dict(arrowstyle="->", color='#ffea00', lw=1.2))

    ax.set_title("Прогноз окупаемости на 12 месяцев", color='#e2e8f0', fontsize=11)
    ax.set_xlabel("Месяцы", color='#a0aec0')
    ax.set_ylabel("Капитал ($)", color='#a0aec0')
    ax.grid(True, color='#2d3748', alpha=0.4, linestyle=':')
    ax.legend(facecolor='#111827', edgecolor='#2d3748')
    st.pyplot(fig)

with tab2:
    # Диаграмма распределения чистого дохода
    labels = ['Инвестор', 'Реинвест', 'Студия/Команда', 'Фикс. Расходы']
    sizes = [investor_payout, reinvest_pool, studio_profit, min(monthly_costs, total_net_developer_usd)]
    colors = ['#00ffcc', '#00bfff', '#ff007f', '#a0aec0']
    
    fig2, ax2 = plt.subplots(figsize=(5, 3.5))
    fig2.patch.set_facecolor('#0b0f19')
    ax2.set_facecolor('#111827')
    
    if sum(sizes) > 0:
        wedges, texts, autotexts = ax2.pie(
            sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors,
            wedgeprops=dict(width=0.4, edgecolor='#111827', linewidth=2)
        )
        for t in texts: t.set_color('#e2e8f0')
        for at in autotexts: 
            at.set_color('#0b0f19')
            at.set_weight('bold')
        ax2.set_title("Куда уходят чистые USD проекта в месяц", color='#e2e8f0', fontsize=11)
    else:
        ax2.text(0.5, 0.5, "Проект пока не генерирует доход", color='#a0aec0', ha='center')
        
    st.pyplot(fig2)