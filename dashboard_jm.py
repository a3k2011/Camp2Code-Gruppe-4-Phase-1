import os
import glob
import json
import pandas as pd
from pandas import read_json
import time
import datetime
import dash
from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash import callback_context
import dash_bootstrap_components as dbc
import fahrparcours_jm_test as fp


df = None


def getLoggerFiles():
    # wcLoggerOrdner = os.path.join("Logger", "*")
    # listLoggerPfade = [filename for filename in glob.glob(wcLoggerOrdner)]
    fileList = []
    if os.path.isdir("Logger"):
        fileList = os.listdir("Logger")
    return fileList


def getLogItemsList():
    return [
        "time",
        "v",
        "dir",
        "st_angle",
        "US",
        "IR1",
        "IR2",
        "IR3",
        "IR4",
        "IR5",
    ]


def load_data_to_df(pfad):
    global df
    df = pd.read_json(os.path.join("Logger", pfad))
    df.columns = getLogItemsList()


kpi_1 = dbc.Card([dbc.CardBody([html.H6("vMax"), html.P(id="kpi1")])])
kpi_2 = dbc.Card([dbc.CardBody([html.H6("vMin"), html.P(id="kpi2")])])
kpi_3 = dbc.Card([dbc.CardBody([html.H6("vMean"), html.P(id="kpi3")])])
kpi_4 = dbc.Card([dbc.CardBody([html.H6("time"), html.P(id="kpi4")])])
kpi_5 = dbc.Card([dbc.CardBody([html.H6("vm"), html.P(id="kpi5")])])


app = dash.Dash(external_stylesheets=[dbc.themes.SUPERHERO])

app.layout = dbc.Container(
    [
        dbc.Row(
            [  # Row 1
                dbc.Col(
                    [  # Col 1
                        html.H1(
                            id="title_main",
                            children="Camp2Code - Gruppe 4",
                            style={
                                "textAlign": "center",
                                "marginTop": 40,
                                "marginBottom": 40,
                            },
                        )
                    ],
                    width=12,
                ),
            ],
            justify="center",
        ),
        dbc.Row(
            [  # Row 2
                dbc.Col(  # Logfile-Handling
                    [
                        dbc.Row(
                            [
                                html.H2(  # Überschrift
                                    id="title_Logfiles",
                                    children="Logfiles",
                                    style={"textAlign": "center", "paddingBottom": 20},
                                ),
                                dcc.Dropdown(  # Dropdown Logfiles
                                    id="dd_Logfiles",
                                    placeholder="Bitte Logging-File wählen!",
                                    options=getLoggerFiles(),
                                    value=["2"],
                                    multi=False,
                                    style={"color": "black"},
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col([kpi_1], width=4),
                                dbc.Col([kpi_2], width=4),
                                dbc.Col([kpi_3], width=4),
                            ],
                            style={"paddingTop": 20, "paddingBottom": 20},
                        ),
                        dbc.Row(
                            [dbc.Col([kpi_4], width=4), dbc.Col([kpi_5], width=4),],
                            style={"paddingBottom": 20},
                        ),
                        dbc.Row(
                            [
                                html.H3(
                                    id="titel_LogDetails", children="Plot-Line Auswahl"
                                ),
                                dcc.Dropdown(  # Dropdown Log-Details
                                    id="dd_LogDetails",
                                    options=getLogItemsList()[1:],
                                    value=["2"],
                                    multi=True,
                                    style={"color": "black"},
                                ),
                                # dcc.Checklist(
                                #     id="cl_Graph_Lines", options=getLogGraphList(),
                                # ),
                            ],
                            style={"paddingBottom": 10},
                        ),
                    ],
                    width=6,
                    style={"backgroundColor": "darkblue"},
                ),
                dbc.Col(
                    [  # Col Fahrzeugsteuerung
                        dbc.Row(
                            [  # Titel
                                html.H2(
                                    id="titel_Fahrzeugsteuerung",
                                    children="Fahrzeugsteuerung",
                                    style={"textAlign": "center", "paddingBottom": 20,},
                                )
                            ]
                        ),
                        dbc.Row(
                            [  # Dropdown Fahrprogramm
                                dcc.Dropdown(
                                    id="dd_Fahrprogramm",
                                    placeholder="Bitte Fahrprogramm wählen:",
                                    options=fp.getParcoursList(),
                                    value=0,
                                    style={"color": "black"},
                                )
                            ]
                        ),
                        dbc.Row(
                            [  # Buttons
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            children="Start Prog",
                                            id="btn_start",
                                            color="dark",
                                            className="me-1",
                                            n_clicks=0,
                                        )
                                    ],
                                    width=4,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            children="Pause",
                                            id="btn_Pause",
                                            color="dark",
                                            className="me-1",
                                            n_clicks=0,
                                        )
                                    ],
                                    width=4,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            children="STOP",
                                            id="btn_STOP",
                                            color="dark",
                                            className="me-1",
                                            n_clicks=0,
                                        )
                                    ],
                                    width=4,
                                ),
                            ],
                            style={"paddingTop": 20, "paddingBottom": 20},
                            justify="center",
                        ),
                        dbc.Row(  # Slider Speed
                            [
                                dbc.Col([html.H3("Speed:")], width=3),
                                dbc.Col(
                                    [
                                        dcc.Slider(
                                            min=0,
                                            max=100,
                                            step=10,
                                            id="slider_speed",
                                            value=40,
                                        )
                                    ],
                                    width=9,
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                html.P(
                                    id="label_test",
                                    children="Hier steht der Debug-Text",
                                    style={
                                        "textAlign": "left",
                                        "paddingTop": 20,
                                        "paddingBottom": 20,
                                    },
                                )
                            ]
                        ),
                    ],
                    width=6,
                    style={"backgroundColor": "darkred"},
                ),
            ],
            justify="center",
        ),
        dbc.Row(
            [
                dcc.Graph(id="plot_Logfile"),
                html.P(
                    id="Fussnote",
                    children="hier das Copyright ;)",
                    style={"textAlign": "right"},
                ),
            ],
            style={"paddingTop": 10, "paddingBottom": 10},
        ),  # Row 3
    ]
)


def computeKPI(data):
    vmax = data["v"].max()
    vmin = data["v"][1:].min()
    vmean = round(data["v"].mean(), 2)
    time = data.iloc[-1].name
    route = round(vmean * time, 2)
    return vmax, vmin, vmean, time, route


@app.callback(
    Output(component_id="kpi1", component_property="children"),
    Output(component_id="kpi2", component_property="children"),
    Output(component_id="kpi3", component_property="children"),
    Output(component_id="kpi4", component_property="children"),
    Output(component_id="kpi5", component_property="children"),
    Input("dd_Logfiles", "value"),
)
def update_KPI_DD(logFile):
    # fahrAttr = [{"label": ddLabels[key], "value": key} for key in df.keys()]
    try:
        df = pd.read_json(os.path.join("Logger", logFile))
        df.columns = getLogItemsList()
    except:
        return 0, 0, 0, 0, 0
    else:
        vmax, vmin, vmean, time, route = computeKPI(df)
        return vmax, vmin, vmean, time, route


@app.callback(
    Output(component_id="label_test", component_property="children"),
    Input(component_id="dd_Fahrprogramm", component_property="value"),
)
def write_label(value):
    return value


@app.callback(
    Output("plot_Logfile", "figure"),
    Input("dd_Logfiles", "value"),
    Input("dd_LogDetails", "value"),
)
def selectedLog(logFile, logDetails):
    df = pd.read_json(os.path.join("Logger", logFile))
    time.sleep(0.1)
    df.columns = getLogItemsList()
    if logDetails != []:
        fig = px.line(df, x="time", y=logDetails)
    else:
        fig = px.line(df, x="time", y="st_angle")
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
