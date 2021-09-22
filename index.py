import dash
from dash import html, dcc

from app import app
from app import server
from homepage import home_page_App
from apps.powell import powell_App
from apps.drought import drought_App
from apps.ur import ur_App


import callbacks

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='powell-water-data'),
    dcc.Store(id='mead-water-data'),
    dcc.Store(id='combo-water-data'),
    dcc.Store(id='powell-annual-change'),
    dcc.Store(id='mead-annual-change'),
    dcc.Store(id='combo-annual-change'),
    dcc.Store(id='blue-mesa-water-data'),
    dcc.Store(id='navajo-water-data'),
    dcc.Store(id='fg-water-data'),
    # dcc.Store(id='upper-cur-levels'),
])

@app.callback(dash.dependencies.Output                    ('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    # if pathname == '/apps/ur':
    #     return ur_App()
    if pathname == '/apps/powell':
        return powell_App()
    elif pathname == '/apps/drought':
        return drought_App()
    elif pathname == '/apps/ur':
        return ur_App()
    else:
        return home_page_App()

if __name__ == '__main__':
    app.run_server(port=8080, debug=True)