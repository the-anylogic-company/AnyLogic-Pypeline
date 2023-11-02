import os
import argparse
import json
import logging
import random
import time
import traceback
from datetime import datetime
from math import ceil
from pathlib import Path
from typing import Optional, Callable

import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
import pandas as pd
import plotly.express as px
import psutil
from dash import dcc, html
from dash.dependencies import Input, Output

# Used to ensure only one app instance at a time
LOCK_FILE = Path(".lock")
# Used in non-testing mode; contains the latest data from the simulation
DATA_FILE = Path("latest_data.json")
# Used in testing mode; causes the app to display random data on each update
TEST_MODE = False
# Locally hosted server which displays the website
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def build_app_layout(num_callcenters: int) -> None:
    """
    Builds the layout of the Dash web application based on the number of call centers.

    The layout includes a header and two tabs: one containing gauges for utilization, and another containing a stacked bar chart for call output counts.
    The number of call centers influences the number of gauges created and the number of bars displayed.

    Parameters
    ----------
    num_callcenters : int
        The number of call centers to be tracked in the application. This parameter influences the layout of the dashboard.
    """
    rows = min(3, ceil(num_callcenters / 3))
    cols = ceil(num_callcenters / rows)

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
                    dbc.Col([ html.P("0.000", id='text-update-time', className='my-0 font-monospace') ], className='col-7'),
                    dbc.Col([ html.P('hours', className='my-0 fw-light text-end') ], className='col-2')
                ], className='text-start'),
                dbc.Row([
                    dbc.Col([ html.P('Date:', className='my-0 fw-light') ], className='col-3'),
                    dbc.Col([ html.P("Jan 01 2020 12:00 AM", id='text-update-date', className='my-0 font-monospace') ], className='col-9')
                ], className='text-start'),
            ], className='col-2')
        ], className='text-center align-items-center')
    ]

    # elements for the utilization tab (gauges)
    tab1_elements = []
    for i in range(rows):
        row_elements = []
        for j in range(cols):
            index = i * cols + j
            if index >= num_callcenters:
                break
            col = dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        daq.Gauge(
                            id=f'gauge-{index}',
                            value=0,
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

    # invisible element to update data elements
    elements.append(
        dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
    )
    
    app.layout = html.Div(elements, className='mx-5 my-1')


def decorate_callbacks(num_callcenters: int, data_file: Optional[Path] = None) -> Callable:
    """
    A wrapper function for all decorators. It's needed due to the number of call centers being dynamic (per run).

    Parameters
    ----------
    num_callcenters : int
        The number of call centers to be tracked in the application. This parameter influences the number of values returned.
    data_file: Path, optional
        The file with the latest information for the call centers. It may not exist if running in test mode.

    Returns
    -------
    Callable
        The decorated function(s) registered by Dash
    """
    outputs = [Output(f'gauge-{n}', 'value') for n in range(num_callcenters)] + [Output('text-update-time', 'children'), Output('text-update-date', 'children')] + [Output("graph", "figure")]
    inputs = [Input("interval-component", "n_intervals")]
    @app.callback(outputs, inputs)
    def update_plots(n_intervals: int) -> list:
        """
        A callback used by Dash to get the information needed to update all plots.

        Parameters
        ----------
        n_intervals : int
            A count for how many updates have occurred.

        Returns
        -------
        list
            A list of values for Dash to update the components.
        """
        if TEST_MODE:
            # fake some data
            data = [(n_intervals+i+random.randint(0,3))%101 for i in range(num_callcenters)]
            update_timestamp = str(round(time.time(),3))[-7:]
            update_datestamp = datetime.now().strftime("%b %d %Y %I:%S %p")
            barchart_data = [[i, random.randint(5,15), random.randint(5,15), random.randint(0,5)] for i in range(num_callcenters)]
        else:
            # read latest info from data file
            with open(data_file) as f:
                jdata = json.load(f)
            data = jdata['utilizations']
            update_timestamp = jdata['update_time']
            update_datestamp = jdata['update_date']
            barchart_data = jdata['counts']
            
        # convert barchart data to figure
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
    
        return data[:num_callcenters] + [update_timestamp, update_datestamp] + [fig]
    return update_plots


def create_lock_file() -> None:
    """
    Creates a 'lock' file to prevent multiple simultaneous executions of the application.

    The 'lock' file contains information about the currently running process, written a JSON file.

    Raises
    ------
    FileExistsError
        If the 'lock' file already exists, indicating that the application is already running.
    """
    if LOCK_FILE.exists():
        raise FileExistsError(f"Lock file '{LOCK_FILE}' already exists! Ensure the process for it and the file is killed before running.")

    proc = psutil.Process(os.getpid())
    info = proc.as_dict(['pid', 'name', 'create_time', 'cmdline'])
    info['parents'] = [p.as_dict(['pid', 'name', 'create_time']) for p in proc.parents()]
    info['children'] = [c.as_dict(['pid', 'name', 'create_time']) for c in proc.children()]
    LOCK_FILE.write_text(json.dumps(info, indent=4))


def validate_lock_file(raise_if_active:bool=True) -> None:
    """
    Validates the existence and necessity of the lock file. 

    If the lock file doesn't exist, no action is taken.
    If it exists, the function verifies whether the process that created the lock file is still active, deleting the file if it's no longer active.

    Parameters
    ----------
    raise_if_active : bool, optional
        Whether to trigger an error if the process that created the lock file is still active.
        This should be set to True (default) if the process is expected to be dead.

    Raises
    ------
    RuntimeError
        When the validation-check for the process to be dead fails (i.e., it's still active when it should not be).
    """
    if not LOCK_FILE.exists():
        return

    process_info = json.loads(LOCK_FILE.read_text())
    pid = process_info['pid']

    try:
        proc = psutil.Process(pid)
        if raise_if_active:
            raise RuntimeError(f"The process with ID {pid} is alive and it's expected to be dead!")
    except psutil.NoSuchProcess:
        LOCK_FILE.unlink()


def cleanup() -> None:
    """
    Clear all temporary files. It's intended only to be called after the server is shutdown and by a parent process
    (as the lock file will not be removed if called by the same process which started the server).

    Raises
    ------
    RuntimeError
        When the validation-check for the process to be dead fails (i.e., it's still active when it should not be).
    """
    validate_lock_file(True)
    if DATA_FILE.exists():
        DATA_FILE.unlink()


def main() -> None:
    """
    The entry point for the application.

    Raises
    ------
    RuntimeError
        If the previous server was not shutdown correctly (it's still active and will need to be force-quit).
    """
    parser = argparse.ArgumentParser(
        prog='app.py',
        description='Python webapp using Dash for the AnyLogic Model "Interconnected Call Centers" - A Pypeline Demo'
    )
    parser.add_argument('-n', '--num', type=int, default=16, help='Number of call centers')
    parser.add_argument('-f', '--file', type=str, default=None, help='Name of file with updated data content; if omitted random data is used')
    args = parser.parse_args()

    # will halt execution if the previous app was not quit properly (likely due to force-quitting the model)
    validate_lock_file(True)

    # update the lock file with the current process's info
    create_lock_file()

    if not args.file:
        # designate as testing mode when data file is not provided
        global TEST_MODE
        TEST_MODE = True
    else:
        # override global filename var for data content
        global DATA_FILE
        DATA_FILE = Path(args.file)

    # construct the layout and then start the server
    build_app_layout(args.num)
    callback_func = decorate_callbacks(args.num, DATA_FILE)

    try:
        # lock the current thread to run/host the server
        app.run_server(debug=False)
    except Exception as e:
        # purposefully generic error handling
        traceback.print_exception(e)
    finally:
        # remove the lock file manually (known to be finished)
        LOCK_FILE.unlink()


if __name__ == '__main__':
    main()
