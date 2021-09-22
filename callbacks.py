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
import io

today = time.strftime("%Y-%m-%d")
print(today)
today2 = datetime.now()
year = datetime.now().year
f_date = datetime(year, 1, 1)
delta = today2 - f_date
days = delta.days

capacities = {'Lake Powell Glen Canyon Dam and Powerplant': 24322000, 'Lake Mead Hoover Dam and Powerplant': 26134000, 'FLAMING GORGE RESERVOIR': 3788700, 'NAVAJO RESERVOIR': 1708600, 'BLUE MESA RESERVOIR': 940800, 'Powell Mead Combo': 50456000}



@app.callback(
    Output('drought-data', 'data'),
    Input('drought-interval-component', 'n_intervals'))
def data(n):
    url = 'https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent?aoi=08&startdate=1/1/2000&enddate=' + today + '&statisticsType=2'

    # combo_data = pd.read_json(com)
    # print(combo_data)
    r = requests.get(url).content

    df = pd.read_json(io.StringIO(r.decode('utf-8')))
    # print(df)

    df['date'] = pd.to_datetime(df['MapDate'].astype(str), format='%Y%m%d')

    df.drop(['StatisticFormatID', 'StateAbbreviation', 'MapDate'] , axis=1, inplace=True)
    df.set_index('date', inplace=True)
    # print(df)
    df['DSCI'] = (df['D0'] + (df['D1']*2) + (df['D2']*3) + (df['D3']*4 + (df['D4']*5)))

    return df.to_json()



@app.callback(
    Output('drought-graph', 'figure'),
    [Input('drought-data', 'data'),
    Input('combo-water-data', 'data')])
def drought_graph(data, combo_data):
    df = pd.read_json(data)
    drought_traces = []

    df_combo = pd.read_json(combo_data)
    print(df_combo)

    drought_traces.append(go.Scatter(
        y = df['DSCI'],
        x = df.index,
        marker_color = 'red',
        yaxis='y'
    )),
    drought_traces.append(go.Bar(
        y = df_combo['Value'],
        x = df_combo.index,
        yaxis ='y2',
        marker_color = 'lightblue'
    )),

    drought_layout = go.Layout(
        height =600,
        title = 'DSCI',
        yaxis = {'title':'DSCI', 'overlaying': 'y2'},
        yaxis2 = {'title': 'MAF', 'side': 'right'},
        paper_bgcolor="#1f2630",
        plot_bgcolor="#1f2630",
        font=dict(color="#2cfec1"),
    )

    return {'data': drought_traces, 'layout': drought_layout}


@app.callback([
    Output('powell-water-data', 'data'),
    Output('mead-water-data', 'data'),
    Output('combo-water-data', 'data')],
    Input('interval-component', 'n_intervals'))
def clean_powell_data(n):

    powell_data = 'https://data.usbr.gov/rise/api/result/download?type=csv&itemId=509&before=' + today + '&after=1999-12-29&filename=Lake%20Powell%20Glen%20Canyon%20Dam%20and%20Powerplant%20Daily%20Lake%2FReservoir%20Storage-af%20Time%20Series%20Data%20'

    mead_data = 'https://data.usbr.gov/rise/api/result/download?type=csv&itemId=6124&before=' + today + '&after=1999-12-30&filename=Lake%20Mead%20Hoover%20Dam%20and%20Powerplant%20Daily%20Lake%2FReservoir%20Storage-af%20Time%20Series%20Data%20(1937-05-28%20-%202020-11-30)&order=ASC'


    # https://data.usbr.gov/rise/api/result/download?type=csv&itemId=509&before=2021-09-19&after=1999-12-29&filename=Lake%20Powell%20Glen%20Canyon%20Dam%20and%20Powerplant%20Daily%20Lake%2FReservoir%20Storage-af%20Time%20Series%20Data%20


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
        # print(df_mead_water)
    
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
    # print(combo_df)

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
    Input('combo-water-data', 'data'),
    Input('interval-component','n_intervals')])
def get_current_volumes(powell_data, mead_data, combo_data, n):
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
    # print(powell_rec_low_date)

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
    pd.set_option('display.max_columns', None)
    # print(combo_last)
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
                html.H6('{0:.1%}'.format(powell_pct), style={'text-align': 'center'})
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
                html.H6('{0:.1%}'.format(mead_pct), style={'text-align': 'center'})
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
                html.H6('{0:.1%}'.format(combo_pct), style={'text-align': 'center'})
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
    ]), powell_last.to_json(), mead_last.to_json(), combo_last.to_json(), 

@app.callback([
    Output('powell-annual-changes', 'figure'),
    Output('mead-annual-changes', 'figure'),
    Output('combo-annual-changes', 'figure')],
    [Input('powell-annual-change', 'data'),
    Input('mead-annual-change', 'data'),
    Input('combo-annual-change', 'data'),])
def change_graphs(powell_data, mead_data, combo_data):
    df_powell = pd.read_json(powell_data)
    df_mead = pd.read_json(mead_data)
    df_combo = pd.read_json(combo_data)
    pd.set_option('display.max_columns', None)
    # print(df_powell)
    # print(df_mead)
    # df_combo = df_combo.drop(df_combo.columns[[2,3,4,5]], axis=1)
    # print(df_combo)
    # df_powell['diff'] = (df_powell['diff'] !='n').astype(int)

    mead_traces = []
    powell_traces = []
    combo_traces = []

    # data = powell_traces.sort_index()

    powell_traces.append(go.Bar(
        y = df_powell['diff'],
        x = df_powell.index,
        marker_color = df_powell['color']
    )),

    mead_traces.append(go.Bar(
        y = df_mead['diff'],
        x = df_mead.index,
        marker_color = df_mead['color']
    )),

    combo_traces.append(go.Bar(
        y = df_combo['diff'],
        x = df_combo.index,
        marker_color = df_combo['color']
    )),

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
        title = 'Powell + Mead',
        yaxis = {'title':'Volume (AF)'},
        paper_bgcolor="#1f2630",
        plot_bgcolor="#1f2630",
        font=dict(color="#2cfec1"),
    )

    return {'data': powell_traces, 'layout': powell_layout}, {'data': mead_traces, 'layout': mead_layout}, {'data': combo_traces, 'layout': combo_layout}

@app.callback(
    Output('upper-cur-levels', 'children'),
    [Input('blue-mesa-water-data', 'data'),
    Input('navajo-water-data', 'data'),
    Input('fg-water-data', 'data')])
def get_current_volumes_upper(bm_data, nav_data, fg_data):
    bm_data = pd.read_json(bm_data)
    bm_data.sort_index()
    bm_current_volume = bm_data.iloc[-1,1]
    bm_pct = bm_current_volume / capacities['BLUE MESA RESERVOIR']
    bm_tfh_change = bm_current_volume - bm_data['Value'][-2]
    bm_cy = bm_current_volume - bm_data['Value'][-days]
    bm_yr = bm_current_volume - bm_data['Value'][-366]
    bm_rec_low = bm_data['Value'].min()
    bm_dif_rl = bm_data['Value'].iloc[-1] - bm_rec_low
    bm_rec_low_date = bm_data['Value'].idxmin().strftime('%Y-%m-%d')


    nav_data = pd.read_json(nav_data)
    nav_data.sort_index()
    nav_current_volume = nav_data.iloc[-1,1]
    nav_pct = nav_current_volume / capacities['NAVAJO RESERVOIR']
    nav_tfh_change = nav_current_volume - nav_data['Value'][-2]
    nav_cy = nav_current_volume - nav_data['Value'][-days]
    nav_yr = nav_current_volume - nav_data['Value'][-366]
    nav_rec_low = nav_data['Value'].min()

    fg_data = pd.read_json(fg_data)
    fg_data.sort_index()
    fg_current_volume = fg_data.iloc[-1,1]
    fg_pct = fg_current_volume / capacities['FLAMING GORGE RESERVOIR']
    fg_tfh_change = fg_current_volume - fg_data['Value'][-2]
    fg_cy = fg_current_volume - fg_data['Value'][-days]
    fg_yr = fg_current_volume - fg_data['Value'][-366]
    fg_rec_low = fg_data['Value'].min()

    return html.Div([
        html.Div([
            html.Div([
                html.H6('Blue Mesa', style={'text-align': 'left'})
            ],
                className = 'two columns'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(bm_current_volume), style={'text-align': 'right'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{0:.0%}'.format(bm_pct), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(bm_tfh_change), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(bm_cy), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(bm_yr), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(bm_rec_low), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(bm_dif_rl), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{}'.format(bm_rec_low_date), style={'text-align': 'center'})
            ],
                className='two columns'
            ),
        ],
            className = 'row'
        ),
        html.Div([
            html.Div([
                html.H6('Navajo', style={'text-align': 'left'})
            ],
                className = 'two columns'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(nav_current_volume), style={'text-align': 'right'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{0:.0%}'.format(nav_pct), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(nav_tfh_change), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(nav_cy), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(nav_yr), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(nav_rec_low), style={'text-align': 'center'})
            ],
                className='one column'
            ),
        ],
            className = 'row'
        ),
        html.Div([
            html.Div([
                html.H6('Flaming Gorge', style={'text-align': 'left'})
            ],
                className = 'two columns'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(fg_current_volume), style={'text-align': 'right'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{0:.0%}'.format(fg_pct), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(fg_tfh_change), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(fg_cy), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(fg_yr), style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('{:,.0f}'.format(fg_rec_low), style={'text-align': 'center'})
            ],
                className='one column'
            ),
        ],
            className = 'row'
        ),
    ])

@app.callback([
    Output('blue-mesa-water-data', 'data'),
    Output('navajo-water-data', 'data'),
    Output('fg-water-data', 'data')],
    Input('interval-component', 'n_intervals'))
def clean_powell_data(n):
    # bm_df = pd.read_json(bm_data)
    # nav_df = pd.read_json(nav_data)
    # fg_df = pd.read_json(fg_data)

    blue_mesa_data = 'https://data.usbr.gov/rise/api/result/download?type=csv&itemId=76&before=' + today + '&after=1999-12-30&filename=Blue%20Mesa%20Reservoir%20Dam%20and%20Powerplant%20Daily%20Lake%2FReservoir%20Storage-af%20Time%20Series%20Data%20(2000-01-01%20-%202021-07-14)&order=ASC'

    navajo_data = 'https://data.usbr.gov/rise/api/result/download?type=csv&itemId=613&before=' + today + '&after=1999-12-30&filename=Navajo%20Reservoir%20and%20Dam%20Daily%20Lake%2FReservoir%20Storage-af%20Time%20Series%20Data%20(1999-12-31%20-%202021-07-14)&order=ASC'

    fg_data = 'https://data.usbr.gov/rise/api/result/download?type=csv&itemId=337&before=' + today + '&after=1999-12-30&filename=Flaming%20Gorge%20Reservoir%20Dam%20and%20Powerplant%20Daily%20Lake%2FReservoir%20Storage-af%20Time%20Series%20Data%20(1999-12-31%20-%202021-07-15)&order=ASC'

    with requests.Session() as s:
        blue_mesa_download = s.get(blue_mesa_data)

        blue_mesa_decoded_content = blue_mesa_download.content.decode('utf-8')

        crm = csv.reader(blue_mesa_decoded_content.splitlines(), delimiter=',')

        for i in range(9): next(crm)
        df_bm_water = pd.DataFrame(crm)
        df_bm_water = df_bm_water.drop(df_bm_water.columns[[1,3,4,5,7,8]], axis=1)
        df_bm_water.columns = ["Site", "Value", "Date"]

        # df_bm_water = df_bm_water[1:]
    

        df_bm_water = df_bm_water.set_index("Date")
        df_bm_water = df_bm_water.sort_index()

        navajo_download = s.get(navajo_data)

        navajo_decoded_content = navajo_download.content.decode('utf-8')

        crm = csv.reader(navajo_decoded_content.splitlines(), delimiter=',')

        for i in range(9): next(crm)
        df_nav_water = pd.DataFrame(crm)
        df_nav_water = df_nav_water.drop(df_nav_water.columns[[1,3,4,5,7,8]], axis=1)
        df_nav_water.columns = ["Site", "Value", "Date"]

        # df_bm_water = df_bm_water[1:]
    

        df_nav_water = df_nav_water.set_index("Date")
        df_nav_water = df_nav_water.sort_index()

        fg_download = s.get(fg_data)

        fg_decoded_content = fg_download.content.decode('utf-8')

        crm = csv.reader(fg_decoded_content.splitlines(), delimiter=',')

        for i in range(9): next(crm)
        df_fg_water = pd.DataFrame(crm)
        df_fg_water = df_fg_water.drop(df_fg_water.columns[[1,3,4,5,7,8]], axis=1)
        df_fg_water.columns = ["Site", "Value", "Date"]

        # df_bm_water = df_bm_water[1:]
    

        df_fg_water = df_fg_water.set_index("Date")
        df_fg_water = df_fg_water.sort_index()

    blue_mesa_df = df_bm_water.drop(df_bm_water.index[0])
    navajo_df = df_nav_water.drop(df_nav_water.index[0])
    fg_df = df_fg_water.drop(df_fg_water.index[0])


    return blue_mesa_df.to_json(), navajo_df.to_json(), fg_df.to_json()


@app.callback([
    Output('bm-levels', 'figure'),
    Output('navajo-levels', 'figure'),
    Output('fg-levels', 'figure')],
    [Input('blue-mesa-water-data', 'data'),
    Input('navajo-water-data', 'data'),
    Input('fg-water-data', 'data')])
def lake_graph(bm_data, nav_data, fg_data):
    bm_df = pd.read_json(bm_data)
    nav_df = pd.read_json(nav_data)
    fg_df = pd.read_json(fg_data)

    bm_traces = []
    nav_traces = []
    fg_traces = []

    bm_traces.append(go.Scatter(
        y = bm_df['Value'],
        x = bm_df.index,
    ))

    nav_traces.append(go.Scatter(
        y = nav_df['Value'],
        x = nav_df.index,
    ))

    fg_traces.append(go.Scatter(
        y = fg_df['Value'],
        x = fg_df.index,
    ))

    bm_layout = go.Layout(
        height =400,
        title = 'Blue Mesa Storage',
        yaxis = {'title':'Volume (AF)'},
        paper_bgcolor="#1f2630",
        plot_bgcolor="#1f2630",
        font=dict(color="#2cfec1"),
    )

    nav_layout = go.Layout(
        height =400,
        title = 'Navajo Storage',
        yaxis = {'title':'Volume (AF)'},
        paper_bgcolor="#1f2630",
        plot_bgcolor="#1f2630",
        font=dict(color="#2cfec1"),
    )

    fg_layout = go.Layout(
        height =400,
        title = 'Flaming Gorge Storage',
        yaxis = {'title':'Volume (AF)'},
        paper_bgcolor="#1f2630",
        plot_bgcolor="#1f2630",
        font=dict(color="#2cfec1"),
    )

    return {'data': bm_traces, 'layout': bm_layout}, {'data': nav_traces, 'layout': nav_layout}, {'data': fg_traces, 'layout': fg_layout}




  




