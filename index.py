import dash
from dash import html, dcc

from app import app
from app import server
from homepage import home_page_App
from apps.powell import powell_App


import callbacks

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    # if pathname == '/apps/ur':
    #     return ur_App()
    if pathname == '/apps/powell':
        return powell_App()
    else:
        return home_page_App()

if __name__ == '__main__':
    app.run_server(port=8080, debug=True)