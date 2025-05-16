import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


customers = pd.read_csv('customers.csv')
items = pd.read_csv('Items_cleaned.csv')  # גרסה נקייה מכפילויות
order_items = pd.read_csv('order_item_updated.csv')  # גרסה עם item_id מעודכן
orders = pd.read_csv('orders.csv')

for df in [customers, items, order_items, orders]:
    df.columns = df.columns.str.strip().str.lower()

if 'id' in customers.columns:
    customers.rename(columns={'id': 'customer_id'}, inplace=True)
if 'id' in items.columns:
    items.rename(columns={'id': 'item_id'}, inplace=True)

customers = customers[customers.isnull().sum(axis=1) < 3].copy()

print("\nעמודות ב-items:", items.columns)
print("עמודות ב-customers:", customers.columns)
print("עמודות ב-order_items:", order_items.columns)
print("עמודות ב-orders:", orders.columns)

# חלק 1: מחיר ממוצע של פריט
average_price = items["item_price"].mean()
print("\nמחיר ממוצע של פריט:", round(average_price, 2))

# חלק 2: הלקוח שרכש הכי הרבה מוצרים
merged = pd.merge(order_items, orders, on="order_id")
merged = pd.merge(merged, customers, on="customer_id")
customer_totals = merged.groupby(["first_name", "last_name"])["quantity"].sum()
top_customer = customer_totals.idxmax()
top_quantity = customer_totals.max()
print("\nהלקוח שרכש הכי הרבה מוצרים:", top_customer, "סה\"כ כמות:", top_quantity)

# חלק 3: חישוב total_price לכל שורה ב-order_items
order_items_merged = pd.merge(order_items, items, on="item_id")
order_items_merged["total_price"] = order_items_merged["quantity"] * order_items_merged["item_price"]
print("\nדוגמה ל-order_items עם total_price:")
print(order_items_merged.head())

# חלק 4: סכום כולל לכל הזמנה
order_totals = order_items_merged.groupby('order_id')['total_price'].sum().reset_index()
print("\nסכום כולל לכל הזמנה:")
print(order_totals.head())

# חלק 5: הזמנה יקרה, זולה וממוצעת
print("הקנייה הכי יקרה:", order_totals['total_price'].max())
print("הקנייה הכי זולה:", order_totals['total_price'].min())
print("הקנייה הממוצעת:", order_totals['total_price'].mean())

# חלק 6: טבלת Pivot לפי לאום ומגדר
pivot_table = pd.pivot_table(customers, index='nationality', columns='gender', aggfunc='size', fill_value=0)
print("\nPivot Table לפי לאום ומגדר:")
print(pivot_table)

# חלק שני – גרפים

# ניקוי לקוחות (לדוגמה: dropna - אפשר לשפר לפי צורך)
customers_clean = customers.dropna(subset=['gender', 'nationality', 'age'])

# פילוג מגדר
plt.figure(figsize=(6, 4))
sns.countplot(data=customers_clean, x='gender')
plt.title("פילוג לקוחות לפי מגדר")
plt.xlabel("מגדר")
plt.ylabel("כמות")
plt.show()

# פילוג לפי לאום
plt.figure(figsize=(8, 5))
sns.countplot(data=customers_clean, x='nationality', order=customers_clean['nationality'].value_counts().index)
plt.title("פילוג לקוחות לפי לאום")
plt.xlabel("לאום")
plt.ylabel("כמות")
plt.xticks(rotation=45)
plt.show()

# היסטוגרמה לפי גיל
plt.figure(figsize=(6, 4))
sns.histplot(data=customers_clean, x='age', bins=10, kde=True)
plt.title("התפלגות גיל לקוחות")
plt.xlabel("גיל")
plt.ylabel("כמות")
plt.show()

# לקוחות חדשים לפי שנה
customers_clean['joining_date'] = pd.to_datetime(customers_clean['joining_date'], errors='coerce')
customers_clean['join_year'] = customers_clean['joining_date'].dt.year
plt.figure(figsize=(8, 4))
sns.countplot(data=customers_clean, x='join_year', order=sorted(customers_clean['join_year'].dropna().unique()))
plt.title("לקוחות חדשים לפי שנה")
plt.xlabel("שנה")
plt.ylabel("כמות")
plt.show()

# מכירות לפי חודשים
orders['order_date'] = pd.to_datetime(orders['order_date'], errors='coerce')
orders['order_month'] = orders['order_date'].dt.to_period('M')
plt.figure(figsize=(10, 5))
orders['order_month'].value_counts().sort_index().plot(kind='bar')
plt.title("כמות מכירות לפי חודשים")
plt.xlabel("חודש")
plt.ylabel("כמות מכירות")
plt.xticks(rotation=45)
plt.show()

# פילוג קניות לפי גיל (עם סכום קניות)
merged = orders.merge(order_items, on='order_id')
merged = merged.merge(customers[['customer_id', 'age']], on='customer_id')
merged = merged.merge(items[['item_id', 'item_price']], on='item_id')
merged['total_price'] = merged['item_price'] * merged['quantity']
plt.figure(figsize=(8, 5))
sns.histplot(data=merged, x='age', weights='total_price', bins=10, kde=True)
plt.title("פילוג קניות לפי גיל")
plt.xlabel("גיל")
plt.ylabel("סך קניות")
plt.show()
