import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

print("1. Loading dataset...")
df = pd.read_excel('Online Retail.xlsx')
print(f"Loaded {len(df):,} rows.")

print("\n2. Cleaning dataset...")
# Remove duplicates
df_clean = df.drop_duplicates().copy()

# Remove missing values
df_clean = df_clean.dropna(subset=['CustomerID', 'Description'])

# Remove cancellations and invalid quantities/prices
df_clean = df_clean[~df_clean['InvoiceNo'].astype(str).str.startswith('C')]
df_clean = df_clean[(df_clean['Quantity'] > 0) & (df_clean['UnitPrice'] > 0)]

# Format types and calculate revenue
df_clean['CustomerID'] = df_clean['CustomerID'].astype(int)
df_clean['Revenue'] = (df_clean['Quantity'] * df_clean['UnitPrice']).round(2)
df_clean['YearMonth'] = df_clean['InvoiceDate'].dt.to_period('M')

print(f"Cleaned dataset: {len(df_clean):,} valid rows across {df_clean['CustomerID'].nunique():,} customers.")

print("\n3. Analyzing Sales & Revenue Trends Over Time...")
monthly_trends = df_clean.groupby('YearMonth').agg(
    Revenue=('Revenue', 'sum'),
    Orders=('InvoiceNo', 'nunique'),
    Units_Sold=('Quantity', 'sum'),
    Active_Customers=('CustomerID', 'nunique')
).reset_index()
monthly_trends['YearMonth_Str'] = monthly_trends['YearMonth'].astype(str)
print(monthly_trends[['YearMonth_Str', 'Revenue', 'Orders', 'Units_Sold', 'Active_Customers']].to_string(index=False))

print("\n4. Analyzing Top Countries by Revenue...")
geo_summary = df_clean.groupby('Country').agg(
    Revenue=('Revenue', 'sum'),
    Orders=('InvoiceNo', 'nunique'),
    Units_Sold=('Quantity', 'sum'),
    Customers=('CustomerID', 'nunique')
).reset_index()
geo_summary['AOV'] = (geo_summary['Revenue'] / geo_summary['Orders']).round(2)
geo_summary['Revenue_Share_%'] = ((geo_summary['Revenue'] / df_clean['Revenue'].sum()) * 100).round(2)
geo_summary = geo_summary.sort_values(by='Revenue', ascending=False).reset_index(drop=True)
print(geo_summary.head(10).to_string(index=False))

print("\n5. Analyzing Top 10 Products by Revenue...")
top_products_rev = df_clean.groupby(['StockCode', 'Description']).agg(
    Total_Revenue=('Revenue', 'sum'),
    Units_Sold=('Quantity', 'sum'),
    Total_Orders=('InvoiceNo', 'nunique')
).reset_index().sort_values(by='Total_Revenue', ascending=False).head(10)
print(top_products_rev.to_string(index=False))

print("\n6. Analyzing Average Order Value (AOV)...")
order_summary = df_clean.groupby('InvoiceNo').agg(
    Order_Revenue=('Revenue', 'sum'),
    Items_Count=('Quantity', 'sum')
).reset_index()
print(f"Overall Mean AOV: £{order_summary['Order_Revenue'].mean():.2f}")
print(f"Overall Median AOV: £{order_summary['Order_Revenue'].median():.2f}")

print("\nAnalysis complete!")

