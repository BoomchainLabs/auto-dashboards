def streamlit_prompt(code: str):
    prompt = "Translate the following Python code to Streamlit dashboard:\n\n"
    prompt += "```python\n"
    prompt += code
    prompt += "```\n"
    prompt += "Only output the Streamlit code and no comments or explanations."

    return prompt

def solara_prompt(code: str):
    prompt = "Translate the following Python code to Solara dashboard:\n\n"
    prompt += """For example, here is how sliders are created in Solara:
```python
import solara

int_value = solara.reactive(42)


@solara.component
def Page():
    solara.SliderInt("Some integer", value=int_value, min=-10, max=120)
    solara.Markdown(f"**Int value**: {int_value.value}")
    with solara.Row():
        solara.Button("Reset", on_click=lambda: int_value.set(42))
```
"""
    prompt += "```python\n"
    prompt += code
    prompt += "```\n"
    prompt += "Only output the Solara code and no comments or explanations."

    return prompt

def dash_prompt(code: str):
    prompt = "Translate the following Python code to a Plotly Dash dashboard:\n\n"
    prompt += """For example, here is how a basic Dash app is created:
```python
from dash import Dash, html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)

app.layout = html.Div([
    html.H1('Simple Dash App'),
    dcc.Graph(id='graph'),
    dcc.Slider(0, 20, 5, value=10, id='slider')
])

@callback(
    Output('graph', 'figure'),
    Input('slider', 'value')
)
def update_graph(value):
    df = pd.DataFrame({'x': range(10), 'y': [i**2 * value/10 for i in range(10)]})
    return px.line(df, x='x', y='y')

if __name__ == '__main__':
    app.run_server(debug=True)
```
"""
    prompt += "```python\n"
    prompt += code
    prompt += "```\n"
    prompt += "Only output the Plotly Dash code and no comments or explanations. Make sure to include code that allows the app to be run with the command-line arguments: app.run_server(host='0.0.0.0', port=int(port), debug=False) if port is passed as a command-line argument."

    return prompt