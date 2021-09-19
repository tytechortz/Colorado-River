import requests
import csv
import pandas as pd
import io
import dash
from dash import html, dcc
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
import time
from datetime import datetime, date, timedelta
# from data import powell_df

today = time.strftime("%Y-%m-%d")

url = 'https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent?aoi=08&startdate=1/1/2000&enddate=' + today + '&statisticsType=2'


# print(df)

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

server = app.server

app.layout = html.Div([
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
        interval=20*1000, # in milliseconds
        n_intervals=0
    ),
    dcc.Store(id='drought-data'),
])

@app.callback(
    Output('drought-data', 'data'),
    Input('interval-component', 'n_intervals'))
def data(n):
    r = requests.get(url).content

    df = pd.read_json(io.StringIO(r.decode('utf-8')))
    print(df)

    df['date'] = pd.to_datetime(df['MapDate'].astype(str), format='%Y%m%d')

    df.drop(['StatisticFormatID', 'StateAbbreviation', 'MapDate'] , axis=1, inplace=True)
    df.set_index('date', inplace=True)
    # print(df)
    df['DSCI'] = (df['D0'] + (df['D1']*2) + (df['D2']*3) + (df['D3']*4 + (df['D4']*5)))

    return df.to_json()



@app.callback(
    Output('drought-graph', 'figure'),
    Input('drought-data', 'data'))
def drought_graph(data):
    df = pd.read_json(data)
    return print(df)


if __name__ == '__main__':
    app.run_server(port=8010, debug=True)