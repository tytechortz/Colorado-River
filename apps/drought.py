import requests
import csv
import pandas as pd
import dash
from dash import html, dcc
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
import time
from datetime import datetime, date, timedelta
from homepage import get_header, get_navbar, get_emptyrow
# from data import powell_df

today = time.strftime("%Y-%m-%d")

# url = 'https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent?aoi=08&startdate=1/1/2000&enddate=' + today + '&statisticsType=2'


# print(df)

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

server = app.server

def drought_App():
    return html.Div([
        get_header(),
        get_navbar("non_home"),
        get_emptyrow(),

        html.Div([
            html.Div([
                html.H2(
                    'Drought',
                    className='twelve columns',
                    style={'text-align': 'center'}
                )
            ],
                className='row'
            ),
            html.Div([
                dcc.Graph(
                    id='drought-graph'
                )
            ],  
                className='row'
            ),
            dcc.Interval(
                id='interval-component',
                interval=200*1000, # in milliseconds
                n_intervals=0
            ),
            dcc.Store(id='drought-data'),   
        ])
    ])

# app.layout = html.Div([
#     html.Div([
#         html.H2(
#             'Drought',
#             className='twelve columns',
#             style={'text-align': 'center'}
#         )
#     ],
#         className='row'
#     ),
#     html.Div([
#         dcc.Graph(
#             id='drought-graph'
#         )
#     ],  
#         className='row'
#     ),
#     dcc.Interval(
#         id='interval-component',
#         interval=200*1000, # in milliseconds
#         n_intervals=0
#     ),
#     dcc.Store(id='drought-data'),
# ])




# if __name__ == '__main__':
#     app.run_server(port=8010, debug=True)

app.layout = drought_App