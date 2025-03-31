import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient

mongo_user = "user"
mongo_password = "user"
mongo_db = "Transparency"
mongo_collection = "Load"

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
df['MTU (CET/CEST)'] = pd.to_datetime(df['MTU (CET/CEST)'], format='%d/%m/%Y %H:%M', errors='coerce')

df.rename(columns={
    'Actual Total Load (MW)': 'Actual_Load',
    'Day-ahead Total Load Forecast (MW)': 'Forecast_Load'
}, inplace=True)

# Count non-numeric values in Actual load before conversion
non_numeric_actual = df['Actual_Load'].apply(pd.to_numeric, errors='coerce').isna().sum()

# Count non-numeric values in Forecast load before conversion
non_numeric_forecast = df['Forecast_Load'].apply(pd.to_numeric, errors='coerce').isna().sum()
print()
print("Missing forecast:")
print(non_numeric_forecast)
print("Missing actual:")
print(non_numeric_actual)

df['Actual_Load'] = pd.to_numeric(df['Actual_Load'], errors='coerce')
df['Forecast_Load'] = pd.to_numeric(df['Forecast_Load'], errors='coerce')
df.dropna(subset=['Actual_Load', 'Forecast_Load'], inplace=True)

# Summary statistics
print("Summary Statistics:")
print(df[['Forecast_Load']].describe())
print(df[['Actual_Load']].describe())


# Select only numeric columns
df_numeric = df[['MTU (CET/CEST)', 'Actual_Load', 'Forecast_Load']]

# Resample the data to weekly averages
df_weekly = df_numeric.resample('W', on='MTU (CET/CEST)').mean()

# Plot daily average actual vs forecasted load
df_weekly[['Actual_Load', 'Forecast_Load']].plot(figsize=(12, 6), marker='o', linestyle='-')
plt.title('Weekly Average: Actual vs Forecasted Load')
plt.xlabel('Date')
plt.ylabel('Load (MW)')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.show()

# Calculate and plot daily average forecast error
df_weekly['Forecast_Error'] = df_weekly['Actual_Load'] - df_weekly['Forecast_Load']
df_weekly['Forecast_Error'].plot(figsize=(12, 6), color='red', marker='o', linestyle='-')
plt.title('Weekly Average Forecast Error Over Time')
plt.xlabel('Date')
plt.ylabel('Error (MW)')
plt.grid()
plt.show()