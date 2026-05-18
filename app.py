import streamlit as st
import matplotlib.pyplot as plt

# Настройки веб-страницы
st.set_page_config(page_title="Abyss 99 Financial Model", layout="wide")

st.title("⚓ Финансовая модель: «99 Ночей в Бездне»")
st.write("Интерактивный калькулятор доходности игры в Roblox (Базовая консервативная модель).")

# Константы платформы Roblox
ROBLOX_TAX = 0.30       # Комиссия 30%
DEVEX_RATE = 0.0035     # Курс DevEx ($0.0035 за 1 Robux)
INVESTMENT = 4500       # Сумма вложений инвестора

# Боковая панель с ползунками для управления переменными
st.sidebar.header("🎛️ Настройка переменных")

ccu = st.sidebar.slider("Средний онлайн (CCU):", 100, 30000, 1500, step=100)
mau = st.sidebar.slider("Игроков в месяц (MAU):", 10000, 5000000, 250000, step=10000)
conv = st.sidebar.slider("Конверсия в донат (%):", 0.5, 5.0, 2.0, step=0.1) / 100.0
arppu = st.sidebar.slider("Средний чек (Robux):", 50, 1000, 250, step=10)
share = st.sidebar.slider("Доля инвестора после ROI (%):", 10, 90, 35, step=5) / 100.0

# 1. Расчет чистой прибыли с прямых донатов
paying_users = mau * conv
gross_robux = paying_users * arppu
net_usd_donates = (gross_robux * (1 - ROBLOX_TAX)) * DEVEX_RATE

# 2. Базовый Premium Payouts без повышенных коэффициентов
premium_bonus = ccu * 1.0

# 3. Итоговые показатели прибыли
total_monthly_usd = net_usd_donates + premium_bonus
investor_payout = total_monthly_usd * share
roi_months = INVESTMENT / total_monthly_usd if total_monthly_usd > 0 else 99

# Вывод красивых карточек с результатами на сайт asdasdasd324
col1, col2, col3 = st.columns(3)
col1.metric("Общая прибыль плейса", f"${total_monthly_usd:,.2f} / мес")
col2.metric("Пассивный доход инвестора", f"${investor_payout:,.2f} / мес")

if roi_months <= 1:
    col3.metric("Срок окупаемости", "1-й месяц релиза!", delta="⚡ Моментальный возврат")
else:
    col3.metric("Срок окупаемости", f"~ {roi_months:.1f} мес.", delta="После старта релиза")

st.markdown("---")

# Построение интерактивного графика возврата инвестиций по месяцам
months = ['М1 (Разработка)', 'М2 (Разработка)', 'М3 (Тест)', 'М4 (Релиз)', 'М5', 'М6']
balance = [-4500, -4500, -4100, 
           -4100 + investor_payout, 
           -4100 + (investor_payout * 2), 
           -4100 + (investor_payout * 3)]

fig, ax = plt.subplots(figsize=(10, 4))
ax.axhline(0, color='gray', linewidth=0.8, linestyle='--')
ax.plot(months, balance, marker='o', color='#00e676', linewidth=2.5, label="Баланс капитала инвестора")
ax.fill_between(months, balance, 0, where=[b<0 for b in balance], color='#ff1744', alpha=0.15)
ax.fill_between(months, balance, 0, where=[b>=0 for b in balance], color='#00e676', alpha=0.15)
ax.set_ylabel("Капитал инвестора ($)")
ax.set_title("Динамика окупаемости инвестиций и выхода в чистый пассивный доход")
ax.grid(True, alpha=0.2)

# Отображаем график на веб-странице
st.pyplot(fig)