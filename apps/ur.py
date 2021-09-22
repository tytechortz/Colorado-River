import dash
from dash import html, dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from homepage import get_header, get_navbar, get_emptyrow


app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

server = app.server

def ur_App():
    return html.Div([
        get_header(),
        get_navbar("non_home"),
        get_emptyrow(),

        html.Div([
            html.Div([
                dcc.Graph(
                    id='bm-levels',
                ),
            ],
                className='four columns'
            ),
            html.Div([
                dcc.Graph(
                    id='navajo-levels',
                ),
            ],
                className='four columns'
            ),
            html.Div([
                dcc.Graph(
                    id='fg-levels',
                ),
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
            html.Div(id='upper-cur-levels')
        ],
            className='row'
        ),
        dcc.Interval(
            id='interval-component',
            interval=500*1000, # in milliseconds
            n_intervals=0
        ),
    ])

app.layout = ur_App