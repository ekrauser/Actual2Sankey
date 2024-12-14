import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime, timedelta

# Step 1: Load and preprocess the data
csv_file = 'statement.csv'  # Replace with your CSV file path
columns_to_keep = ['Date', 'Category', 'Amount']
df = pd.read_csv(csv_file, usecols=columns_to_keep)

# Filter transactions to include only the last 12 months
today = datetime.today()
one_year_ago = today - timedelta(days=365)

df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])  # Drop rows with invalid dates
df = df[(df['Date'] >= one_year_ago) & (df['Date'] <= today)]

# Step 2: Categorize transactions and calculate Debt totals
df['MainCategory'] = df['Category'].apply(lambda x: str(x).split('/')[0] if isinstance(x, str) else 'Unknown')
debt_categories = ['Debt']  # Add specific debt categories as needed
debt_data = df[df['MainCategory'].isin(debt_categories)]  # Isolate Debt category
debt_total = -debt_data['Amount'].sum()  # Convert to positive

# Exclude Debt from main data
df = df[~df['MainCategory'].isin(debt_categories)]

# Aggregate data
aggregated_data = df.groupby('MainCategory').sum(numeric_only=True).reset_index()

# Format values for display
aggregated_data['FormattedAmount'] = aggregated_data['Amount'].apply(lambda x: f"${x:,.2f}")

# Calculate totals
total_income = aggregated_data[aggregated_data['Amount'] > 0]['Amount'].sum()
total_expenses = -aggregated_data[aggregated_data['Amount'] < 0]['Amount'].sum()  # Convert to positive
starting_balance = 1000  # Replace with actual starting balance if available
grand_total_income = total_income + starting_balance

# Prepare categories and labels
categories = list(aggregated_data['MainCategory'])
categories.append("Total Income")

# Append dollar values to node labels
category_labels = [
    f"{cat} ({aggregated_data.loc[aggregated_data['MainCategory'] == cat, 'FormattedAmount'].values[0]})"
    if cat in aggregated_data['MainCategory'].values else
    f"Total Income (${grand_total_income:,.2f})"
    for cat in categories
]

source = []
target = []
value = []

# Add flows for income
income_categories = aggregated_data[aggregated_data['Amount'] > 0]
expense_categories = aggregated_data[aggregated_data['Amount'] < 0]

for _, row in income_categories.iterrows():
    source.append(categories.index(row['MainCategory']))
    target.append(categories.index("Total Income"))
    value.append(row['Amount'])

for _, row in expense_categories.iterrows():
    source.append(categories.index("Total Income"))
    target.append(categories.index(row['MainCategory']))
    value.append(-row['Amount'])

# Step 3: Create the Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=20,
        thickness=20,
        line=dict(color="rgba(200, 200, 200, 0.5)", width=1),
        label=category_labels,
        color=["#1f77b4" if idx < len(categories) - 1 else "#ff7f0e" for idx in range(len(categories))]
    ),
    link=dict(
        source=source,
        target=target,
        value=value,
        color=["rgba(31, 119, 180, 0.7)" if val > 0 else "rgba(255, 127, 14, 0.7)" for val in value]
    )
)])

# Step 4: Add annotations for totals
fig.add_annotation(
    x=0,  # Place on the left side of the diagram
    y=0.2,   # Adjust for placement
    text=f"Total Income: ${grand_total_income:,.2f}",
    showarrow=False,
    font=dict(size=14, color="white"),
    align="left"
)

fig.add_annotation(
    x=0,  # Same x-position as above
    y=0.25,   # Slightly lower for the expense total
    text=f"Total Expenses: ${total_expenses:,.2f}",
    showarrow=False,
    font=dict(size=14, color="white"),
    align="left"
)

fig.add_annotation(
    x=0,  # Same x-position as above
    y=0.3,   # Slightly lower for the debt total
    text=f"Total Debt: ${debt_total:,.2f}",
    showarrow=False,
    font=dict(size=14, color="white"),
    align="left"
)

# Step 5: Customize appearance
fig.update_layout(
    title_text="2024 Cash Flow",
    title_font=dict(size=18, color="white"),
    font=dict(family="Arial", size=12, color="white"),
    plot_bgcolor="#111111",
    paper_bgcolor="#111111"
)

# Step 6: Save as a high-quality image using Orca
output_file = 'financial_sankey_orca.png'

try:
    print("Attempting to save image using Orca...")
    pio.write_image(fig, output_file, format='png', engine='orca', width=1600, height=900, scale=2)
    print(f"Sankey diagram saved as {output_file}")
except Exception as e:
    print(f"Error saving image with Orca: {e}")
