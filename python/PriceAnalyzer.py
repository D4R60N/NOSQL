import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient

mongo_user = "user"
mongo_password = "user"
mongo_db = "Transparency"
mongo_collection = "Prices"

client = MongoClient(f"mongodb://{mongo_user}:{mongo_password}@127.0.0.1:27117,127.0.0.1:27118/?authMechanism=DEFAULT")
db = client[mongo_db]
collection = db[mongo_collection]

# Load data from MongoDB
data = list(collection.find())

# Convert to DataFrame
df = pd.DataFrame(data)

df.drop(columns=['_id'], inplace=True, errors='ignore')

# Convert time column to datetime format
df['MTU (CET/CEST)'] = df['MTU (CET/CEST)'].str.split(' - ').str[0]
df['MTU (CET/CEST)'] = df['MTU (CET/CEST)'].str.strip()
df['MTU (CET/CEST)'] = pd.to_datetime(df['MTU (CET/CEST)'], format='%d/%m/%Y %H:%M:%S', errors='coerce')

df.rename(columns={
    'Day-ahead Price (EUR/MWh)': 'Day-ahead_Price',
}, inplace=True)

# Count non-numeric values in Day-ahead price before conversion
non_numeric_price = df['Day-ahead_Price'].apply(pd.to_numeric, errors='coerce').isna().sum()

print()
print("Missing actual:")
print(non_numeric_price)

df['Day-ahead_Price'] = pd.to_numeric(df['Day-ahead_Price'], errors='coerce')
df.dropna(subset=['Day-ahead_Price'], inplace=True)

# Summary statistics
print("Summary Statistics:")
print(df[['Day-ahead_Price']].describe())


# Select only numeric columns
df_numeric = df[['MTU (CET/CEST)', 'Day-ahead_Price']]

# Resample the data to weekly averages
df_weekly = df_numeric.resample('W', on='MTU (CET/CEST)').mean()

# Plot daily average actual vs forecasted load
df_weekly[['Day-ahead_Price']].plot(figsize=(12, 6), marker='o', linestyle='-')
plt.title('Weekly Average: Price')
plt.xlabel('Date')
plt.ylabel('Price (EUR/MWh)')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.show()