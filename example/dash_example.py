# See official docs at https://dash.plotly.com
# pip install dash pandas

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import argparse
import pandas as pd
import os

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

def create_app(proxy_path=None):
    """Create and configure the Dash app"""
    if proxy_path:
        app = Dash(__name__, requests_pathname_prefix=proxy_path)
    else:
        app = Dash(__name__)
    
    app.layout = html.Div([
        dcc.Graph(id='graph-with-slider'),
        dcc.Slider(
            df['year'].min(),
            df['year'].max(),
            step=None,
            value=df['year'].min(),
            marks={str(year): str(year) for year in df['year'].unique()},
            id='year-slider'
        )
    ])

    @app.callback(
        Output('graph-with-slider', 'figure'),
        Input('year-slider', 'value'))
    def update_figure(selected_year):
        filtered_df = df[df.year == selected_year]

        fig = px.scatter(filtered_df, x="gdpPercap", y="lifeExp",
                         size="pop", color="continent", hover_name="country",
                         log_x=True, size_max=55)

        return fig
    
    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8050, help='Port to run the app on')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--proxy-path', type=str, help='Proxy path for Jupyter integration')
    
    args = parser.parse_args()
    
    # Create app with proxy configuration if provided
    proxy_path = None
    if args.proxy_path:
        proxy_path = args.proxy_path
        if not proxy_path.endswith('/'):
            proxy_path = proxy_path + '/'
    
    app = create_app(proxy_path)
    app.run(debug=args.debug, port=args.port, dev_tools_ui=not args.no_browser, host='127.0.0.1')