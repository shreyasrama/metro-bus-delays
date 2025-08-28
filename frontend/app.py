import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from datetime import datetime
from fetch import fetch_latest_data
from map import create_map, update_map
import os
from waitress import serve

app = dash.Dash(__name__)
server = app.server

endpoint = os.getenv("API_ENDPOINT") or ""
api_key = os.getenv("API_KEY") or ""

initial_data = fetch_latest_data(endpoint, api_key)
initial_df = initial_data["data"]
initial_timestamp = datetime.fromisoformat(initial_data["timestamp"])
initial_title = f"Live Bus Delays - {initial_timestamp.strftime('%A, %d %B %Y %H:%M:%S')}"

fig = create_map(initial_df)
update_map(fig)

app.title = "Live Bus Delays in Christchurch"

app.layout = html.Div(
    id="main-div",
    children = [
        html.H1(str(initial_title), id="app-title"),
        html.P("Data updates every 5 minutes. Delays are based on actual recorded time a bus leaves the stop."),
        dcc.Graph(
            id='live-update-graph',
            figure=fig,
            responsive=True,
            style={'height': '85vh'}  # Full viewport height
        ),
        dcc.Interval(
            id='interval-component',
            interval=300000,
            n_intervals=0
        ),
        dcc.Store(id='latest-timestamp', data=str(initial_timestamp)),
    ]
)

@app.callback(
    Output('live-update-graph', 'figure'),
    Output('latest-timestamp', 'data'),
    Input('interval-component', 'n_intervals'),
    State('live-update-graph', 'figure')
)
def update_graph_live(n, _):
    latest_data = fetch_latest_data(endpoint, api_key)
    latest_df = latest_data["data"]
    latest_timestamp = latest_data["timestamp"]

    fig = create_map(latest_df)
    update_map(fig)

    return fig, latest_timestamp

@app.callback(
    Output('app-title', 'children'),
    Input('latest-timestamp', 'data')
)
def update_h1(timestamp: str):
    if not isinstance(timestamp, str):
        return "Live Bus Delays"
    try:
        latest_timestamp = datetime.fromisoformat(timestamp)
        latest_title = f"Live Bus Delays - {latest_timestamp.strftime('%A, %d %B %Y %H:%M:%S')}"
        return latest_title
    except Exception:
        return "Live Bus Delays"

if __name__ == '__main__':
    if os.getenv("ENVIRONMENT") == "prod":
        serve(server, host='0.0.0.0', port=3000)
    else:
        app.run(debug=True)
