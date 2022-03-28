import os
import glob
import json
import pandas as pd
from pandas import read_json
import datetime
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
        dataDF = pd.read_json(data, orient='index')
        dataIndex = dataDF.index.to_pydatetime()-datetime.datetime.fromtimestamp(-3600)
        dataIndex = [t.total_seconds() for t in dataIndex]
        dataDF.index = dataIndex
    return dataDF

def computeKPI(data):
    vmax = data['v'].max()
    vmin = data['v'][1:].min()
    vmean = round(data['v'].mean(),2)
    time = data.iloc[-1].name
    route = round(vmean * time,2)
    return vmax, vmin, vmean, time, route

listLoggerFiles = getLoggerFiles()
ddLabels = {'v': 'Geschwindigkeit', 'sa': 'Lenkwinkel', 'dir': 'Richtung', 'dist': 'Abstand', 'inf': 'Infrarot'}
dfFahrattribut = pd.DataFrame()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

kpi_1 = dbc.Card([dbc.CardBody([html.H4("vMax") , html.P(id='kpi1')])])
kpi_2 = dbc.Card([dbc.CardBody([html.H4("vMin") , html.P(id='kpi2')])])
kpi_3 = dbc.Card([dbc.CardBody([html.H4("vMean") , html.P(id='kpi3')])])
kpi_4 =dbc.Card([dbc.CardBody([html.H4("time") , html.P(id='kpi4')])])
kpi_5 =dbc.Card([dbc.CardBody([html.H4("vm") , html.P(id='kpi5')])])

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
        html.Br(),
        html.H2(id='H2', children='Log-Datei:'),
        dcc.Dropdown(id='dropdown-log',
                     options=listLoggerFiles,
                     placeholder='Bitte Logging-File wählen!', style={'width': 500}),
        html.Br(),
        html.H2(id='H3', children='KPI\'s:'),
        dbc.Row(cards),
        html.Br(),
        html.H2(id='H4', children='Fahrattribut:'),
        dcc.Dropdown(id='dropdown-fahrattribut',
                     placeholder='Bitte Fahrattribut wählen!', style={'width': 500}),
        dcc.Graph(id='fahrattribut-plot'),
        html.Br(),
    ]
)

@app.callback(
    Output(component_id='kpi1', component_property='children'),
    Output(component_id='kpi2', component_property='children'),
    Output(component_id='kpi3', component_property='children'),
    Output(component_id='kpi4', component_property='children'),
    Output(component_id='kpi5', component_property='children'),
    Output(component_id='dropdown-fahrattribut', component_property='options'),
    Input('dropdown-log', 'value')
)
def update_KPI_DD(logFile):
    if logFile:
        data = readJSON(logFile)
        global dfFahrattribut
        dfFahrattribut = data
        fahrAttr = [{'label': ddLabels[key], 'value': key} for key in data.keys()]
        vmax, vmin, vmean, time, route = computeKPI(data)
        return vmax, vmin, vmean, time, route, fahrAttr
    else:
        return 0, 0, 0, 0, 0, []

@app.callback(
    Output(component_id='fahrattribut-plot', component_property='figure'),
    Input('dropdown-fahrattribut', 'value')
)
def update_Fahrattribut(value):
    if value in ddLabels:
        fig = px.line(dfFahrattribut, y=dfFahrattribut[value], labels={value: ddLabels[value], 'index':'Zeit'}, title='Zeitliche Entwicklung - ' + ddLabels[value])
        return fig
    else:
        return px.line()


if __name__ == '__main__':
    app.run_server(debug=True)