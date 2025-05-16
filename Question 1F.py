import pandas as pd

customers = pd.read_csv('customers.csv')
items = pd.read_csv('Items.csv')
order_item = pd.read_csv('order_item.csv')
orders = pd.read_csv('orders.csv')

def explore_table(df, name):
    print(f"\n--- טבלה: {name} ---")
    print("שמות עמודות וסוגי נתונים:")
    print(df.dtypes)

    print("\nכמות ערכים שאינם NAN:")
    print(df.count())

    print("\nסטטיסטיקות כלליות:")
    print(df.describe(include='all', datetime_is_numeric=True))

    print("\nחמש שורות ראשונות:")
    print(df.head())
    print("-" * 40)

explore_table(customers, "customers")
explore_table(items, "items")
explore_table(order_item, "order_item")
explore_table(orders, "orders")


items["not_null_count"] = items.notnull().sum(axis=1)

items_sorted = items.sort_values(by=["item_name", "not_null_count"], ascending=[True, False])

items_deduplicated = items_sorted.drop_duplicates(subset="item_name", keep="first")

items_deduplicated = items_deduplicated.drop(columns=["not_null_count"])

items_deduplicated.to_csv("Items_cleaned.csv", index=False)
print("\nבוצעה הסרת כפילויות מטבלת items. הטבלה החדשה נשמרה כ-Items_cleaned.csv")


missing_counts = customers.isnull().sum(axis=1)
customers_clean = customers[missing_counts < 3].copy()
print(f"\nמספר הלקוחות אחרי סינון לקוחות עם 3+ ערכים חסרים: {len(customers_clean)}")


order_item_orders = pd.merge(order_item, orders[['order_id', 'customer_id']], on='order_id', how='left')

valid_customer_ids = set(customers_clean['customer_id'])
order_item_filtered = order_item_orders[order_item_orders['customer_id'].isin(valid_customer_ids)].copy()

order_item_filtered = order_item_filtered[order_item.columns]

print(f"\nמספר שורות בטבלת order_item אחרי סינון לפי לקוחות תקינים: {len(order_item_filtered)}")


order_item_with_name = pd.merge(order_item_filtered, items[['item_id', 'item_name']], on='item_id', how='left')

order_item_updated = pd.merge(order_item_with_name.drop(columns=['item_id']),
                              items_deduplicated[['item_id', 'item_name']],
                              on='item_name', how='left')

print("\nחלק משורות order_item לאחר עדכון ה-item_id לפי הטבלה הנקייה:")
print(order_item_updated.head())

order_item_updated.to_csv("order_item_updated.csv", index=False)
print("\nטבלת order_item עודכנה ושמרה את ה-item_id המעודכן בקובץ order_item_updated.csv")
