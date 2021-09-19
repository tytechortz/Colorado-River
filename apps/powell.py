import dash    
from dash import html, dcc
from homepage import get_header, get_navbar, get_emptyrow

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

server = app.server

def powell_App():
    return html.Div([
        get_header(),
        get_navbar("non_home"),
        get_emptyrow()
    ])
    
app.layout = powell_App

