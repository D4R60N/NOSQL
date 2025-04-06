import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
from pymongo import MongoClient

mongo_user = "user"
mongo_password = "user"
mongo_db = "Transparency"
mongo_collection = "Production"

client = MongoClient(f"mongodb://{mongo_user}:{mongo_password}@127.0.0.1:27117,127.0.0.1:27118/?authMechanism=DEFAULT")
db = client[mongo_db]
collection = db[mongo_collection]

# Load data from MongoDB
data = list(collection.find())

# Convert to DataFrame
df = pd.DataFrame(data)

df.drop(columns=['_id'], inplace=True, errors='ignore')

# Convert the MTU (CET/CEST) column to datetime (extract the first timestamp)
df['MTU (CET/CEST)'] = df['MTU (CET/CEST)'].str.split(' - ').str[0]
df['MTU (CET/CEST)'] = pd.to_datetime(df['MTU (CET/CEST)'], format='%d/%m/%Y %H:%M:%S', errors='coerce')

# Convert 'Generation (MW)' to numeric, forcing errors to NaN (for "n/e" values)
df['Generation (MW)'] = pd.to_numeric(df['Generation (MW)'], errors='coerce')

# Drop rows with missing generation values (if any)
df.dropna(subset=['Generation (MW)'], inplace=True)

# Basic statistics on generation by production type
production_stats = df.groupby('Production Type')['Generation (MW)'].agg(['sum', 'mean', 'median', 'min', 'max', 'std'])

# Print the production statistics
print("Production Statistics by Production Type:")
print(production_stats)

# Formatter for millions
def millions(x, pos):
    return f'{x * 1e-6:.0f}M'  # Convert to millions and add 'M'

# Apply the formatter to the Y-axis
plt.gca().yaxis.set_major_formatter(FuncFormatter(millions))

# Plot the total generation by production type (bar plot)
production_totals = df.groupby('Production Type')['Generation (MW)'].sum().sort_values(ascending=False)
production_totals.plot(kind='bar', figsize=(12, 6), color='skyblue')
plt.title('Total Generation by Production Type')
plt.xlabel('Production Type')
plt.ylabel('Total Generation (MW)')
plt.xticks(rotation=90)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# Plot the mean generation by production type (bar plot)
production_mean = df.groupby('Production Type')['Generation (MW)'].mean().sort_values(ascending=False)
production_mean.plot(kind='bar', figsize=(12, 6), color='lightcoral')
plt.title('Average Generation by Production Type')
plt.xlabel('Production Type')
plt.ylabel('Average Generation (MW)')
plt.xticks(rotation=90)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# Set the index to 'MTU (CET/CEST)' for time-based resampling
df.set_index('MTU (CET/CEST)', inplace=True)

# Resample to weekly frequency and calculate the sum of Generation (MW) for each week
weekly_generation = df.resample('W')['Generation (MW)'].sum()

# Formatter for millions with two decimal places
def millions2(x, pos):
    return f'{x * 1e-6:.2f}M'  # Convert to millions and add 'M'

# Apply the formatter to the Y-axis
plt.gca().yaxis.set_major_formatter(FuncFormatter(millions2))

# Plot weekly generation totals (line plot)
weekly_generation.plot(figsize=(12, 6), color='green', marker='o', linestyle='-')
plt.title('Weekly Generation Totals')
plt.xlabel('Date')
plt.ylabel('Total Generation (MW)')
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# Create a 'Month' column based on the index (MTU)
df['Month'] = df.index.to_period('M').start_time

monthly_pivot = df.pivot_table(
    values='Generation (MW)',
    index='Month',
    columns='Production Type',
    aggfunc='sum',
    fill_value=0
)

# Plot the monthly production type distribution as a stacked bar plot
monthly_pivot.plot(kind='bar', stacked=True, figsize=(12, 6), colormap='tab20')
plt.gca().yaxis.set_major_formatter(FuncFormatter(millions2))
plt.title('Monthly Production Type Distribution Over Time')
plt.xlabel('Date')
plt.ylabel('Generation (MW)')
plt.xticks(rotation=90)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.legend(title='Production Type', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
