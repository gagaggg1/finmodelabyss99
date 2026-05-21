import streamlit as st
import matplotlib.pyplot as plt

# Настройки страницы
st.set_page_config(page_title="Abyss 99 | Full Enterprise Model", layout="wide")

st.title("🐙 Abyss 99: Полная аналитическая панель (Enterprise Edition)")

# --- САЙДБАР: ГЛОБАЛЬНЫЕ НАСТРОЙКИ ---
with st.sidebar:
    st.header("⚙️ Глобальные параметры")
    ccu = st.slider("Средний онлайн (CCU):", 50, 10000, 500, 50)
    session_time = st.slider("Длина сессии (мин):", 1, 60, 15, 1)
    cac = st.number_input("Стоимость привлечения 1 юзера (CAC) ($):", 0.01, 2.00, 0.20, 0.01)
    st.divider()
    base_d1 = st.slider("D1 Retention (идеал %):", 10.0, 60.0, 32.0)
    base_conv = st.slider("Конверсия в донат (%):", 0.5, 10.0, 2.5) / 100.0
    base_arppu = st.slider("Чек донатера (R$):", 50, 2000, 280)
    devex = st.slider("Курс DevEx ($ за 1 R$):", 0.0010, 0.0100, 0.0035, 0.0001)
    share = st.slider("Доля инвестора (%):", 0, 100, 35) / 100.0

# --- ЛОГИКА РАСЧЕТОВ ---
TARGET_SESSION = 10.0
retention_factor = (session_time / TARGET_SESSION) ** 2 if session_time < TARGET_SESSION else min(1.15, 1.0 + (session_time - TARGET_SESSION) / 100.0)
d1 = max(0.0, min(base_d1 * retention_factor, 75.0))
lifetime = 1 + sum([(d1/100.0) * (t ** -0.55) for t in range(2, 31)])
dau = (ccu * 1440) / session_time
mau = dau * (30 / lifetime)
session_mon = max(0.02, min(1.0, session_time / TARGET_SESSION))
real_conv = base_conv * session_mon * max(0.1, min(1.0, d1/base_d1))
gross_usd = ((dau * real_conv * lifetime * base_arppu * 0.70 * devex) + (dau * 0.03 * session_time * 30 * 0.00015 * (d1/100)))
total_marketing = (dau * 30 / lifetime) * cac
net_profit = gross_usd - total_marketing
investor_share = net_profit * share if net_profit > 0 else 0

# --- ВЫВОД: МАСШТАБНЫЙ ИНТЕРФЕЙС ---

# Блок 1: Метрики аудитории
st.subheader("📊 Операционные метрики аудитории")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ежедневный онлайн (DAU)", f"{int(dau):,}")
c2.metric("Месячный охват (MAU)", f"{int(mau):,}")
c3.metric("Retention D1", f"{d1:.1f}%")
c4.metric("LTV игрока", f"${(gross_usd / mau if mau > 0 else 0):.4f}")

st.divider()

# Блок 2: Финансы
st.subheader("💰 Финансовый отчет (Monthly)")
f1, f2, f3, f4 = st.columns(4)
f1.metric("Gross Выручка", f"${gross_usd:,.2f}")
f2.metric("Расходы на трафик", f"${total_marketing:,.2f}")
f3.metric("Чистая прибыль", f"${net_profit:,.2f}")
f4.metric("Выплата инвестору", f"${investor_share:,.2f}")

# Статус окупаемости
if net_profit > 0:
    roi_time = 4500 / investor_share if investor_share > 0 else 99
    st.success(f"### 📈 Проект прибыльный! Расчетный срок окупаемости вложений ($4500): {roi_time:.1f} месяцев.")
else:
    st.error("### ⚠️ Проект убыточен: Стоимость привлечения (CAC) превышает доходность.")

# Блок 3: График на 12 месяцев
st.subheader("🗓️ Прогноз возврата инвестиций (ROI)")
fig, ax = plt.subplots(figsize=(14, 5))
ax.set_facecolor('#0e1117')
fig.patch.set_facecolor('#0e1117')
balance = [-4500 + (investor_share * i) for i in range(13)]
ax.plot(range(13), balance, color='#00ff41', lw=4, marker='o', markersize=8)
ax.axhline(0, color='white', lw=1, ls='--')
plt.xticks(range(13), [f"Месяц {i}" for i in range(13)])
ax.tick_params(colors='white')
ax.set_ylabel("Чистый баланс инвестора ($)", color='white')
st.pyplot(fig)