import pandas as pd
import plotly.graph_objects as go

def plot_treemap_with_plotly_go(nodes):
    df = pd.DataFrame(nodes)
    fig = go.Figure(go.Treemap(
        labels=df['label'],
        parents=df['parent'],
        ids=df['id'],
        values=df['value'],
        customdata=df[['Build Time (formatted)', 'Build Time (seconds)']],
        hovertemplate='<b>%{label}</b><br>Build Time: %{customdata[0]}<br>Total Seconds: %{customdata[1]:.2f}<extra></extra>',
        textinfo='label+value'
    ))
    fig.update_layout(title='Package Build Times Treemap')
    return fig
