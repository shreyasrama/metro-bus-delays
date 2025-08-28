import pandas as pd
import plotly.graph_objects as go

def create_map(df: pd.DataFrame) -> go.Figure:
    # Delays of 2 minutes or greater only
    if not df.empty and 'delay_minutes' in df.columns:
        df = df[df['delay_minutes'] >= 2]
        marker_color = df['delay_minutes'].clip(0, 20)
        colorscale = 'orrd'
    else:
        marker_color = 'blue'
        colorscale = None

    fig = go.Figure(go.Scattermap(
        lat=df['stop_lat'],
        lon=df['stop_lon'],
        mode='markers',
        marker=dict(
            size=14,
            color=marker_color,
            colorscale=colorscale,
            colorbar=dict(title="Delay (minutes)") if colorscale else None
        ),

        # Construct text object for tooltip
        text=[
            f"{line}: {direction}<br>{name}<br>Delay: {round(delay)} minutes" for line, direction, name, delay in 
                zip(
                    df['published_line_name'],
                    df['direction_ref'],
                    df['stop_point_name'], 
                    df.get('delay_minutes', [0]*len(df))
                )
        ],
        hoverinfo='text',
    ))
    
    return fig

def update_map(fig):
    fig.update_layout(
        hovermode='closest',
        map=dict(
            style="dark",
            center=dict(lat=-43.532812, lon=172.636350),
            zoom=12
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        autosize=True,
        uirevision=True,
    )
