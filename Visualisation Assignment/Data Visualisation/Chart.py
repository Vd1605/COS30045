# Please check the OECD_Dashboard_Instrucitons.txt for instructions on how to run this code.
# This code creates an interactive dashboard using Plotly Dash to visualize OECD patent data.
import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# Data Preprocessing and Cleaning for OECD Patent Dataset
# ---------------------------------------------------
# 1. Load the CSV data
# 2. Handle missing values
# 3. Standardise formats (e.g., country names, years)
# 4. Transform data for dashboard use (pivot, aggregation)
# 5. Save cleaned data for dashboard use

# Load the data
df = pd.read_csv('OECD.STI.PIE,DSD_PATENTS@DF_PATENTS,1.0+.A...PRIORITY...INVENTOR..._T.csv', skiprows=0)

# Select relevant columns for analysis
columns_of_interest = [
    'REF_AREA', 'Reference area', 'TIME_PERIOD', 'Time period',
    'OBS_VALUE', 'Observation value', 'UNIT_MEASURE', 'Unit of measure',
    'OECD_TECHNOLOGY_PATENT', 'Selected OECD technology domains',
    'PATENT_AUTHORITIES', 'Patent authorities'
]
# Some columns may be missing in some rows, so use .get for safety
df = df[[col for col in columns_of_interest if col in df.columns]]

# Rename columns for easier access
df = df.rename(columns={
    'REF_AREA': 'Country_Code',
    'Reference area': 'Country',
    'TIME_PERIOD': 'Year',
    'Time period': 'Year2',
    'OBS_VALUE': 'Value',
    'Observation value': 'Value2',
    'UNIT_MEASURE': 'Unit',
    'Unit of measure': 'Unit2',
    'OECD_TECHNOLOGY_PATENT': 'Tech_Domain',
    'Selected OECD technology domains': 'Tech_Domain2',
    'PATENT_AUTHORITIES': 'Patent_Office',
    'Patent authorities': 'Patent_Office2'
})

# Prefer non-null values between duplicate columns
df['Country'] = df['Country'].combine_first(df['Country_Code'])
df['Year'] = df['Year'].combine_first(df['Year2'])
df['Value'] = df['Value'].combine_first(df['Value2'])
df['Unit'] = df['Unit'].combine_first(df['Unit2'])
df['Tech_Domain'] = df['Tech_Domain'].combine_first(df['Tech_Domain2'])
df['Patent_Office'] = df['Patent_Office'].combine_first(df['Patent_Office2'])

# Drop duplicate columns
df = df.drop(columns=['Country_Code', 'Year2', 'Value2', 'Unit2', 'Tech_Domain2', 'Patent_Office2'], errors='ignore')

# Handle missing values
# Convert Value to numeric, coerce errors to NaN
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
# Drop rows with missing country, year, or value
df = df.dropna(subset=['Country', 'Year', 'Value'])

# Standardise year to integer
df['Year'] = df['Year'].astype(int)

# Standardise country names (strip whitespace)
df['Country'] = df['Country'].str.strip()

# Only keep data for years 2020 and 2021 (no decimals)
df = df[df['Year'].isin([2020, 2021])]
df = df[df['Year'] == df['Year'].astype(int)]
df['Year'] = df['Year'].astype(int)

# Optional: Aggregate by country and year (sum values)
df_agg = df.groupby(['Country', 'Year', 'Patent_Office', 'Tech_Domain', 'Unit'], as_index=False)['Value'].sum()

# Save cleaned data for dashboard use
df_agg.to_csv('cleaned_patent_data.csv', index=False)

# Documented steps above. Next: dashboard implementation.

# --- Interactive Dashboard Implementation ---
# This section creates a Plotly Dash dashboard with interactive graphs.
# The dashboard allows filtering by country and year, and links interactions between graphs.

# Load the cleaned data
df = pd.read_csv('cleaned_patent_data.csv')

# Get unique countries and years for dropdowns
countries = sorted(df['Country'].unique())
years = sorted(df['Year'].unique())

# Create Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('OECD Patent Data Dashboard'),
    html.Div([
        html.Label('Select Country:'),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': c, 'value': c} for c in countries],
            value=countries[0],
            multi=False
        ),
        html.Label('Select Year:'),
        dcc.Checklist(
            id='year-dropdown',
            options=[{'label': y, 'value': y} for y in years],
            value=[years[-1]],
            inline=True,
            inputStyle={"margin-right": "8px", "margin-left": "16px"},
            style={"margin-bottom": "16px"}
        )
    ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    html.Div([
        dcc.Graph(id='bar-chart'),
        dcc.Graph(id='grouped-bar-chart')
    ], style={'width': '68%', 'display': 'inline-block', 'paddingLeft': '2%'})
])

# Callback for interactive filtering and linking
def filter_data(country, years_selected):
    dff = df.copy()
    if country:
        dff = dff[dff['Country'] == country]
    if years_selected:
        dff = dff[dff['Year'].isin(years_selected)]
    return dff

@app.callback(
    Output('bar-chart', 'figure'),
    Output('grouped-bar-chart', 'figure'),
    Input('country-dropdown', 'value'),
    Input('year-dropdown', 'value')
)
def update_graphs(selected_country, selected_years):
    # If no country is selected, return figures with a centered message
    if not selected_country:
        message = "Choose any country to display visualisations"
        empty_fig = px.scatter()
        empty_fig.update_layout(
            xaxis={'visible': False},
            yaxis={'visible': False},
            annotations=[{
                'text': message,
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 22, 'color': '#3a0ca3'},
                'x': 0.5,
                'y': 0.5,
                'xanchor': 'center',
                'yanchor': 'middle',
            }],
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='#f8f9fa',
        )
        return empty_fig, empty_fig

    dff = filter_data(selected_country, selected_years)

    # Pie charts for 2020 and 2021 in a single figure (subplot)
    pie_fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                            subplot_titles=[f"2020 ({selected_country})", f"2021 ({selected_country})"])
    # Get consistent color mapping for Patent_Office
    unique_offices = sorted(df['Patent_Office'].unique())
    color_map = px.colors.qualitative.Plotly
    office_color_dict = {office: color_map[i % len(color_map)] for i, office in enumerate(unique_offices)}

    for idx, year in enumerate([2020, 2021]):
        year_df = dff[dff['Year'] == year]
        if not year_df.empty:
            offices = year_df['Patent_Office'].values
            values = year_df['Value'].values
            total = values.sum()
            percent = [round((val / total * 100), 1) if total else 0.0 for val in values]
            marker_colors = [office_color_dict.get(office, '#888') for office in offices]
            pie = go.Pie(
                labels=offices,  # legend entries: patent office
                values=values,
                name=str(year),
                hole=0.35,
                textinfo='percent',  # data label: percent only
                pull=[0.05]*len(offices),
                marker=dict(line=dict(color='#fff', width=2), colors=marker_colors),
                hovertemplate="<b>%{label}</b><br>Patents: %{value}<br>Percent of Patents: %{customdata}%<extra></extra>",
                customdata=percent,
                legendgroup='patent_office',
                showlegend=(idx == 0),
            )
            pie_fig.add_trace(pie, 1, idx+1)
        else:
            # Add an empty pie with annotation
            pie_fig.add_trace(go.Pie(labels=[], values=[]), 1, idx+1)
            pie_fig.add_annotation(
                text=f'No data for {year}',
                x=0.25 if idx == 0 else 0.75,
                y=0.5,
                xref='paper',
                yref='paper',
                showarrow=False,
                font=dict(size=18, color='#3a0ca3'),
                xanchor='center',
                yanchor='middle',
            )
    pie_fig.update_layout(
        title_text=f'Percentage of Patents by Patent Authorities (2020 & 2021, {selected_country})',
        title_font=dict(size=20, color='#3a0ca3', family='Segoe UI, Arial'),
        font=dict(family='Segoe UI, Arial', size=15, color='#2a3f5f'),
        legend=dict(
            title_text='Patent Authorities',
            bgcolor='rgba(255,255,255,0.7)',
            bordercolor='#e0e7ff',
            borderwidth=1
        ),
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='#f8f9fa',
        margin=dict(l=30, r=30, t=60, b=30)
    )

    # Column chart: Year on x-axis, colored by Patent Office, grouped (not stacked)
    column_df = dff.groupby(['Year', 'Patent_Office'], as_index=False)['Value'].sum()
    column_fig = px.bar(
        column_df,
        x='Year',
        y='Value',
        color='Patent_Office',
        barmode='group',
        title='Number of Patents by Year and Patent Authorities ({}{})'.format(
            selected_country,
            (', ' + ', '.join(map(str, selected_years))) if selected_years else ''
        ),
        hover_data={'Patent_Office': True, 'Year': True, 'Value': True},
        labels={'Value': 'Number of Patents', 'Year': 'Year', 'Patent_Office': 'Patent Office'}
    )
    column_fig.update_layout(
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='#f8f9fa',
        font=dict(family='Segoe UI, Arial', size=15, color='#2a3f5f'),
        legend=dict(
            title_text='Patent Authorities',
            bgcolor='rgba(255,255,255,0.7)',
            bordercolor='#e0e7ff',
            borderwidth=1
        ),
        bargap=0.18,
        bargroupgap=0.08,
        title_font=dict(size=22, color='#3a0ca3', family='Segoe UI, Arial'),
        xaxis=dict(title='Year', showgrid=False, zeroline=False, tickmode='linear'),
        yaxis=dict(title='Number of Patents', gridcolor='#e0e7ff', zeroline=False)
    )
    column_fig.update_traces(marker_line_width=1.5, marker_line_color='#fff', opacity=0.92)
    return pie_fig, column_fig

if __name__ == '__main__':
    app.run(debug=True)
