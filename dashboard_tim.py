import os
import glob
import json
import pandas as pd
from pandas import read_json
import time
import datetime
import dash
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import infraredcar_tim as IC

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

ic = IC.InfraredCar()

listLoggerFiles = getLoggerFiles()
ddLabels = {'v': 'Geschwindigkeit', 'sa': 'Lenkwinkel', 'dir': 'Richtung', 'dist': 'Abstand', 'inf': 'Infrarot'}

app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])

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
        dbc.Row([dbc.Col([html.H2(id='H2', children='Log-Datei:'),
        dcc.Dropdown(id='dropdown-log',
                     options=listLoggerFiles,
                     placeholder='Bitte Logging-File wählen!', style={'color': 'black', 'width': 500}),
        html.Br(),
        html.H2(id='H3', children='KPI\'s:'),
        dbc.Row(cards),
        html.Br(),
        ]), 
        dbc.Col([html.H2(id='H5', children='Steuerung:'),
        html.Div(children=[html.Div("Geschwindigkeit:") ,dcc.Input(id='input-on-submit', type='text')]),
        html.Br(),
        html.Button('Fahrparcour 1', id='btn-fp1', n_clicks=0, style={'marginLeft': 00, 'marginRight': 10}),
        html.Button('Fahrparcour 2', id='btn-fp2', n_clicks=0, style={'marginLeft': 10, 'marginRight': 10}),
        html.Button('Fahrparcour 3', id='btn-fp3', n_clicks=0, style={'marginLeft': 10, 'marginRight': 10}),
        html.Button('Fahrparcour 4', id='btn-fp4', n_clicks=0, style={'marginLeft': 10, 'marginRight': 10}),
        html.Button('Fahrparcour 5', id='btn-fp5', n_clicks=0, style={'marginLeft': 10, 'marginRight': 10}),
        html.Button('Fahrparcour 6', id='btn-fp6', n_clicks=0, style={'marginLeft': 10, 'marginRight': 10}),
        html.Br(),
        html.Div(id='placeholder'),
        html.Br(),
        html.Button('Notfall Exit', id='btn-e', n_clicks=0, style={'marginLeft': 00, 'marginRight': 10})
        ])
        ]),
        html.H2(id='H4', children='Fahrattribut:'),
        dcc.Dropdown(id='dropdown-fahrattribut',
                     placeholder='Bitte Fahrattribut wählen!', style={'color': 'black', 'width': 500}),
        html.Br(),    
        dcc.Graph(id='fahrattribut-plot'),
        html.Br(),
    ], style={'marginLeft': 20}
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
        fahrAttr = [{'label': ddLabels[key], 'value': key} for key in data.keys()]
        vmax, vmin, vmean, time, route = computeKPI(data)
        return vmax, vmin, vmean, time, route, fahrAttr
    else:
        return 0, 0, 0, 0, 0, []

@app.callback(
    Output(component_id='fahrattribut-plot', component_property='figure'),
    Input('dropdown-fahrattribut', 'value'),
    State('dropdown-log', 'value')
)
def update_Fahrattribut(value, logFile):
    if value in ddLabels:
        dfFahrattribut = readJSON(logFile)
        
        if not value == 'inf':
            fig = px.line(dfFahrattribut, y=dfFahrattribut[value], labels={value: ddLabels[value], 'index':'Zeit'}, title='Zeitliche Entwicklung - ' + ddLabels[value])
        else:

            splitDF = pd.DataFrame(dfFahrattribut['inf'].tolist(), columns=['i1','i2','i3','i4','i5'])
            listDF = [list(i) for i in zip(*splitDF.values)]
            list1 = [list(i[1:]) for i in listDF]
            fig = px.line(dfFahrattribut.iloc[1:,:], y=list1)

            colNames = {'wide_variable_0': 'i0', 'wide_variable_1': 'i1', 'wide_variable_2': 'i2', 'wide_variable_3': 'i3', 'wide_variable_4': 'i4'}
            fig.for_each_trace(lambda t: t.update(name = colNames[t.name],
                                      legendgroup = colNames[t.name],
                                      hovertemplate = t.hovertemplate.replace(t.name, colNames[t.name])
                                     ))
        return fig
    else:
        return px.line()

@app.callback(
    Output(component_id='dropdown-log', component_property='options'),
    Input('btn-fp1', 'n_clicks'),
    Input('btn-fp2', 'n_clicks'),
    Input('btn-fp3', 'n_clicks'),
    Input('btn-fp4', 'n_clicks'),
    Input('btn-fp5', 'n_clicks'),
    Input('btn-fp6', 'n_clicks'),
    Input('btn-e', 'n_clicks'),
    State('input-on-submit', 'value')
)
def displayClick(btn1, btn2, btn3, btn4, btn5, btn6, btn7, value):

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    v = int(value) if value != None else 50

    if 'btn-fp1' in changed_id:
        ic.fp1(v)
    elif 'btn-fp2' in changed_id:
        ic.fp2(v)
    elif 'btn-fp3' in changed_id:
        ic.fp3(v)
    elif 'btn-fp4' in changed_id:
        ic.fp4(v)
    elif 'btn-fp5' in changed_id:
        ic.fp5(v)   
    elif 'btn-fp6' in changed_id:
        ic.fp6(v)  
    elif 'btn-e' in changed_id:
        ic._active = False
        ic._worker.shutdown(wait=False)
    else:
        pass
    
    time.sleep(2)
    listLoggerFiles = getLoggerFiles()
    return listLoggerFiles

@app.callback(
    Output(component_id='placeholder', component_property='children'),
    Input('btn-fp1', 'n_clicks'),
    Input('btn-fp2', 'n_clicks'),
    Input('btn-fp3', 'n_clicks'),
    Input('btn-fp4', 'n_clicks'),
    Input('btn-fp5', 'n_clicks'),
    Input('btn-fp6', 'n_clicks'),
    Input('btn-e', 'n_clicks')
)
def messageButton(btn1, btn2, btn3, btn4, btn5, btn6, btn7):

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'btn-fp1' in changed_id:
        msg = 'Fahrparcour 1 wurde gestartet!'
    elif 'btn-fp2' in changed_id:
        msg = 'Fahrparcour 2 wurde gestartet!'
    elif 'btn-fp3' in changed_id:
        msg = 'Fahrparcour 3 wurde gestartet!'
    elif 'btn-fp4' in changed_id:
        msg = 'Fahrparcour 4 wurde gestartet!'
    elif 'btn-fp5' in changed_id:
        msg = 'Fahrparcour 5 wurde gestartet!' 
    elif 'btn-fp6' in changed_id:
        msg = 'Fahrparcour 6 wurde gestartet!' 
    elif 'btn-e' in changed_id:
        msg = 'Notfall Exit wurde durchgeführt!'
    else:
        msg = 'Es wurde noch kein Fahrparcour gestartet!'
    
    return msg


if __name__ == '__main__':
    app.run_server(debug=True)