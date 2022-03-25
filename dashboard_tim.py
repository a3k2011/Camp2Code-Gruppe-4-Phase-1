import dash
from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

class Dashboard():

    def __init__(self):
        self._app = dash.Dash()
        self.initLayout()
        self._app.run_server(debug=True)


    def initLayout(self):
        print("Initialisiere")
        self._app.layout = html.Div(
    children=[
        html.H1(id='H1',
                children='HTML Component',
                style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
        html.H2(id='H2',
                children='2nd HTML Component'),
        html.Div(children='Ein ganz normaler Container (div) für Fließende Objekte'),
        html.Div([dcc.Dropdown(options=['NYC', 'MTL', 'SF'], placeholder= 'Select a City!', id='demo-dropdown'),
        html.Div(id='dd-output-container')])
    ]
)