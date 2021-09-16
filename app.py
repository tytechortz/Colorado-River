import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import time
import requests
import csv
import pandas as pd


app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

server = app.server

today = time.strftime("%Y-%m-%d")
print(today)

app.layout = html.Div([
    html.Div([
        html.H2(
            'Colorado River Water Storage',
            className='twelve columns',
            style={'text-align': 'center'}
        ),
        html.Div([
        # html.Div([
        #     dcc.Graph(
        #         id='mead-levels',
        #     ),
        # ],
        #     className='four columns'
        # ),
        html.Div([
            dcc.Graph(
                # figure=powell_fig,
                id='powell-levels',
            ),
        ],
            className='four columns'
        ),
        # html.Div([
        #     dcc.Graph(
        #         # figure=powell_fig,
        #         id='combo-levels',
        #     ),
        # ],
        #     className='four columns'
        # ),

    ],
        className='row'
    ),
    ],
        className='row'
    ),

    dcc.Interval(
        id='interval-component',
        interval=1*100000, # in milliseconds
        n_intervals=0
    ),
    dcc.Store(id='powell-water-data')
])


@app.callback(
    Output('powell-water-data', 'data'),
    #Output('mead-water-data', 'children'),
    #Output('combo-water-data', 'children'),
    #Output('blue-mesa-water-data', 'children'),
    #Output('navajo-water-data', 'children'),
    #Output('fg-water-data', 'children')],
    Input('interval-component', 'n_intervals'))
def clean_powell_data(n):

    powell_data = 'https://data.usbr.gov/rise/api/result/download?type=csv&itemId=509&before=' + today + '&after=1999-12-29&filename=Lake%20Powell%20Glen%20Canyon%20Dam%20and%20Powerplant%20Daily%20Lake%2FReservoir%20Storage-af%20Time%20Series%20Data%20'

    # https://data.usbr.gov/rise/api/result/download?type=csv&itemId=509&before=2021-09-16&after=1999-12-29&filename=Lake%20Powell%20Glen%20Canyon%20Dam%20and%20Powerplant%20Daily%20Lake%2FReservoir%20Storage-af%20Time%20Series%20Data%20


    with requests.Session() as s:

        powell_download = s.get(powell_data)
        
        powell_decoded_content = powell_download.content.decode('utf-8')
    
        crp = csv.reader(powell_decoded_content.splitlines(), delimiter=',')
        
        
        for i in range(9): next(crp)
        df_powell_water = pd.DataFrame(crp)
        
        df_powell_water = df_powell_water.drop(df_powell_water.columns[[1,3,4,5,7,8]], axis=1)
        df_powell_water.columns = ["Site", "Value", "Date"]
    
        df_powell_water = df_powell_water[1:]
        
        df_powell_water['power level'] = 6124000

        df_powell_water = df_powell_water.set_index("Date")
        df_powell_water = df_powell_water.sort_index()
        # print(df_powell_water)
    
    powell_df = df_powell_water.drop(df_powell_water.index[0])
    # print(powell_df)

    return powell_df.to_json()

@app.callback([
    Output('powell-levels', 'figure')],
    [Input('powell-water-data', 'data')])
def lake_graphs(powell_data):
    powell_df = pd.read_json(powell_data)
    return(print(powell_df))


if __name__ == '__main__':
    app.run_server(port=8080, debug=True)