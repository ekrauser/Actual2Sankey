import pandas as pd
import plotly.graph_objects as go

# Step 1: Load the CSV data
csv_file = '2024statement.csv'  # Replace with your CSV file path
df = pd.read_csv(csv_file)

# Step 2: Process and prepare data for Sankey diagram
# Extract main categories for simplicity
df['MainCategory'] = df['Category'].apply(lambda x: x.split('/')[0])

# Aggregate by category
aggregated_data = df.groupby('MainCategory').sum(numeric_only=True).reset_index()

# Separate income and expenses
income_categories = aggregated_data[aggregated_data['Amount'] > 0]
expense_categories = aggregated_data[aggregated_data['Amount'] < 0]

# Sankey source and target nodes
categories = list(aggregated_data['MainCategory'])
categories.append('Total Income')
categories.append('Total Expenses')

source = []
target = []
value = []

# Add income connections
for i, row in income_categories.iterrows():
    source.append(categories.index(row['MainCategory']))
    target.append(categories.index('Total Income'))
    value.append(row['Amount'])

# Add expense connections
for i, row in expense_categories.iterrows():
    source.append(categories.index('Total Income'))
    target.append(categories.index(row['MainCategory']))
    value.append(-row['Amount'])

# Step 3: Create Sankey diagram
sankey_fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=categories
    ),
    link=dict(
        source=source,
        target=target,
        value=value
    )
)])

# Update layout
sankey_fig.update_layout(title_text="2024 Primary Cash Flow Sankey", font_size=10)
sankey_fig.show()
