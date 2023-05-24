import argparse
import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
import pandas as pd
import plotly.express as px
import threading
import time
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from datetime import datetime
from math import ceil, sqrt

# whether the app is running in test mode (i.e., strictly in python env); will generate fake data
TEST_MODE = False

# default to max possible centers
num = 16

# web app using bootstrap
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# utilization (0-100) of resources at the given call center
data = [0 for _ in range(num)]

# index, num local calls, num ext calls, num balked calls
barchart_data = [[0, 0, 0, 0] for _ in range(num)]

# model time in hours at last update
update_timestamp = "0.000"

# model date at last update
update_datestamp = "Jan 01 2020 12:00 AM"  


def build(num_callcenters):
    """Construct the app's layout based on the number of call centers."""
    global num
    num = num_callcenters
    global timestamp_units
    global app
    global data
    global update_timestamp
    global update_datestamp
    
    #rows = round(sqrt(num_callcenters))
    rows = min(3, ceil(num/3))
    cols = ceil(num_callcenters/rows)

    # Define the list of root-level objects
    elements = [
        # header
        dbc.Row([
            dbc.Col([
                # main title
                html.H1('Interconnected Call Center Web App', className='fw-semibold')
            ], className='col-10'),
            dbc.Col([
                # info about last update
                dbc.Row([html.P('Last model update', className='my-0 text-decoration-underline')]),
                dbc.Row([
                    dbc.Col([ html.P('Time:', className='my-0 fw-light') ], className='col-3'),
                    dbc.Col([ html.P(update_timestamp, id='text-update-time', className='my-0 font-monospace') ], className='col-7'),
                    dbc.Col([ html.P('hours', className='my-0 fw-light text-end') ], className='col-2')
                ], className='text-start'),
                dbc.Row([
                    dbc.Col([ html.P('Date:', className='my-0 fw-light') ], className='col-3'),
                    dbc.Col([ html.P(update_datestamp, id='text-update-date', className='my-0 font-monospace') ], className='col-9')
                ], className='text-start')
            ], className='col-2')
        ], className='text-center align-items-center')
    ]

    # elements for the utilization tab (gauges)
    tab1_elements = []
    for i in range(rows):
        row_elements = []
        for j in range(cols):
            index = i * cols + j
            if index >= num:
                break
            col = dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        daq.Gauge(
                            id=f'gauge-{index}',
                            value=data[i * rows + j],
                            min=0,
                            max=100,
                            units="%",
                            label=f'Center #{index}',
                            color={"default": "black",
                                   "gradient": True,
                                   "ranges": {"green":[0,39],"lawngreen":[39,41],"gold": [41,59],"orange": [59,61], "darkorange": [61,79], "orangered": [79,81], "red":[81,100]}},
                            showCurrentValue=True,
                            style={'textAlign': 'center'},
                            size=150
                        )
                    ])
                ], className='mb-2', style={'max-height': '250px'})
            ])
            row_elements.append(col)
        tab1_elements.append( dbc.Row(row_elements) )

    # elements for the outcomes tab (stacked bar chart)
    tab2_elements = [
        html.Div([
            dcc.Graph(id="graph"),
        ])
    ]

    # combine elements for both tabs into single object
    tabs = dbc.Tabs([
        dbc.Tab(tab1_elements, label="Utilizations"),
        dbc.Tab(tab2_elements, label="Call outputs"),
    ])

    # add tab section and invisible event timers to layout
    elements.append(tabs)

    # invisible element to update gauges
    elements.append(
        dcc.Interval(id='interval-component', interval=250, n_intervals=0),
    )

    # invisible element to update 'last updated' text elements
    elements.append(
        dcc.Interval(id='interval-component-2', interval=250, n_intervals=0),
    )

    # invisible element to update bar chart
    elements.append(
        dcc.Interval(id='interval-component-3', interval=250, n_intervals=0),
    )

    app.layout = html.Div(elements, className='mx-5 my-1')
            
    
def decorate_callback():
    # need to separately add some decorators due to dynamic number of call centers

    # decorators for updating gauges
    global num
    outputs = [Output(f'gauge-{n}', 'value') for n in range(num)] # + [Output('text-update-time', 'children'), Output('text-update-date', 'children')]
    inputs = [Input("interval-component", "n_intervals")]
    @app.callback(outputs, inputs)
    def update_gauges(n_intervals):
        global data
        global TEST_MODE
        if TEST_MODE:
            # fake some data
            data = [(v+i)%101 for i,v in enumerate(data)]
        return data[:num]# + [update_timestamp, update_datestamp]

    
    # decorators for updating 'update' stamps
    @app.callback([Output('text-update-time', 'children'), Output('text-update-date', 'children')],
                  [Input("interval-component-2", "n_intervals")])
    def update_stamps(n_intervals):
        global update_timestamp
        global update_datestamp
        global TEST_MODE
        if TEST_MODE:
            update_timestamp = str(round(time.time(),3))[-7:]
            update_datestamp = datetime.now().strftime("%b %d %Y %I:%S %p")
        return [update_timestamp, update_datestamp]


    # decorator for updating the counts of each CC's bars
    @app.callback(
        Output("graph", "figure"), 
        Input("interval-component-3", "n_intervals"))
    def update_bar_chart(n_intervals):
        global barchart_data
        global TEST_MODE
        if TEST_MODE:
            import random
            barchart_data = [[i, random.randint(5,15), random.randint(5,15), random.randint(0,5)] for i in range(16)]
        df = pd.DataFrame(barchart_data, columns=['index', 'local', 'ext', 'balk'])
        
        # reformat the dataframe to create a long format (with 'index', 'variable', and 'value' columns)
        df_melt = pd.melt(df, id_vars=['index'], value_vars=['local', 'ext', 'balk'])

        # create a stacked bar chart
        fig = px.bar(df_melt, x='index', y='value', color='variable', barmode='stack')
        
        # update labels shown
        fig.update_layout(
            xaxis=dict(tickmode='linear', dtick=1),
            xaxis_title='Call Center (index)',
            yaxis_title='Count',
            legend_title='Call type',
            hovermode='x unified')

        # each line in hover text shows just the count
        fig.update_traces(hovertemplate="%{value} calls")
        return fig
    
    return update_gauges, update_stamps, update_bar_chart


def run_server() -> None:
    """ Simple callable to trigger the server starting (called by `initialize`) """
    app.run_server(debug=False)


def initialize(num):
    """ Entry point to build and launch the web app

    Args:
        num: How many call centers that are being tracked

    """
    
    # Setup the structure of the web app
    build(num)

    # Setup the callbacks to update the values as the model is running
    callbacks = decorate_callback()
    
    # Start the server in a separate thread
    thread = threading.Thread(target=run_server)
    thread.start()

    return callbacks, thread


# Testing code if run from within a native Python environment
if __name__ == '__main__':
    # designate as testing mode so that values are updated with faked data
    TEST_MODE = True
    
    parser = argparse.ArgumentParser(
        prog='app.py',
        description='Python webapp using Dash for the AnyLogic Model "Interconnected Call Centers" - A Pypeline Demo'
        )
    parser.add_argument('-n', '--num', type=int, default=16, help='Number of call centers')
    args = parser.parse_args()

    initialize(args.num)
