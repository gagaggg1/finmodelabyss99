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
st.caption("Бизнес-модель и симуляция LTV/ROI для подводного выживания в Roblox")

# --- ЛОГИКА РАСЧЕТОВ ---
def calculate_economics(ccu, session_time, d1, d7, d30, conv, arppu, premium_share, investment, investor_share, base_session=30.0):
    # 1. Расчет аудитории (DAU фиксирован относительно базовой сессии, чтобы рост времени игры не уменьшал базу игроков)
    dau = (ccu * 1440) / base_session
    
    # Эмпирический расчет MAU на основе затухания удержания
    mau = dau * 30 * (1 - (d1 + d7 + d30) / 300.0)
    mau = max(mau, dau * 1.5) # Защита от отрицательного или слишком маленького MAU
    
    # 2. Монетизация от длины сессии (Вовлечение увеличивает конверсию и чек)
    session_factor = session_time / base_session
    dynamic_conv = min((conv / 100.0) * (session_factor ** 0.5), 1.0)
    dynamic_arppu = arppu * (session_factor ** 0.7)
    
    # Доход от донатов (Robux)
    daily_paying_users = dau * dynamic_conv
    gross_robux_donates = daily_paying_users * 30 * (1 + (d30 / 100.0)) * dynamic_arppu
    
    # 3. Premium-выплаты (Engagement Payouts)
    total_engagement_minutes_monthly = dau * 30 * session_time
    premium_minutes_monthly = total_engagement_minutes_monthly * (premium_share / 100.0)
    
    # Базовая ставка + бонус за долгосрочное удержание D7
    robux_per_premium_minute = 0.00015 * (1 + (d7 / 100.0))
    gross_robux_premium = premium_minutes_monthly * robux_per_premium_minute
    
    # Итоговые показатели в Robux и USD (Курс DevEx: 1 Robux = $0.0035)
    total_gross_robux = gross_robux_donates + gross_robux_premium
    total_gross_usd = total_gross_robux * 0.0035
    
    # Налог Roblox на донаты (30%), Premium-выплаты приходят чистыми
    net_developer_usd = (gross_robux_donates * 0.7 + gross_robux_premium) * 0.0035
    
    # Распределение прибыли
    investor_payout = net_developer_usd * (investor_share / 100.0)
    studio_profit = net_developer_usd - investor_payout
    
    # Расчет честного LTV (Доход на одного пользователя в месяц)
    ltv_usd = net_developer_usd / max(mau, 1)
    
    return {
        "dau": int(dau),
        "mau": int(mau),
        "gross_robux": total_gross_robux,
        "gross_usd": total_gross_usd,
        "net_developer_usd": net_developer_usd,
        "investor_payout": investor_payout,
        "studio_profit": studio_profit,
        "ltv_usd": ltv_usd,
        "premium_robux": gross_robux_premium,
        "donate_robux": gross_robux_donates
    }

# --- ИНТЕРФЕЙС: БОКОВАЯ ПАНЕЛЬ С НАСТРОЙКАМИ ---
st.sidebar.header("🛸 Метрики Трафика")
ccu = st.sidebar.slider("Средний онлайн (CCU)", 10, 5000, 500, step=50)
session_time = st.sidebar.slider("Длина сессии (мин)", 10, 180, 45, step=5)

st.sidebar.header("📈 Удержание (Retention)")
d1 = st.sidebar.slider("Day 1 Retention (%)", 5.0, 60.0, 35.0, step=1.0)
# Математическое автовычисление D7 и D30 по степенному закону для подсказки
alpha = -np.log(d1/100.0) / np.log(2) if d1 > 0 else 1
pred_d7 = float(np.clip((d1/100.0) * (7**-0.5) * 100, 1.0, d1))
pred_d30 = float(np.clip((d1/100.0) * (30**-0.5) * 100, 0.5, pred_d7))

d7 = st.sidebar.slider("Day 7 Retention (%)", 1.0, 30.0, pred_d7, step=0.5)
d30 = st.sidebar.slider("Day 30 Retention (%)", 0.1, 15.0, pred_d30, step=0.1)

st.sidebar.header("💰 Монетизация")
conv = st.sidebar.slider("Базовая конверсия в донат (%)", 0.1, 10.0, 2.5, step=0.1)
arppu = st.sidebar.number_input("Средний чек платящего (ARPPU в Robux)", 50, 5000, 450, step=50)
premium_share = st.sidebar.slider("Доля Premium игроков (%)", 1.0, 40.0, 15.0, step=0.5)

st.sidebar.header("🤝 Инвестиции и Доли")
investment = st.sidebar.number_input("Сумма инвестиций ($)", 0, 100000, 7000, step=500)
investor_share = st.sidebar.slider("Доля инвестора в прибыли (%)", 0, 100, 35, step=5)

# --- ВЫЧИСЛЕНИЯ ---
data = calculate_economics(ccu, session_time, d1, d7, d30, conv, arppu, premium_share, investment, investor_share)

# --- ВЫВОД ОСНОВНЫХ МЕТРИК ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Суточный охват (DAU)", f"{data['dau']:,}")
    st.metric("Месячный оборот (Gross)", f"${data['gross_usd']:,.2f}")
with col2:
    st.metric("Месячный охват (MAU)", f"{data['mau']:,}")
    st.metric("Чистый доход студии", f"${data['studio_profit']:,.2f}")
with col3:
    st.metric("Месячный чистый доход (Net)", f"${data['net_developer_usd']:,.2f}")
    st.metric("Выплата инвестору / мес", f"${data['investor_payout']:,.2f}")
with col4:
    st.metric("Честный LTV игрока", f"${data['ltv_usd']:.4f}")
    if data['investor_payout'] > 0:
        roi_months = investment / data['investor_payout']
        st.metric("Окупаемость инвестиций", f"{roi_months:.1f} мес." if roi_months < 36 else "> 3 лет")
    else:
        st.metric("Окупаемость инвестиций", "∞ (0% инвестору)")

st.write("---")

# --- ВИЗУАЛИЗАЦИЯ: ГРАФИКИ ---
st.subheader("📊 Аналитика доходов и окупаемости проекта")

tab1, tab2 = st.tabs(["📉 График окупаемости (ROI)", "🍕 Структура доходов (Robux)"])

with tab1:
    # График окупаемости по месяцам (на 12 месяцев)
    months = np.arange(0, 13)
    investor_cumulative = -investment + (data['investor_payout'] * months)
    studio_cumulative = (data['studio_profit'] * months)
    
    # Настройка темного стиля для matplotlib
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.patch.set_facecolor('#0b0f19')
    ax.set_facecolor('#111827')
    
    # Линии с неоновым свечением (Neon Glow effect)
    ax.plot(months, investor_cumulative, color='#00ffcc', label='Баланс Инвестора ($)', linewidth=2.5, zorder=3)
    ax.plot(months, investor_cumulative, color='#00ffcc', alpha=0.3, linewidth=6, zorder=2) # Свечение
    
    ax.plot(months, studio_cumulative, color='#ff007f', label='Чистая прибыль Студии ($)', linewidth=2, linestyle='--', alpha=0.8)
    
    # Линия нуля (точка безубыточности)
    ax.axhline(0, color='#4a5568', linestyle='-', linewidth=1, alpha=0.5)
    
    # Поиск точки окупаемости для аннотации
    if data['investor_payout'] > 0:
        cross_month = investment / data['investor_payout']
        if 0 <= cross_month <= 12:
            ax.scatter(cross_month, 0, color='#ffea00', s=100, edgecolor='black', zorder=5, label='Точка окупаемости')
            # Безопасное относительное смещение текста в пикселях, чтобы избежать наложения
            ax.annotate('ROI 100%! 🎉', xy=(cross_month, 0), 
                        xytext=(15, 10), textcoords='offset points',
                        color='#ffea00', weight='bold',
                        arrowprops=dict(arrowstyle="->", color='#ffea00', lw=1.5))

    ax.set_title("Прогноз динамики капитала на 12 месяцев", color='#e2e8f0', fontsize=12, pad=15)
    ax.set_xlabel("Месяцы с момента релиза", color='#a0aec0')
    ax.set_ylabel("Капитал ($)", color='#a0aec0')
    ax.grid(True, color='#2d3748', alpha=0.5, linestyle=':')
    ax.legend(facecolor='#111827', edgecolor='#2d3748', loc='upper left')
    
    st.pyplot(fig)

with tab2:
    # Круговая диаграмма распределения поступающих Robux
    labels = ['Внутриигровые Донаты', 'Premium Выплаты (Engagement)']
    sizes = [data['donate_robux'], data['premium_robux']]
    colors = ['#00bfff', '#00ffcc']
    
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    fig2.patch.set_facecolor('#0b0f19')
    ax2.set_facecolor('#111827')
    
    if sum(sizes) > 0:
        wedges, texts, autotexts = ax2.pie(
            sizes, labels=labels, autopct='%1.1f%%', 
            startangle=140, colors=colors, 
            textcolor='#e2e8f0',
            wedgeprops=dict(width=0.4, edgecolor='#111827', linewidth=3) # Donut chart стиль
        )
        for text in texts:
            text.set_color('#e2e8f0')
        for autotext in autotexts:
            autotext.set_color('#0b0f19')
            autotext.set_weight('bold')
    else:
        ax2.text(0.5, 0.5, "Нет данных для отображения", color='#a0aec0', ha='center')
        
    ax2.set_title("Источник входящего трафика валюты (Robux)", color='#e2e8f0', fontsize=12, pad=10)
    st.pyplot(fig2)

# --- СПРАВОЧНЫЙ БЛОК ---
st.markdown("""
> 💡 **Как теперь работает симуляция сессий:** 
> Мы отвязали дневную аудиторию (`DAU`) от падения при увеличении времени игры. Теперь рост длины сессии плавно увеличивает **конверсию в донат** (на показатель `^0.5`) и **средний чек** (на `^0.7`). Это симулирует естественное поведение игрока: чем глубже и дольше длится сессия в подводном хорроре, тем сильнее нагнетается атмосфера, и тем охотнее пользователь покупает расходники, геймпассы или тратит Premium-минуты платформы.
""")