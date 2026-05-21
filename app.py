# 2. РАСЧЕТ CREATOR REWARDS (Реалистичный подход)
# Часть А: Daily Engagement Rewards (5 R$ за VGU, топ-3 запуск)
daily_active_spenders = dau * vgu_ratio
top3_filter_ratio = 0.015  
monthly_qualified_engagement = (daily_active_spenders * top3_filter_ratio) * 30
engagement_rewards_usd = (monthly_qualified_engagement * 5.0 * (1.0 - ROBLOX_TAX)) * devex_rate

# Часть Б: Affiliate Rewards (Реалистичный 1% новичков от MAU)
new_or_returned_ratio = 0.01  # Реалистичная конверсия потока
monthly_total_affiliates = mau * new_or_returned_ratio

# Конверсия в платящих в ROBLOX (1.5%)
affiliate_pay_conv = 0.015  
monthly_paying_affiliates = monthly_total_affiliates * affiliate_pay_conv

# Средний чек новичка в Roblox ($25) * наша доля (35%) = $8.75 с человека
affiliate_revenue_per_user = 25.0 * 0.35
affiliate_rewards_usd = monthly_paying_affiliates * affiliate_revenue_per_user

awards_bonus_usd = engagement_rewards_usd + affiliate_rewards_usd