from jupyter_dash import JupyterDash

from dash_table import DataTable, FormatTemplate
from dash_table.Format import Format, Scheme

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
    
import plotly.graph_objects as go

import numpy as np
import pandas as pd
from pandas_datareader import data as web

from datetime import datetime

#--------------------------------------------------------------------------------------------------------------------------------------
class Portfolio:
    now = datetime.now()
    start = datetime(now.year-3, now.month, now.day).strftime("%m-%d-%Y")
                                                              
    def __init__(self, ticks):
        self._ticks = ticks

        # get data
        self._data = web.DataReader(self._ticks, data_source='yahoo', start=self.start)['Adj Close'].values
    
        # we need to shift the days over by 1
        dataShift = np.delete(np.insert(self._data, 0, 1, axis=0), -1, axis=0)
    
        # calculate log returns and delete top row
        self.logR = np.delete(np.log(self._data/dataShift), 0, axis=0)
    
    
    def coskew(self):
        # the number of our stocks
        num = len(self._ticks)
    
        # 2D matrix for tensor product of same height
        # but width num**2
        mtx = np.zeros(shape = (len(self.logR), num**2))
    
        # calculate col means and broadcast
        # against original log returns
        mean = self.logR.mean(0, keepdims=True)
        v1 = (self.logR-mean).T
    
        # complex af math
        for i in range(num):
            for j in range(num):
                vals = v1[i]*v1[j]
                mtx[:, (i * num) + j] = vals/float((len(self.logR) - 1) * self.logR[:,i].std() * self.logR[:,j].std())
    
        # coskewness matrix
        m3 = np.dot(v1,mtx)
    
        # Normalize by dividing by st.dev
        for i in range(num**2):
            use = i%num
            m3[:,i] = m3[:,i]/float(self.logR[:,use].std())
    
        return m3
    
    
    def cokurt(self):
        # the number of our stocks
        num = len(self._ticks)
    
        # 2D matrix for tensor product of same height
        # but width num**2
        mtx1 = np.zeros(shape = (len(self.logR), num**2))
    
        # Second 2D matrix for tensor product
        mtx2 = np.zeros(shape = (len(self.logR), num**3))

        # numpy representation of our data
        # calculate col means and broadcast
        # against original v
        mean = self.logR.mean(0, keepdims=True)
        v1 = (self.logR-mean).T
    
        # complex af math
        for k in range(num):
            for i in range(num):
                for j in range(num):
                        vals = v1[i]*v1[j]*v1[k]
                        mtx2[:,(k * (num**2)) + (i * num) + j] = vals/float((len(self.logR) - 1) * self.logR[:,i].std()*\
                                                                        self.logR[:,j].std() * self.logR[:,k].std())
    
        # Normalize by dividing by st.dev
        m4 = np.dot(v1,mtx2)
        for i in range(num**3):
            use = i%num
            m4[:,i] = m4[:,i]/float(self.logR[:,use].std())
    
        return m4
    
                                                                  
    def build(self, m3, m4):
    
        # for reproducability
        np.random.seed(10)
        trials = 1000
    
        # build arrays
        all_weights = np.zeros((trials, len(self._ticks)))
        ret_arr = np.zeros(trials)
        vol_arr = np.zeros(trials)
        coskew_arr = np.zeros(trials)
        cokurt_arr = np.zeros(trials)

        # let's do the hard math
        for i in range(trials):
    
            # obtain random weights
            weights = np.array(np.random.random(len(self._ticks)))
            weights = weights/np.sum(weights)
            all_weights[i] = weights
    
            # Exp Ret / first moment
            ret_arr[i] = np.sum(np.mean(self.logR, axis=0)*weights*252)
    
            # Volatility / second moment
            vol_arr[i] = np.sqrt(np.dot(weights.T, np.dot(np.cov(self.logR, rowvar=False)*252, weights)))
    
            # Coskew / third moment
            coskew_arr[i] = np.dot(weights.T, np.dot(m3, np.kron(weights,weights)))
    
            # Cokurtosis / fourth moment
            cokurt_arr[i] = np.dot(weights.T, np.dot(m4, np.kron(weights, np.kron(weights,weights))))
    
        return all_weights, ret_arr, vol_arr, coskew_arr, cokurt_arr
    
    
    def graph(self, ret_arr, vol_arr, coskew_arr, cokurt_arr):
    
        # scatter3D properties
        scatter = go.Scatter3d(
            x=cokurt_arr,
            y=vol_arr,
            z=ret_arr,
            mode='markers',
            hoverinfo='skip',
            marker=dict(
                size=3,
                cmax=1,
                cmin=-1,
                color=coskew_arr,     # set color to an array/list of desired values
                colorscale='matter',  # choose a colorscale
                colorbar=dict(
                   title=dict(text='Skew', font=dict(size=14, color='white')),
                    tickfont=dict(color='white'),
                    tickcolor='white',
                    dtick=0.2,
                    ypad=30,
                    xpad=0,
                    ),
                opacity=0.30)
        )
    
        # layout properties
        layout = go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            template='ggplot2',
            
            scene = dict(
                xaxis=dict(dtick=1, title=dict(text='Kurtosis'), color='white', tickcolor='white'),
                yaxis=dict(title=dict(text='Volatility'), tickformat='%', color='white', tickcolor='white'),
                zaxis=dict(dtick=0.05, title=dict(text='Return'), tickformat='%', color='white', tickcolor='white')
            ),
    
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0
            )
        )
    
        return go.Figure(data=scatter, layout=layout) 
    
#--------------------------------------------------------------------------------------------------------------------------------------    
def main():
    # collect stocks
    ticks = []
    while True:    
        boof = input('Add stock to portfolio: ')
        if boof:
            ticks.append(boof)
        else:
            break
    
    # create portfolio object 
    port = Portfolio(ticks)
    W, R, V, S, K = port.build(port.coskew(), port.cokurt())
    
    #make a dataframe
    weights = pd.DataFrame({ticks[i] : W[:,i] for i in range(len(ticks))})
    stats = pd.DataFrame({'Return':R, 'Volatility':V, 'Skew':S, 'Kurtosis':K})
    df = weights.join(stats)
    
    #create a graph object
    graph = port.graph(R, V, S, K)    
    
    # initialize app
    app = JupyterDash(__name__, external_stylesheets=[dbc.themes.FLATLY])
    
    PLOTLY_LOGO = 'https://images.plot.ly/logo/new-branding/plotly-logomark.png'
    percent = FormatTemplate.percentage(2)
    decimal = Format(precision=2, scheme=Scheme.fixed)

    app.layout = html.Div([
        html.Div([
            html.Img(
                src=PLOTLY_LOGO,
                style={
                    'width':'40px',
                    'margin-right':'auto'
                }
            )
        ],
            style={
                'grid-area':'nav',
                'background':'#58d5f6',
                'padding':'10px',
                'display':'flex',
                'align-items':'center',
                'justify-content':'flex-end'
            }
        ),

        html.Div([
            dcc.Graph(
                id='graph',
                figure=graph
            )
        ],
            style={
                'grid-area':'scatter',
                'background':'#236fc8',
                'padding':'10px',
                'color':'white'
            }
        ),

        html.Div([
            DataTable(
                id='table',
                data=df.to_dict('records'),
                columns=[
                    {'id':i, 'name':i, 'type':'numeric', 'hideable':True, 'format':decimal}
                    if i == 'Skew' or i == 'Kurtosis' else
                    {'id':i, 'name':i, 'type':'numeric', 'hideable':True, 'format':percent}
                    for i in df.columns
                ],
                filter_action='native',
                sort_action='native',
                page_current=0,
                page_size=10,
                cell_selectable=False,
                style_as_list_view=True,

                style_table={'overflowX': 'auto'},

                style_header={ # header style
                    'backgroundColor': 'rgb(230, 230, 230, 0.15)',
                    'fontWeight': 'bold'
                },
                style_filter={ # header filter
                    'backgroundColor': 'rgb(230, 230, 230, 0)'
                },    
                style_cell={ # style each individual cell
                    'minWidth': '65px',
                    'color':'white'
                },
                style_data={ # same as above, exclude header and filter cells
                    'whiteSpace': 'normal',
                    'backgroundColor': 'rgb(248, 248, 248, 0)',
                    'height': 'auto'
                },
                style_data_conditional=[{
                    'if': {'row_index': 'even'},
                    'backgroundColor': 'rgb(248, 248, 248, 0.15)'
                }]
            )
        ],
            style={
                    'grid-area':'datatable',
                    'background':'#236fc8',
                    'padding':'10px',
            }
        )
    ],
        style={ # main wrapper
            'height':'100vh',
            'width':'97%',
            'margin':'0 auto',

            'display':'grid', 
            'grid-gap':'5px',

            'grid-template-columns':'5fr 2fr',
            'grid-template-rows':'1fr 12fr',
            'grid-template-areas':'"nav nav"\
                                   "datatable scatter"'


        }
    )
    app.run_server(mode='external', debug=True, port=140)
        
    
if __name__ == '__main__':
    main()