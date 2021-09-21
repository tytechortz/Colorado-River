import dash
from dash import html, dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from homepage import get_header, get_navbar, get_emptyrow


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
                id='drought-interval-component',
                interval=100*1000, # in milliseconds
                n_intervals=0
            ),
            dcc.Store(id='drought-data'),
            # dcc.Store(id='combo-water-data'),
            # dcc.Store(id='combo-annual-change-drought'), 
            # dcc.Store(id='combo-levels-drought'),
            # dcc.Store(id='combo-water-drought'),   
        ])
    ])


app.layout = drought_App