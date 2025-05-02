import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pymongo import MongoClient

# MongoDB setup
mongo_user = "user"
mongo_password = "user"
mongo_db = "Transparency"

client = MongoClient(f"mongodb://{mongo_user}:{mongo_password}@127.0.0.1:27117,127.0.0.1:27118/?authMechanism=DEFAULT")
db = client[mongo_db]

# ------------------- Load Analysis -------------------
load_collection = db["Load"]
load_data = list(load_collection.find())
df_load = pd.DataFrame(load_data)
df_load.drop(columns=['_id'], inplace=True, errors='ignore')
df_load['MTU (CET/CEST)'] = df_load['MTU (CET/CEST)'].str.split(' - ').str[0].str.strip()
df_load['MTU (CET/CEST)'] = pd.to_datetime(df_load['MTU (CET/CEST)'], format='%d/%m/%Y %H:%M:%S', errors='coerce')

df_load.rename(columns={
    'Actual Total Load (MW)': 'Actual_Load',
    'Day-ahead Total Load Forecast (MW)': 'Forecast_Load'
}, inplace=True)

df_load['Actual_Load'] = pd.to_numeric(df_load['Actual_Load'], errors='coerce')
df_load['Forecast_Load'] = pd.to_numeric(df_load['Forecast_Load'], errors='coerce')
df_load.dropna(subset=['Actual_Load', 'Forecast_Load'], inplace=True)

df_weekly_load = df_load[['MTU (CET/CEST)', 'Actual_Load', 'Forecast_Load']].resample('W', on='MTU (CET/CEST)').sum()

def millions2(x, pos):
    return f'{x * 1e-6:.2f}M'

df_weekly_load[['Actual_Load', 'Forecast_Load']].plot(figsize=(12, 6), marker='o')
plt.title('Weekly Average: Actual vs Forecasted Load')
plt.ylabel('Load (MW)')
plt.gca().yaxis.set_major_formatter(FuncFormatter(millions2))
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

df_weekly_load['Forecast_Error'] = df_weekly_load['Actual_Load'] - df_weekly_load['Forecast_Load']
df_weekly_load['Forecast_Error'].plot(figsize=(12, 6), color='red', marker='o')
plt.title('Weekly Average Forecast Error Over Time')
plt.ylabel('Error (MW)')
plt.grid()
plt.tight_layout()
plt.show()

# ------------------- Price Analysis -------------------
price_collection = db["Prices"]
price_data = list(price_collection.find())
df_price = pd.DataFrame(price_data)
df_price.drop(columns=['_id'], inplace=True, errors='ignore')
df_price['MTU (CET/CEST)'] = df_price['MTU (CET/CEST)'].str.split(' - ').str[0].str.strip()
df_price['MTU (CET/CEST)'] = pd.to_datetime(df_price['MTU (CET/CEST)'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
df_price.rename(columns={'Day-ahead Price (EUR/MWh)': 'Day-ahead_Price'}, inplace=True)

df_price['Day-ahead_Price'] = pd.to_numeric(df_price['Day-ahead_Price'], errors='coerce')
df_price.dropna(subset=['Day-ahead_Price'], inplace=True)

df_weekly_price = df_price[['MTU (CET/CEST)', 'Day-ahead_Price']].resample('W', on='MTU (CET/CEST)').mean()
df_weekly_price.plot(figsize=(12, 6), marker='o')
plt.title('Weekly Average: Day-ahead Price')
plt.ylabel('Price (EUR/MWh)')
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# ------------------- Production Analysis -------------------
production_collection = db["Production"]
production_data = list(production_collection.find())
df_prod = pd.DataFrame(production_data)
df_prod.drop(columns=['_id'], inplace=True, errors='ignore')
df_prod['MTU (CET/CEST)'] = df_prod['MTU (CET/CEST)'].str.split(' - ').str[0]
df_prod['MTU (CET/CEST)'] = pd.to_datetime(df_prod['MTU (CET/CEST)'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
df_prod['Generation (MW)'] = pd.to_numeric(df_prod['Generation (MW)'], errors='coerce')
df_prod.dropna(subset=['Generation (MW)'], inplace=True)

prod_stats = df_prod.groupby('Production Type')['Generation (MW)'].agg(['sum', 'mean', 'median', 'min', 'max', 'std'])
print("\nProduction Statistics by Production Type:")
print(prod_stats)

plt.gca().yaxis.set_major_formatter(FuncFormatter(millions2))
df_prod.groupby('Production Type')['Generation (MW)'].sum().sort_values().plot(kind='bar', color='skyblue', figsize=(12,6))
plt.title('Total Generation by Production Type')
plt.xticks(rotation=90)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

df_prod.groupby('Production Type')['Generation (MW)'].mean().sort_values().plot(kind='bar', color='lightcoral', figsize=(12,6))
plt.title('Average Generation by Production Type')
plt.xticks(rotation=90)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

df_prod.set_index('MTU (CET/CEST)', inplace=True)
weekly_gen = df_prod.resample('W')['Generation (MW)'].sum()
plt.gca().yaxis.set_major_formatter(FuncFormatter(millions2))
weekly_gen.plot(color='green', marker='o', figsize=(12, 6))
plt.title('Weekly Generation Totals')
plt.xlabel('Date')
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

df_prod['Month'] = df_prod.index.to_period('M').start_time
monthly_pivot = df_prod.pivot_table(values='Generation (MW)', index='Month', columns='Production Type', aggfunc='sum', fill_value=0)
monthly_pivot.plot(kind='bar', stacked=True, figsize=(12, 6), colormap='tab20')
plt.gca().yaxis.set_major_formatter(FuncFormatter(millions2))
plt.title('Monthly Production Type Distribution')
plt.xticks(rotation=90)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.legend(title='Production Type', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
