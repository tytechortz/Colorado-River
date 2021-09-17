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



app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

server = app.server

def get_header():

    header = html.Div([

        # html.Div([], className = 'col-2'), #Same as img width, allowing to have the title centrally aligned

        html.Div([
            html.H2(
                'Colorado River Water Storage',
                className='twelve columns',
                style={'text-align': 'center'}
            ),
        ],
            className='row'
        ),
    ])

    return header


def get_navbar(p = 'homepage'):
    navbar_homepage = html.Div([
        html.Div([], className='col-2'),
        html.Div([
            dcc.Link(
                html.H6(children='Upper Reservoirs'),
                href='/apps/ur'
            )
        ],
            className='col-2',
            style={'text-align': 'center'}
        ),
        html.Div([], className = 'col-2')
    ],
    className = 'row',
    style = {'background-color' : 'dark-green',
            'box-shadow': '2px 5px 5px 1px rgba(0, 100, 0, .5)'}
    )
    navbar_ur = html.Div([
        html.Div([], className='col-2'),
        html.Div([
            dcc.Link(
                html.H6(children='Home'),
                href='/homepage'
            )
        ],
            className='col-2',
            style={'text-align': 'center'}
        ),
        html.Div([], className = 'col-2')
    ],
    className = 'row',
    style = {'background-color' : 'dark-green',
            'box-shadow': '2px 5px 5px 1px rgba(0, 100, 0, .5)'}
    )
    if p == 'homepage':
        return navbar_homepage
    elif p == 'revenue':
        return navbar_ur
    
def get_emptyrow(h='15px'):
    """This returns an empty row of a defined height"""

    emptyrow = html.Div([
        html.Div([
            html.Br()
        ], className = 'col-12')
    ],
    className = 'row',
    style = {'height' : h})

    return emptyrow



def home_page_App():
    return html.Div([
        get_header(),
        get_navbar('homepage'),
        get_emptyrow(),

        html.Div([
            html.Div([
                dcc.Loading(
                id="loading-powell",
                type="default",
                children=html.Div(dcc.Graph(id='powell-levels'))),
            ],
                className='four columns'
            ),
            html.Div([
                dcc.Loading(
                id="loading-mead",
                type="default",
                children=html.Div(dcc.Graph(id='mead-levels'))),
            ],
                className='four columns'
            ),
            html.Div([
                dcc.Loading(
                id="loading-combo",
                type="default",
                children=html.Div(dcc.Graph(id='combo-levels'))),
            ],
                className='four columns'
            ),
        ],
            className='row'
        ),
        html.Div([
            html.Div([
                html.H6('Current Storage - AF', style={'text-align': 'center'})
            ],
                className='three columns'
            ),
            html.Div([
                html.H6('Pct. Full', style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('24 hr', style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('C.Y.', style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('Year', style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('Rec Low', style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('Diff', style={'text-align': 'center'})
            ],
                className='one column'
            ),
            html.Div([
                html.H6('Rec Low Date', style={'text-align': 'center'})
            ],
                className='two columns'
            ),
        ],
            className='row'
        ),
        html.Div([
            html.Div(id='cur-levels')
        ],
            className='row'
        ),
        dcc.Interval(
            id='interval-component',
            interval=300*1000, # in milliseconds
            n_intervals=0
        ),
        dcc.Store(id='powell-water-data'),
        dcc.Store(id='mead-water-data'),
        dcc.Store(id='combo-water-data'),
        html.Div(id='powell-annual-change', style={'display': 'none'}),
        html.Div(id='mead-annual-change', style={'display': 'none'}),
        html.Div(id='combo-annual-change', style={'display': 'none'}),

    ])

app.layout = home_page_App

   

