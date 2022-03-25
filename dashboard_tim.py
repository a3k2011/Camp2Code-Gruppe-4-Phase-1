import os
import glob
import re
import json
from pandas import read_json
from pandas import json_normalize
import pandas as pd
import dash
from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

def getLoggerFiles():
    wcLoggerOrdner = os.path.join('Logger', '*')
    listLoggerPfade = [filename for filename in glob.glob(wcLoggerOrdner)]
    return listLoggerPfade

def readJSON(pfad):
    with open(pfad, "r") as f:
        data = json.load(f)
        dataDF = pd.read_json(data, orient ='index')
    return dataDF

def getLoggerData():
    listLoggerPfade = getLoggerFiles()

    for log in listLoggerPfade:
        data = readJSON(log)
        break

    return data

def computeKPI(data):
    vmax = data['v'].max()
    vmin = data['v'][1:].min()
    vmean = round(data['v'].mean(),2)
    time = round((data.iloc[-1].name - data.iloc[0].name).total_seconds(),2)
    route = 2
    return vmax, vmin, vmean, time, route


listLoggerFiles = getLoggerFiles()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

kpi_1 = dbc.Card([dbc.CardBody([html.H4("vMax") , html.P(id='kpi1', children="")])])
kpi_2 = dbc.Card([dbc.CardBody([html.H4("vMin") , html.P(id='kpi2', children="")])])
kpi_3 = dbc.Card([dbc.CardBody([html.H4("vMean") , html.P(id='kpi3', children="")])])
kpi_4 =dbc.Card([dbc.CardBody([html.H4("time") , html.P(id='kpi4', children="")])])
kpi_5 =dbc.Card([dbc.CardBody([html.H4("m") , html.P(id='kpi5', children="")])])

cards = [
        dbc.Col(kpi_1, width="auto"),
        dbc.Col(kpi_2, width="auto"),
        dbc.Col(kpi_3, width="auto"),
        dbc.Col(kpi_4, width="auto"),
        dbc.Col(kpi_5, width="auto")
    ]

app.layout = html.Div(
    children=[
        html.H1(id='H1',
                children='Camp2Code - Gruppe 4',
                style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
        html.Div(children='Bitte eine Log-Datei auswählen:'),
        dcc.Dropdown(id='dropdown-log',
                     options=listLoggerFiles,
                     placeholder='Bitte Logging-File wählen!'),
        html.Br(),
        html.H1(id='H2', children='KPI\'s:'),
        dbc.Row(cards),
        html.Br(),
        html.H1(id='H3', children='Fahrattribut:'),
        html.Div(children='Bitte ein Attribut auswählen:'),
        dcc.Dropdown(id='dropdown',
                     options=[
                         {'label': 'Google', 'value': 'GOOG'},
                         {'label': 'Apple', 'value': 'AAPL'},
                         {'label': 'Amazon', 'value': 'AMZN'},
                     ],
                     value='GOOG'),
        dcc.Graph(id='line_plot'),
        html.Br(),
    ]
)

@app.callback(
    Output(component_id='kpi1', component_property='children'),
    Output(component_id='kpi2', component_property='children'),
    Output(component_id='kpi3', component_property='children'),
    Output(component_id='kpi4', component_property='children'),
    Output(component_id='kpi5', component_property='children'),
    Input('dropdown-log', 'value')
)
def update_output(value):
    data = readJSON(value)
    return computeKPI(data)


if __name__ == '__main__':

    app.run_server(debug=True)

    #data = getLoggerData()
    #print(data)

    #print(data['v'])

    #print(data['v'].max())
    #print(data['v'].min())
    #print(data['v'].mean())

    #print((data.iloc[-1].name - data.iloc[0].name).total_seconds())

