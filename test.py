import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from dotenv import load_dotenv
load_dotenv() 
import os

db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
engine = create_engine(db_url)


#Normal Select with Aggregation product category and total_orders
# query = """
# SELECT product_category, COUNT(*) AS total_orders
# FROM orders
# GROUP BY product_category
# ORDER BY total_orders DESC;
# """

# Query with CASE or If statement 
# Case basically returns the value 1 if an order is cancelled and null if it isnt. 
# As Count only counts non null values it wont count all the items that doesnt have 
# order_status = 'Cancelled'
# Expanded a bit to have multiple columns back.
# in df.plot you just have to add an array of the column names.
#    y=['cancelled_orders', 'completed_orders', 'total_orders'], 
# query = """
# Select product_category, 
# COUNT(CASE WHEN order_status = 'Cancelled' THEN 1 END) AS cancelled_orders, 
# COUNT(CASE WHEN order_status = 'Completed' THEN 1 END) as completed_orders,
# COUNT(CASE WHEN order_status != 'Pending' THEN 1 END) AS total_orders
# FROM orders
# GROUP BY product_category
# ORDER BY cancelled_orders DESC
# """

# Prøv å counte hvor mange om dager med flest ordre på toppen gruppert på måneder.
query = """
WITH daily_counts AS (
  SELECT 
    DATE_TRUNC('month', order_date) AS month,
    order_date AS day,
    COUNT(CASE WHEN order_status = 'Completed' THEN 1 END) AS dailyOrders
  FROM orders
  GROUP BY month, day
),
monthly_totals AS (
  SELECT 
    DATE_TRUNC('month', order_date) AS month,
    COUNT(CASE WHEN order_status = 'Completed' THEN 1 END) AS monthlyOrders
  FROM orders
  GROUP BY month
),
highest_days AS (
  SELECT 
    d.*,
    ROW_NUMBER() OVER (PARTITION BY d.month ORDER BY d.dailyOrders DESC, d.day) AS day_rank
  FROM daily_counts d
)
SELECT 
  COALESCE(TO_CHAR(CASE WHEN h.day_rank = 1 THEN h.month ELSE NULL END, 'YYYY-MM-DD'), '') AS month,
  TO_CHAR(h.day, 'YYYY-MM-DD') AS day,
  h.dailyOrders,
  COALESCE(CAST(CASE WHEN h.day_rank = 1 THEN m.monthlyOrders ELSE NULL END AS TEXT), '') AS monthlyOrders
FROM highest_days h
JOIN monthly_totals m ON h.month = m.month
ORDER BY h.month, h.day_rank;
"""


df = pd.read_sql(query, engine)

ax = df.plot(
    kind='bar',
    x='month',
    y=['dailyorders','monthlyorders'],
    color='#4CAF50',  # custom green
    figsize=(10, 6),
    legend=False,
    edgecolor='black'
)

plt.title("Monthly Completed Orders", fontsize=16, weight='bold')
plt.xlabel("Month", fontsize=12)
plt.ylabel("Orders", fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(fontsize=10)

plt.grid(axis='y', linestyle='--', alpha=0.7)

for p in ax.patches:
    ax.annotate(str(p.get_height()),
                (p.get_x() + p.get_width() / 2, p.get_height()),
                ha='center', va='bottom', fontsize=9, color='black')

plt.tight_layout()
plt.show()
