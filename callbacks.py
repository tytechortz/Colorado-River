import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime as dt
from app import app
# import dash_bootstrap_components as dbc
# import callbacks
from datetime import datetime, date, timedelta
import time
import requests
import csv

today = time.strftime("%Y-%m-%d")
print(today)
today2 = datetime.now()
year = datetime.now().year
f_date = datetime(year, 1, 1)
delta = today2 - f_date
days = delta.days

capacities = {'Lake Powell Glen Canyon Dam and Powerplant': 24322000, 'Lake Mead Hoover Dam and Powerplant': 26134000, 'FLAMING GORGE RESERVOIR': 3788700, 'NAVAJO RESERVOIR': 1708600, 'BLUE MESA RESERVOIR': 940800, 'Powell Mead Combo': 50456000}


@app.callback([
    Output('powell-water-data', 'data'),
    Output('mead-water-data', 'data'),
    Output('combo-water-data', 'data')],
    Input('interval-component', 'n_intervals'))
def clean_powell_data(n):

    powell_data = 'https://data.usbr.gov/rise/api/result/download?type=csv&itemId=509&before=' + today + '&after=1999-12-29&filename=Lake%20Powell%20Glen%20Canyon%20Dam%20and%20Powerplant%20Daily%20Lake%2FReservoir%20Storage-af%20Time%20Series%20Data%20'

    mead_data = 'https://data.usbr.gov/rise/api/result/download?type=csv&itemId=6124&before=' + today + '&after=1999-12-30&filename=Lake%20Mead%20Hoover%20Dam%20and%20Powerplant%20Daily%20Lake%2FReservoir%20Storage-af%20Time%20Series%20Data%20(1937-05-28%20-%202020-11-30)&order=ASC'

    # https://data.usbr.gov/rise/api/result/download?type=csv&itemId=509&before=2021-09-17&after=1999-12-29&filename=Lake%20Powell%20Glen%20Canyon%20Dam%20and%20Powerplant%20Daily%20Lake%2FReservoir%20Storage-af%20Time%20Series%20Data%20


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

        mead_download = s.get(mead_data)

        mead_decoded_content = mead_download.content.decode('utf-8')

        crm = csv.reader(mead_decoded_content.splitlines(), delimiter=',')

        for i in range(9): next(crm)
        df_mead_water = pd.DataFrame(crm)
        df_mead_water = df_mead_water.drop(df_mead_water.columns[[1,3,4,5,7,8]], axis=1)
        df_mead_water.columns = ["Site", "Value", "Date"]
    
        df_mead_water['1090'] = 10857000
        df_mead_water['1075'] = 9601000
        df_mead_water['1050'] = 7683000
        df_mead_water['1025'] = 5981000

        df_mead_water = df_mead_water.set_index("Date")
        df_mead_water = df_mead_water.sort_index()
    
    powell_df = df_powell_water.drop(df_powell_water.index[0])
    mead_df = df_mead_water.drop(df_mead_water.index[0])

    start_date = date(1963, 6, 29)
    date_now = date.today()
    delta = date_now - start_date
    
    days = delta.days
    df_mead_water = mead_df[9527:]
    
    df_total = pd.merge(mead_df, powell_df, how='inner', left_index=True, right_index=True)
  
    df_total.rename(columns={'Date_x':'Date'}, inplace=True)
    
    df_total['Value_x'] = df_total['Value_x'].astype(int)
    df_total['Value_y'] = df_total['Value_y'].astype(int)
    df_total['Value'] = df_total['Value_x'] + df_total['Value_y']
    
    # combo_df = df_total.drop(df_total.index[0])
    combo_df = df_total

    return powell_df.to_json(), mead_df.to_json(), combo_df.to_json()

@app.callback([
    Output('powell-levels', 'figure'),
    Output('mead-levels', 'figure'),
    Output('combo-levels', 'figure')],
    [Input('powell-water-data', 'data'),
    Input('mead-water-data', 'data'),
    Input('combo-water-data', 'data')])
def lake_graphs(powell_data, mead_data, combo_data):
    powell_df = pd.read_json(powell_data)
    mead_df = pd.read_json(mead_data)
    combo_df = pd.read_json(combo_data)

    powell_traces = []
    mead_traces = []
    combo_traces = []

    data = powell_df.sort_index()
    # title = 'Lake Powell'
    powell_traces.append(go.Scatter(
        y = powell_df['Value'],
        x = powell_df.index,
        name='Water Level'
    )),

    for column in mead_df.columns[1:]:
        mead_traces.append(go.Scatter(
            y = mead_df[column],
            x = mead_df.index,
            name = column
        ))

    powell_traces.append(go.Scatter(
        y = powell_df['power level'],
        x = powell_df.index,
        name = 'Power level'
    )),

    combo_traces.append(go.Scatter(
        y = combo_df['Value'],
        x = combo_df.index,
    ))

    powell_layout = go.Layout(
        height =400,
        title = 'Lake Powell',
        yaxis = {'title':'Volume (AF)'},
        paper_bgcolor="#1f2630",
        plot_bgcolor="#1f2630",
        font=dict(color="#2cfec1"),
    )

    mead_layout = go.Layout(
        height =400,
        title = 'Lake Mead',
        yaxis = {'title':'Volume (AF)'},
        paper_bgcolor="#1f2630",
        plot_bgcolor="#1f2630",
        font=dict(color="#2cfec1"),
    )

    combo_layout = go.Layout(
        height =400,
        title = 'Powell and Mead Total Storage',
        yaxis = {'title':'Volume (AF)'},
        paper_bgcolor="#1f2630",
        plot_bgcolor="#1f2630",
        font=dict(color="#2cfec1"),
    )


    time.sleep(5)
    return {'data': powell_traces, 'layout': powell_layout}, {'data': mead_traces, 'layout': mead_layout}, {'data': combo_traces, 'layout': combo_layout}

@app.callback([
    Output('cur-levels', 'children'),
    Output('powell-annual-change', 'data'),
    Output('mead-annual-change', 'data'),
    Output('combo-annual-change', 'data')],
    [Input('powell-water-data', 'data'),
    Input('mead-water-data', 'data'),
    Input('combo-water-data', 'data')])
def get_current_volumes(powell_data, mead_data, combo_data):
    powell_data = pd.read_json(powell_data)
    powell_data.sort_index()
    powell_current_volume = powell_data.iloc[-1,1]
    powell_current_volume_date = powell_data.index[-1]
    cvd = str(powell_current_volume_date)
    powell_last_v = powell_data.iloc[-1,0]
    powell_pct = powell_current_volume / capacities['Lake Powell Glen Canyon Dam and Powerplant']
    powell_tfh_change = powell_current_volume - powell_data['Value'][-2]
    powell_cy = powell_current_volume - powell_data['Value'][-days]
    powell_yr = powell_current_volume - powell_data['Value'][-366]
    powell_last = powell_data.groupby(powell_data.index.strftime('%Y')).tail(1)
   
    # powell_last['diff'] = powell_last['Value'] - powell_last['Value'].shift(1)
    powell_last['diff'] = powell_last['Value'].diff()
    powell_last['color'] = np.where(powell_last['diff'] < 0, 'red', 'green')
   
    powell_annual_min = powell_data.resample('Y').min()
    powell_min_twok = powell_annual_min[(powell_annual_min.index.year > 1999)]
    powell_rec_low = powell_min_twok['Value'].min()
    powell_dif_rl = powell_data['Value'].iloc[-1] - powell_rec_low
    # powell_rec_diff = powell_current_volume - powel
    
    powell_rec_low_date = powell_data['Value'].idxmin().strftime('%Y-%m-%d')
    print(powell_rec_low_date)

    mead_data = pd.read_json(mead_data)
    mead_data.sort_index()
    mead_current_volume = mead_data.iloc[-0,-0]
    mead_current_volume = mead_data['Value'].iloc[-1]
    mead_pct = mead_current_volume / capacities['Lake Mead Hoover Dam and Powerplant']
    mead_last_v = mead_data.iloc[-1,0]
    mead_tfh_change = mead_current_volume - mead_data['Value'][-2]
    mead_cy = mead_current_volume - mead_data['Value'][-days]
    mead_yr = mead_current_volume - mead_data['Value'][-366]
    mead_last = mead_data.groupby(mead_data.index.strftime('%Y')).tail(1)
    mead_annual_min = mead_data.resample('Y').min()
    mead_min_twok = mead_annual_min[(mead_annual_min.index.year > 1999)]
    mead_rec_low = mead_min_twok['Value'].min()
    mead_dif_rl = mead_data['Value'].iloc[-1] - mead_rec_low
    
    # powell_last['diff'] = powell_last['Value'] - powell_last['Value'].shift(1)
    mead_last['diff'] = mead_last['Value'].diff()
    mead_last['color'] = np.where(mead_last['diff'] < 0, 'red', 'green')
    mead_rec_low_date = mead_data['Value'].idxmin().strftime('%Y-%m-%d')
   
    combo_data = pd.read_json(combo_data)
    
    combo_current_volume = combo_data['Value'][-1]
    combo_current_volume_date = combo_data.index[-1]
    combo_pct = combo_current_volume / capacities['Powell Mead Combo']
    combo_last_v = combo_data['Value'][-2]
    combo_tfh_change = combo_current_volume - combo_data['Value'][-2]
    combo_cy = combo_current_volume - combo_data['Value'][-days]
    combo_yr = combo_current_volume - combo_data['Value'][-366]
   
    combo_last = combo_data.groupby(combo_data.index.strftime('%Y')).tail(1)
    combo_last['diff'] = combo_last['Value'].diff()
    combo_last['color'] = np.where(combo_last['diff'] < 0, 'red', 'green')
    combo_annual_min = combo_data.resample('Y').min()
    combo_min_twok = combo_annual_min[(combo_annual_min.index.year > 1999)]
    combo_rec_low = combo_min_twok['Value'].min()
    combo_dif_rl = combo_data['Value'].iloc[-1] - combo_rec_low
    combo_rec_low_date = combo_data['Value'].idxmin().strftime('%Y-%m-%d')


    return html.Div([
        html.Div([
            html.Div([
                html.H6('Powell', style={'text-align': 'left'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(powell_current_volume), style={'text-align': 'right'})
            ],
                className='two columns'
            ),
            html.Div([
                html.H6('{0:.0%}'.format(powell_pct), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(powell_tfh_change), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(powell_cy), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(powell_yr), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(powell_rec_low), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(powell_dif_rl), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{}'.format(powell_rec_low_date), style={'text-align': 'center'})
            ],
                className='two columns'
            ),
        ],
            className='row'
        ),
        html.Div([
            html.Div([
                html.H6('Mead', style={'text-align': 'left'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(mead_current_volume), style={'text-align': 'right'})
            ],
                className='two columns'
            ),
            html.Div([
                html.H6('{0:.0%}'.format(mead_pct), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(mead_tfh_change), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(mead_cy), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(mead_yr), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(mead_rec_low), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(mead_dif_rl), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{}'.format(mead_rec_low_date), style={'text-align': 'center'})
            ],
                className='two columns'
            ),
        ],
            className='row'
        ),
        html.Div([
            html.Div([
                html.H6('Combined', style={'text-align': 'left'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(combo_current_volume), style={'text-align': 'right'})
            ],
                className='two columns'
            ),
            html.Div([
                html.H6('{0:.0%}'.format(combo_pct), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(combo_tfh_change), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(combo_cy), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(combo_yr), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(combo_rec_low), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(combo_dif_rl), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{}'.format(combo_rec_low_date), style={'text-align': 'center'})
            ],
                className='two columns'
            ),
        ],
            className='row'
        ),
    ]), powell_last.to_json(), mead_last.to_json(), combo_last.to_json()