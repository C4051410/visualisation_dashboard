import pandas as pd
import numpy as np
import altair as alt

# 1. Data Loading and Preparation
df = pd.read_csv('country_economics_data.csv')

# Select at least 7 attributes for the visualization to meet the brief criteria
cols_to_keep = [
    'Name',
    'Region',
    'Population_millions',
    'Area_km2',
    'GDP_billionUSD',
    'Inflation Rate_percent',
    'Jobless Rate_percent'
]

# Clean data: drop rows missing our key visualization metrics
df_clean = df.dropna(subset=cols_to_keep).copy()

# Feature Engineering: Create a derived attribute (Population Density - people per km2)
df_clean['Population_Density'] = (df_clean['Population_millions'] * 1000000) / df_clean['Area_km2']

# 2. Define Interactivity
# Brush selection for cross-filtering between charts
brush = alt.selection_interval(resolve='global')

# Dropdown selection for the general public to filter by Region
regions = [None] + list(df_clean['Region'].dropna().unique())
region_labels = ['All Regions'] + list(df_clean['Region'].dropna().unique())
region_dropdown = alt.binding_select(options=regions, labels=region_labels, name="Highlight Region: ")
region_select = alt.selection_point(fields=['Region'], bind=region_dropdown)

# 3. View 1: Main Scatter Plot (Economic vs. Demographic)
scatter = alt.Chart(df_clean).mark_circle().encode(
    x=alt.X('GDP_billionUSD:Q', title='GDP (Billion USD, Log Scale)', scale=alt.Scale(type='symlog')),
    y=alt.Y('Inflation Rate_percent:Q', title='Inflation Rate (%)'),
    size=alt.Size('Population_millions:Q', title='Population (Millions)', scale=alt.Scale(range=[20, 1000])),
    color=alt.condition(brush, 'Region:N', alt.value('lightgray'), legend=alt.Legend(title="Region")),
    opacity=alt.condition(region_select, alt.value(0.8), alt.value(0.1)),
    tooltip=[
        'Name',
        'Region',
        'Population_millions',
        alt.Tooltip('Population_Density:Q', format='.2f'),
        'GDP_billionUSD',
        'Inflation Rate_percent'
    ]
).add_params(
    brush,
    region_select
).properties(
    width=800,
    height=500,
    title="Global Economic Health vs. Population Size"
)

# 4. View 2: Regional Bar Chart (Aggregation)
bar = alt.Chart(df_clean).mark_bar().encode(
    x=alt.X('mean(Population_Density):Q', title='Average Population Density'),
    y=alt.Y('Region:N', sort='-x', title=None),
    color=alt.Color('Region:N', legend=None),
    tooltip=['Region', alt.Tooltip('mean(Population_Density):Q', format='.2f')]
).transform_filter(
    brush  # Updates based on user selection in the scatter plot
).properties(
    width=400,
    height=500,
    title="Average Population Density by Region"
)

# 5. View 3: Distribution Histogram (Economic Metric)
histogram = alt.Chart(df_clean).mark_bar().encode(
    x=alt.X('Jobless Rate_percent:Q', bin=alt.Bin(maxbins=40), title='Jobless Rate (%)'),
    y=alt.Y('count():Q', title='Number of Countries'),
    color=alt.value('#4c78a8')
).transform_filter(
    brush
).transform_filter(
    region_select
).properties(
    width=1280,
    height=250,
    title="Distribution of Jobless Rates Across Selected Countries"
)

# 6. Assemble the Dashboard Layout
# Structured to fit within a 1920x1080 resolution screen
dashboard = alt.vconcat(
    alt.hconcat(scatter, bar, spacing=40),
    histogram,
    spacing=30
).resolve_scale(
    color='independent',
    size='independent'
).configure_view(
    strokeWidth=0
).configure_title(
    fontSize=20,
    font='Arial',
    anchor='start',
    color='#333333'
).configure_axis(
    labelFontSize=12,
    titleFontSize=14,
    gridOpacity=0.4
)

# 7. Export to HTML
# Saves a standalone, self-explanatory HTML file
dashboard.save('index.html')
print("Dashboard successfully generated as 'index.html'. Open this file in your web browser to view.")