import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px

data_dir = 'data/plays/'

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def round_percentiles(df, columns, decimals=2):
    """
    Rounds the specified columns in the dataframe to the given number of decimal places.
    """
    for column in columns:
        df[column] = df[column].round(decimals)
    return df

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("NBA Player Play Type Analysis"),
            html.Div([
                dcc.Input(id='player-name', type='text', placeholder='Enter player name', debounce=True),
                dcc.Input(id='season-year', type='number', placeholder='Enter season year (e.g., 2024)', debounce=True),
                html.Button('Submit', id='submit-button', n_clicks=0)
            ], className='input-group'),
            html.Br(),
            html.Div(id='player-table', className='data-table')
        ], width=12)
    ])
], fluid=True)

@app.callback(
    Output('player-table', 'children'),
    [Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('player-name', 'value'),
     dash.dependencies.State('season-year', 'value')]
)
def update_table(n_clicks, player_name, season_year):
    if not player_name or not season_year:
        return None

    file_path = f'{data_dir}NBA_{season_year}_Plays.csv'

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return html.Div("File not found for the specified season year.", style={'color': 'red'})

    player_df = df[df['PLAYER_NAME'].str.contains(player_name, case=False, na=False)]
    if player_df.empty:
        return html.Div("Player not found in the specified season.", style={'color': 'red'})

    columns = [
        {'name': 'Play Type', 'id': 'PLAY_TYPE'},
        {'name': 'Posessions', 'id': 'POSS'},
        {'name': 'Frequency percent', 'id': 'FREQ'},
        {'name': 'Frequency percentile', 'id': 'FREQ_PCTL'},
        {'name': 'Efficiency - PPP', 'id': 'PPP'},
        {'name': 'Efficiency percentile', 'id': 'PPP_PCTL'}
    ]

    player_table = player_df[['PLAY_TYPE', 'POSS', 'FREQ', 'FREQ_PCTL', 'PPP', 'PPP_PCTL']]

    # Ensure all play types are present
    play_types = ["Isolation", "Transition", "Spotup", "PnR Ball-Handler", "PnR Roll Man",
                  "Handoff", "Off Screens", "Postup", "Cut", "Putbacks", "Misc"]
    player_table = player_table.set_index('PLAY_TYPE').reindex(play_types).reset_index().fillna(0)
    player_table = round_percentiles(player_table, ['FREQ_PCTL', 'PPP_PCTL'])

    table = dash_table.DataTable(
        columns=columns,
        data=player_table.to_dict('records'),
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{FREQ_PCTL} >= 90',
                    'column_id': 'FREQ_PCTL'
                },
                'backgroundColor': 'green',
                'color': 'white'
            },
            {
                'if': {
                    'filter_query': '{FREQ_PCTL} < 90 && {FREQ_PCTL} >= 75',
                    'column_id': 'FREQ_PCTL'
                },
                'backgroundColor': 'limegreen',
                'color': 'white'
            },
            {
                'if': {
                    'filter_query': '{FREQ_PCTL} < 75 && {FREQ_PCTL} >= 50',
                    'column_id': 'FREQ_PCTL'
                },
                'backgroundColor': 'yellow',
                'color': 'black'
            },
            {
                'if': {
                    'filter_query': '{FREQ_PCTL} < 50 && {FREQ_PCTL} >= 25',
                    'column_id': 'FREQ_PCTL'
                },
                'backgroundColor': 'orange',
                'color': 'white'
            },
            {
                'if': {
                    'filter_query': '{FREQ_PCTL} < 25',
                    'column_id': 'FREQ_PCTL'
                },
                'backgroundColor': 'red',
                'color': 'white'
            },
            {
                'if': {
                    'filter_query': '{PPP_PCTL} >= 90',
                    'column_id': 'PPP_PCTL'
                },
                'backgroundColor': 'green',
                'color': 'white'
            },
            {
                'if': {
                    'filter_query': '{PPP_PCTL} < 90 && {PPP_PCTL} >= 75',
                    'column_id': 'PPP_PCTL'
                },
                'backgroundColor': 'limegreen',
                'color': 'white'
            },
            {
                'if': {
                    'filter_query': '{PPP_PCTL} < 75 && {PPP_PCTL} >= 50',
                    'column_id': 'PPP_PCTL'
                },
                'backgroundColor': 'yellow',
                'color': 'black'
            },
            {
                'if': {
                    'filter_query': '{PPP_PCTL} < 50 && {PPP_PCTL} >= 25',
                    'column_id': 'PPP_PCTL'
                },
                'backgroundColor': 'orange',
                'color': 'white'
            },
            {
                'if': {
                    'filter_query': '{PPP_PCTL} < 25',
                    'column_id': 'PPP_PCTL'
                },
                'backgroundColor': 'red',
                'color': 'white'
            }
        ],
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'padding': '10px'},
        style_cell_conditional=[
            {'if': {'column_id': 'PLAY_TYPE'}, 'textAlign': 'left', 'width': '20%'},
            {'if': {'column_id': 'POSS'}, 'width': '16%'},
            {'if': {'column_id': 'FREQ'}, 'width': '16%'},
            {'if': {'column_id': 'FREQ_PCTL'}, 'width': '16%'},
            {'if': {'column_id': 'PPP'}, 'width': '16%'},
            {'if': {'column_id': 'PPP_PCTL'}, 'width': '16%'}
        ],
        page_size=11
    )

    return html.Div([
        html.H3(f"Player: {player_name}"),
        table
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
