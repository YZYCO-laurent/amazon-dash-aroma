import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px

# Load data
def load_data(file_path):
    df = pd.read_csv(file_path, parse_dates=['Date'], dayfirst=True)
    df['Week'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time)
    df['Units Sold'] = 1  # Assuming each row is a unit sold, modify as needed
    return df

# Initial load
data_file = 'transactions 20205.csv'
df = load_data(data_file)

# Initialize app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload CSV'),
        multiple=False
    ),
    dcc.Graph(id='weekly-transactions'),
    dcc.Graph(id='weekly-units-sold'),
    dash_table.DataTable(
        id='transaction-table',
        columns=[{'name': col, 'id': col} for col in df.columns],
        data=df.to_dict('records'),
        page_size=10
    )
], style={'fontFamily': 'Arial', 'margin': '20px'})

# Callbacks
@app.callback(
    [Output('weekly-transactions', 'figure'),
     Output('weekly-units-sold', 'figure'),
     Output('transaction-table', 'data')],
    Input('upload-data', 'contents')
)
def update_dashboard(contents):
    global df
    if contents:
        df = load_data(data_file)
    
    weekly_summary = df.groupby('Week').agg({'Total (EUR)': 'sum', 'Units Sold': 'sum'}).reset_index()
    
    fig_amount = px.line(weekly_summary, x='Week', y='Total (EUR)', title='Weekly Transaction Totals',
                         template='plotly_white', markers=True, line_shape='spline')
    fig_amount.update_layout(
        xaxis_title='Week',
        yaxis_title='Total (EUR)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='lightgrey')
    )
    
    fig_units = px.line(weekly_summary, x='Week', y='Units Sold', title='Weekly Units Sold',
                         template='plotly_white', markers=True, line_shape='spline')
    fig_units.update_layout(
        xaxis_title='Week',
        yaxis_title='Units Sold',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='lightgrey')
    )
    
    return fig_amount, fig_units, df.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)
