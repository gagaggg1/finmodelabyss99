import streamlit as st
import matplotlib.pyplot as plt

# Настройки веб-страницы
st.set_page_config(page_title="Abyss 99 Financial Model", layout="wide")

st.title("⚓ Финансовая модель: «99 Ночей в Бездне»")
st.write("Интерактивный калькулятор доходности игры в Roblox (Гибкая базовая модель).")

# Константы платформы Roblox
ROBLOX_TAX = 0.30       # Фиксированная комиссия 30%
INVESTMENT = 4500       # Сумма вложений инвестора

# Боковая панель управления (Ввод чисел вручную)
st.sidebar.header("🎛️ Настройка переменных")

ccu = st.sidebar.number_input("Средний онлайн (CCU):", min_value=0, max_value=100000, value=1500, step=100)
mau = st.sidebar.number_input("Игроков в месяц (MAU):", min_value=0, max_value=50000000, value=250000, step=10000)
conv = st.sidebar.number_input("Конверсия в донат (%):", min_value=0.0, max_value=100.0, value=2.0, step=0.1, format="%.1f") / 100.0
arppu = st.sidebar.number_input("Средний чек (Robux):", min_value=0, max_value=100000, value=250, step=10)
devex_rate = st.sidebar.number_input("Курс DevEx ($ за 1 Robux):", min_value=0.0, max_value=0.1, value=0.0035, step=0.0001, format="%.4f")
share = st.sidebar.number_input("Доля инвестора после ROI (%):", min_value=0, max_value=100, value=35, step=5) / 100.0

# 1. Расчет чистой прибыли с прямых донатов
paying_users = mau * conv
gross_robux = paying_users * arppu
net_usd_donates = (gross_robux * (1 - ROBLOX_TAX)) * devex_rate

# 2. Базовый Premium Payouts
premium_bonus = ccu * 1.0

# 3. Итоговые показатели прибыли
total_monthly_usd = net_usd_donates + premium_bonus
investor_payout = total_monthly_usd * share

# Расчет окупаемости (ROI)
# Если доля инвестора = 0%, то технически окупаемости "нет", считаем по 100% доходу плейса до возврата инвестиций
if share > 0:
    roi_months = INVESTMENT / investor_payout if investor_payout > 0 else 99
else:
    roi_months = INVESTMENT / total_monthly_usd if total_monthly_usd > 0 else 99

# Вывод карточек с результатами
col1, col2, col3 = st.columns(3)
col1.metric("Общая прибыль плейса", f"${total_monthly_usd:,.2f} / мес")
col2.metric("Пассивный доход инвестора", f"${investor_payout:,.2f} / мес")

if roi_months <= 1:
    col3.metric("Срок окупаемости", "1-й месяц релиза!", delta="⚡ Отличный темп")
else:
    col3.metric("Срок окупаемости", f"~ {roi_months:.1f} мес.", delta="После старта релиза")

st.markdown("---")

# Построение интерактивного графика
months = ['М1 (Разработка)', 'М2 (Разработка)', 'М3 (Тест)', 'М4 (Релиз)', 'М5', 'М6']

# Моделируем баланс: до релиза инвестор в минусе на $4500, на тесте немного отбивается (-$4100)
# С 4 месяца капает выплата инвестору. Если доля 0%, график просто покажет выход самого проекта "в ноль".
payout_step = investor_payout if share > 0 else total_monthly_usd
balance = [-4500, -4500, -4100, 
           -4100 + payout_step, 
           -4100 + (payout_step * 2), 
           -4100 + (payout_step * 3)]

fig, ax = plt.subplots(figsize=(10, 4))
ax.axhline(0, color='gray', linewidth=0.8, linestyle='--')
ax.plot(months, balance, marker='o', color='#00e676', linewidth=2.5, label="Баланс капитала")
ax.fill_between(months, balance, 0, where=[b<0 for b in balance], color='#ff1744', alpha=0.15)
ax.fill_between(months, balance, 0, where=[b>=0 for b in balance], color='#00e676', alpha=0.15)
ax.set_ylabel("Капитал ($)")
ax.set_title("Динамика окупаемости проекта")
ax.grid(True, alpha=0.2)

st.pyplot(fig)