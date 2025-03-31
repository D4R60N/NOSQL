import json
import pandas as pd
import matplotlib.pyplot as plt

# Load the JSON file
file_path = "../data/Transparency.Load.json"
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Convert to DataFrame
df = pd.DataFrame(data)

# Print exact column names to debug
print("Exact Column Names:", list(df.columns))
print(df.head())

# Strip column names of whitespace
df.columns = df.columns.str.strip()

# Convert time column to datetime format
df['MTU (CET/CEST)'] = df['MTU (CET/CEST)'].str.split(' - ').str[0]
df['MTU (CET/CEST)'] = df['MTU (CET/CEST)'].str.strip()
df['MTU (CET/CEST)'] = pd.to_datetime(df['MTU (CET/CEST)'], format='%d/%m/%Y %H:%M:%S', errors='coerce')

# Rename columns for easier access
df.rename(columns=lambda x: x.strip(), inplace=True)
df.rename(columns={
    'Generation (MW)': 'Generation',
    'Production Type': 'Production_Type'
}, inplace=True)

# Check if required columns exist
if 'Production_Type' not in df.columns or 'Generation' not in df.columns:
    print("Error: Required columns not found in the DataFrame. Available columns:", list(df.columns))
    exit()

# Check for missing values
print("Missing values:")
print(df[['Production_Type', 'Generation']].isnull().sum())

# Summary statistics
print("Summary Statistics:")
print(df.groupby('Production_Type')['Generation'].describe())

# Plot total generation over time
df_grouped = df.groupby(['MTU (CET/CEST)', 'Production_Type'])['Generation'].sum().unstack()
df_grouped.plot(figsize=(12, 6))
plt.title('Electricity Generation by Production Type Over Time')
plt.xlabel('Time')
plt.ylabel('Generation (MW)')
plt.legend(title='Production Type')
plt.grid()
plt.show()
