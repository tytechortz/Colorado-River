import dash
from dash import html, dcc

import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime as dt
from app import app
import dash_bootstrap_components as dbc




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

        # html.Div([
        #     html.H1(children='Colorado Cannabis',
        #             style = {'textAlign' : 'center', 'color':'white'}
        #     )],
        #     className='col-12',
        #     style = {'padding-top' : '1%'}
        # ),
        # ],
        # className = 'row',
        # style = {'height' : '4%',
        #         'background-color' : 'green'}
        # )

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
        get_emptyrow()
    ])
    

   