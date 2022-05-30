import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import dash
from dash import dcc, Dash, html
from dash.dependencies import Input, Output
import base64
from plotly.subplots import make_subplots
import json
import requests
import warnings
from math import ceil
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import Dense, Dropout, LSTM
import datetime as dt
warnings.filterwarnings("ignore")

# ----------------------------------------------------------------------------------------------------------------------
# Calling the app
app = Dash(external_stylesheets=[dbc.themes.GRID])
server = app.server

# ----------------------------------------------------------------------------------------------------------------------
# Building the necessary elements / functions

coins_bc4 = ['ADA-USD', 'ATOM-USD', 'AVAX-USD', 'AXS-USD', 'LUNA1-USD', 'MATIC-USD', 'BTC-USD', 'ETH-USD', 'SOL-USD', "LINK-USD"]
coins_added = ["DOGE-USD", "DOT-USD", "TRX-USD", "SHIB-USD", "LTC-USD", "XMR-USD", "FLOW-USD", "HNT-USD", "QNT-USD", "PAXG-USD"]
coins = coins_bc4 + coins_added
coins.sort()

dropdown_leaderboard = dcc.Dropdown(
    id='leaderboard_drop',
    className = "dropdown",
    # options={"1d":"Last Day", "5d":"Last Five Days", "1mo":"Last Month", "2mo":"Last Two Months", "3mo":"Last Quarter", "1y":"Last Year"},
    options={"5d":"Last Five Days", "1mo":"Last Month", "2mo":"Last Two Months", "3mo":"Last Quarter", "1y":"Last Year"},
    value='1y',
    multi=False,
    clearable = False,
    style={"box-shadow" : "1px 1px 3px lightgray", "background-color" : "white"}
    )

dropdown_tech_analysis_coin = dcc.Dropdown(
    id='tech_analysis_coin_drop',
    className = "dropdown",
    options=coins,
    value='BTC-USD',
    multi=False,
    clearable = False,
    style={"box-shadow" : "1px 1px 3px lightgray", "background-color" : "white"}
    )
dropdown_tech_analysis_range = dcc.Dropdown(
    id='tech_analysis_range_drop',
    className = "dropdown",
    # options={"4h":"Last Four Hours", "1d":"Last Day", "5d":"Last Five Days", "1mo":"Last Month", "3mo":"Last Quarter", "1y":"Last Year", "max":"Coin Life" },
    options={"1d":"Last Day", "5d":"Last Five Days", "1mo":"Last Month", "3mo":"Last Quarter", "1y":"Last Year", "max":"Coin Life" },
    value='max',
    multi=False,
    clearable = False,
    style={"box-shadow" : "1px 1px 3px lightgray", "background-color" : "white"}
    )
dropdown_tech_analysis_indicator = dcc.Dropdown(
    id='tech_analysis_indicator_drop',
    className = "dropdown",
    # options={"4h":"Last Four Hours", "1d":"Last Day", "5d":"Last Five Days", "1mo":"Last Month", "3mo":"Last Quarter", "1y":"Last Year", "max":"Coin Life" },
    options={"EMA" : "Exponential Moving Average", "SMA" : "Simple Moving Average"},
    value='EMA',
    multi=False,
    clearable = False,
    style={"box-shadow" : "1px 1px 3px lightgray", "background-color" : "white"}
    )

#downloading all data that will be needed for the leaderboard
data_lb_1d = yf.download(tickers=coins, period = "1d", interval = "15m")
data_lb_5d = yf.download(tickers=coins, period = "5d", interval = "60m")
data_lb_1y = yf.download(tickers=coins, period = "1y", interval = "1d")
data_lb_1mo = data_lb_1y.reset_index().loc[data_lb_1y.reset_index()["Date"] >= datetime.now() - relativedelta(months=1)].set_index("Date")
data_lb_2mo = data_lb_1y.reset_index().loc[data_lb_1y.reset_index()["Date"] >= datetime.now() - relativedelta(months=2)].set_index("Date")
data_lb_3mo = data_lb_1y.reset_index().loc[data_lb_1y.reset_index()["Date"] >= datetime.now() - relativedelta(months=3)].set_index("Date")

#donwloading coin price 
leaderboard_prices = pd.DataFrame(columns = ["Price"])
for coin in coins:
    if coin == "LUNA1-USD":
        coin = "LUNA-USD"
    key = "https://api.binance.com/api/v3/ticker/price?symbol="
    coin_key = coin.replace("-", "")
    coin_key = coin_key + "T"
    url = key + coin_key
    data = requests.get(url)
    data = data.json()
    rounded = np.round(float(data["price"]), 3)
    leaderboard_prices.loc[coin] = rounded


# ----------------------------------------------------------------------------------------------------------------------
# Functions to create plots

image_filename = 'crypto.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

def create_leaderboard(lb_range = "1d"):
    """creates a leaderboard of the most performing coins in a time range 
    possible values for argument: one day 1d, five days 5d, one month 1mo, 2months 2mo, one quarter 3mo, one year 1y"""

    if (lb_range == "1d"):
        data_lb = data_lb_1d
    elif (lb_range == "5d"):
        data_lb = data_lb_5d
    elif (lb_range == "1mo"):
        data_lb = data_lb_1mo
    elif (lb_range == "2mo"):
        data_lb = data_lb_2mo
    elif (lb_range == "3mo"):
        data_lb = data_lb_3mo
    else:
        data_lb = data_lb_1y

    # creating empty df
    leaderboard_prc = pd.DataFrame(columns = ["Percentage"])
    # appending percentage change in the timeframe for each coin into leaderboard df
    for coin in coins:
        prc = ((data_lb["Close", coin].iloc[-1] - data_lb["Close", coin].iloc[0]) / data_lb["Close", coin].iloc[-1]) * 100
        prc = np.round(prc, 2)
        leaderboard_prc.loc[coin] = prc

    leaderboard = leaderboard_prc.merge(right=leaderboard_prices, how="inner", on=leaderboard_prc.index).set_index("key_0")
    leaderboard.sort_values("Percentage", ascending=False, inplace=True)
    return data_lb, leaderboard

def get_linegraph(close_price, coin_name):

    if close_price[0] > close_price[-1]:
        fig = go.Scatter(
            x = close_price.index,
            y = close_price.values,
            name = coin_name,
            marker_color="red",
            fill="tozeroy",
            fillcolor="rgb(251, 180, 174)"
        )
    else:
        fig = go.Scatter(
            x = close_price.index,
            y = close_price.values,
            name = coin_name,
            marker_color="green",
            fill="tozeroy",
            fillcolor="rgb(204, 235, 197)"
        )
    return fig


def get_top_bot(data_lb, leaderboard):
    """returns the linegraph figures for the two top and bottom performancers for the range specified in create_leaderboard() function """
    # leaderboard = leaderboard["Percentage"]
    leaderboard.dropna(inplace=True)
    fig1 = get_linegraph(data_lb["Close", leaderboard.iloc[0].name], leaderboard.iloc[0].name)
    fig2 = get_linegraph(data_lb["Close", leaderboard.iloc[1].name], leaderboard.iloc[1].name)
    fig3 = get_linegraph(data_lb["Close", leaderboard.iloc[-2].name], leaderboard.iloc[-2].name)
    fig4 = get_linegraph(data_lb["Close", leaderboard.iloc[-1].name], leaderboard.iloc[-1].name)
    return fig1, leaderboard.iloc[0].name, fig2, leaderboard.iloc[1].name, fig3, leaderboard.iloc[-2].name, fig4, leaderboard.iloc[-1].name



def plot_leaderboard(leaderboard):
    """returns the table leaderboard figure"""

    leaderboard.dropna(axis = 0, inplace=True)
    fig = go.Figure(data=[go.Table(
    header=dict(values=["Coins", "Percentage change in closing price", "Closing Price"],
                fill_color='#dae9f5',
                align='center'),
    cells=dict(values=[leaderboard.index, leaderboard["Percentage"].values, leaderboard["Price"].values],
               fill_color='white',
               align='center'))
    ])
    return fig


def plot_technical_analyis(coin='BTC-USD', range="max", indicator = "EMA"):
    """returning technical analysis plots for a certain coin over the time of existence of the coin"""

    '''
    The function takes the cyptocurrency, look-back periods and the indicator type(SMA or EMA) as input 
    and returns the respective MA Crossover chart along with the buy/sell signals for the given period.
    '''
    # short_window - (int)lookback period for short-term moving average. Eg: 5, 10, 20 
    # long_window - (int)lookback period for long-term moving average. Eg: 50, 100, 200
    # moving_avg - (str)the type of moving average to use ('SMA' or 'EMA')
    # display_table - (bool)whether to display the date and price table at buy/sell positions(True/False)
    
    
    short_window = 20
    long_window = 50


    if (range in ["1d", "5d"]):
        df = yf.download(tickers=coin, period = range, interval = "15m")
        df.reset_index(inplace = True)
        short_window = 9
        long_window = 21
        boll_window = 18
        x_axis = df["Datetime"]
    if (range in ["1mo", "3mo", "1y", "max"]):
        df = yf.download(tickers=coin, period = range, interval = "1d")
        short_window = 100
        long_window = 200
        boll_window = 30
        x_axis = df.index



    # column names for long and short moving average columns
    short_window_col = str(short_window) + '_' + indicator
    long_window_col = str(long_window) + '_' + indicator 

    df['sma'] = df['Close'].rolling(boll_window).mean()
    df['std'] = df['Close'].rolling(boll_window).std(ddof = 0)
    
    if indicator == 'SMA':
        # Create a short simple moving average column
        df[short_window_col] = df['Close'].rolling(window = short_window, min_periods = 1).mean()

        # Create a long simple moving average column
        df[long_window_col] = df['Close'].rolling(window = long_window, min_periods = 1).mean()

    elif indicator == 'EMA':
        # Create short exponential moving average column
        df[short_window_col] = df['Close'].ewm(span = short_window, adjust = False).mean()

        # Create a long exponential moving average column
        df[long_window_col] = df['Close'].ewm(span = long_window, adjust = False).mean()

    # create a new column 'Signal' such that if faster moving average is greater than slower moving average 
    # then set Signal as 1 else 0.
    df['Signal'] = 0.0  
    df['Signal'] = np.where(df[short_window_col] > df[long_window_col], 1.0, 0.0) 

    # create a new column 'Position' which is a day-to-day difference of the 'Signal' column. 
    df['Position'] = df['Signal'].diff() 
    
    layout = go.Layout(
        autosize=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    
        xaxis= go.layout.XAxis(linecolor = 'black',
                              linewidth = 1,
                              mirror = True),
    
        yaxis= go.layout.YAxis(linecolor = 'black',
                              linewidth = 1,
                              mirror = True),
    
        margin=go.layout.Margin(
            l=50,
            r=50,
            b=100,
            t=100,
            pad = 4
        )
    )
    
    fig1 = go.Figure(
    
        data=[go.Candlestick(
        x=x_axis,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        increasing_line_color= 'Green', decreasing_line_color= 'Red'
    ), #
                go.Scatter(
                    x = x_axis, 
                    y = df[short_window_col],
                    mode = 'lines', 
                    name = short_window_col,
                    line = {'color': '#00ff11'}
                ),
                go.Scatter(
                    x = x_axis, 
                    y = df[long_window_col],
                    mode = 'lines',
                    name = long_window_col,
                    line = {'color': '#ff0008'}
                ),
                go.Scatter(
                    x = x_axis[df["Position"] == -1], 
                    y = df[long_window_col][df["Position"] == -1],
                    mode = 'markers',
                    marker= dict(symbol='triangle-down', size = 14),
                    name = 'Sell',
                    line = {'color': '#ff0000'}
                ),
                go.Scatter(
                    x = x_axis[df["Position"] == 1], 
                    y = df[short_window_col][df["Position"] == 1],
                    mode = 'markers',
                    marker= dict(symbol='triangle-up', size = 14),
                    name = 'Buy',
                    line = {'color': '#00ff95'}
                ), 
                 go.Scatter(
                    x = x_axis, 
                    y = df["sma"] + (df['std'] * 2),
                    line_color = 'gray',
                    line = {'dash': 'dash'},
                    name = 'upper band',
                    opacity = 0.3
                ),
                go.Scatter(
                    x = x_axis, 
                    y = df["sma"] - (df['std'] * 2),
                    line_color = 'gray',
                    line = {'dash': 'dash'},
                    fill = 'tonexty',
                    name = 'lower band',
                    opacity = 0.3
                ),
            ]
        ,layout=layout)

    fig2 = go.Figure(
                data = go.Bar(
                    x = x_axis,
                    y = df["Volume"],
                    marker_color = "#85acc9"
                )
    )

    fig2.update_layout(
        title = f'The Barchart graph showing volume for {coin}',
        xaxis_title = 'Date',
        yaxis_title = 'Amount of asset traded during the day',
        xaxis_rangeslider_visible = False,
        autosize=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig1.update_layout(
        legend=dict(yanchor="top", y=0.9, xanchor="left", x=0.06),
        title = f'The Candlestick graph for {coin}',
        xaxis_title = 'Date',
        yaxis_title = coin,
        xaxis_rangeslider_visible = False #DEFAULT TRUE, WHILE TAKING SCREENSHOT WE PUT IT TO FALSE
    )

    return fig1, fig2

def plot_info_coin(coin = 'BTC-USD'):
    #changes code for binance API
    if coin == "LUNA1-USD":
        coin = "LUNA-USD"
    rounded = leaderboard_prices.loc[coin][0].astype("str")
    string = "Today's price for " + coin + " is " + rounded
    return string, rounded


def prediction(coin='BTC-USD'):
    #end = dt.date.today()
    #start = end - dt.timedelta(days=365)
    #df = yf.download(tickers=coin, start=start,end=end, interval="1d")
    #df = pd.DataFrame(df['Close'])

    df = pd.DataFrame(data_lb_1y["Close", coin])
    df = df["Close"].tail(100)

    tf.random.set_seed(12)

    # scaling for better LSTM performance
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df.values.reshape(-1, 1))

    # how many days to use for testing
    testing_days = ceil(len(scaled) * 0.2)
    # how many days to go back for predicting one value
    prediction_days = ceil(ceil(len(scaled) * 0.8) * 0.05)
    # how many days in the future to predict from the day after the last date (zero means it predicts the day after)
    future_day = 1

    X, y = [], []

    # appending target and input data to be later split
    for i in range(prediction_days, len(scaled) - future_day):
        X.append(scaled[i - prediction_days:i, 0])
        y.append(scaled[i + future_day, 0])

    X_train = X[:-testing_days]
    y_train = y[:-testing_days]

    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    # Building and training the model
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    # Prevent overfitting
    model.add(tf.keras.layers.Dropout(0.2))

    model.add(tf.keras.layers.LSTM(units=50, return_sequences=True))

    model.add(tf.keras.layers.Dropout(0.2))

    model.add(tf.keras.layers.LSTM(units=50))

    model.add(tf.keras.layers.Dropout(0.2))

    model.add(tf.keras.layers.Dense(units=1))

    model.compile(optimizer='adam', loss='mse')
    model.fit(X_train, y_train, epochs=1)

    model_inputs = scaled[len(scaled) - prediction_days - testing_days:]

    # building test data with same logic as train data, but for last records
    X_test = []
    for i in range(prediction_days, len(model_inputs)):
        X_test.append(model_inputs[i - prediction_days:i, 0])

    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    predicted_prices_sc = model.predict(X_test)
    # again prices in dollars
    predicted_prices = scaler.inverse_transform(predicted_prices_sc.reshape(-1, 1))

    df["Predicted Price"] = np.NaN

    # add next day
    df.reset_index(inplace=True)
    df["Date"] = pd.to_datetime(df['Date'])
    # last date in which we'll predict the  price
    prediction_date = df.iloc[len(df) - 1]["Date"] + timedelta(days=future_day)
    # adding the dates in the "future" to the df
    for date in pd.date_range(start=df.iloc[len(df) - 1]["Date"], end=prediction_date):
        df = df.append({'Date': date + timedelta(days=future_day)}, ignore_index=True)

    # appending predicted prices
    df.loc[df.index[-testing_days:], 'Predicted Price'] = predicted_prices
    price_tmr = df["Predicted Price"].iloc[-2]
    price_tmr = np.round(price_tmr, 4)

    price_tmr2 = df["Predicted Price"].iloc[-1]
    price_tmr2 = np.round(price_tmr2, 4)

    return price_tmr, price_tmr2

def get_predictions(coin = 'BTC-USD'):
    price_tmr, price_tmr2 = prediction(coin = coin)
    price_tmr = price_tmr.astype("str")
    price_tmr2 = price_tmr2.astype("str")
    pred_tomorrow = "The prediction for tomorrow is that " + coin + "'s price is " + price_tmr
    pred_tomorrow2 = "The prediction for the day after tomorrow is that " + coin + "'s price is " + price_tmr2
    return pred_tomorrow, pred_tomorrow2, price_tmr, price_tmr2

def gauge_plot(predicted_value, current_value, interval=0.05, coin = 'BTC-USD'):

    predicted_value = predicted_value.astype("float")
    current_value = current_value.astype("float")
    plot_bgcolor = "rgba(0,0,0,0)"
    quadrant_colors = [plot_bgcolor, "red", "#eff229", "green"]
    quadrant_text = ["", "<b>Sell</b>", "<b>Hold</b>", "<b>Buy</b>"]
    n_quadrants = len(quadrant_colors) - 1

    min_value = predicted_value * (1 - interval)
    max_value = predicted_value * (1 + interval)
    hand_length = np.sqrt(2) / 4
    hand_angle = np.pi * (1 - (max(min_value, min(max_value, current_value)) - min_value) / (max_value - min_value))

    fig = go.Figure(
        data=[
            go.Pie(
                values=[0.5] + (np.ones(n_quadrants) / 2 / n_quadrants).tolist(),
                rotation=90,
                hole=0.5,
                marker_colors=quadrant_colors,
                text=quadrant_text,
                textinfo="text",
                hoverinfo="skip",
            ),
        ],
        layout=go.Layout(
            showlegend=False,
            margin=dict(b=0, t=10, l=10, r=10),
            # width=450,
            # height=450,
            paper_bgcolor=plot_bgcolor,
            annotations=[
                go.layout.Annotation(
                    text=f"<b>{coin}</b>",
                    x=0.5, xanchor="center", xref="paper",
                    y=0.25, yanchor="bottom", yref="paper",
                    showarrow=False,
                )
            ],
            shapes=[
                go.layout.Shape(
                    type="circle",
                    x0=0.48, x1=0.52,
                    y0=0.48, y1=0.52,
                    fillcolor="#333",
                    line_color="#333",
                ),
                go.layout.Shape(
                    type="line",
                    x0=0.5, x1=0.5 + hand_length * np.cos(hand_angle),
                    y0=0.5, y1=0.5 + hand_length * np.sin(hand_angle),
                    line=dict(color="#333", width=4)
                )
            ]
        )
    )
    return fig


# ----------------------------------------------------------------------------------------------------------------------
# App layout
app.layout = dbc.Container([

    # 1st Row
    dbc.Row([
        dbc.Col(html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))),width=1),
        dbc.Col([html.H1("Crypto Currencies Dashboard",style={'letter-spacing': '1.5px','font-weight': 'bold','text-transform': 'uppercase'}),
                 html.H2("Business Case n. 5  -  Group I  -  Emanuele Aldera, Robin Schmidt, Rui Ramos, Muhammad Abdullah", style={'margin-bottom': '5px'})],
                width=9)
    ]),

    # Intermediate Row - Story telling
    dbc.Row(dbc.Col(html.H2("Discover the coins that performed better in a specified range of time by comparing their percentage changes over the course of the chosen range", 
    style={'margin-bottom': '5px', 'padding':'2px 15px 15px 15px'}))),
    # Intermediate Row - DropDown Menu
    dbc.Row(dbc.Col(html.Div(dropdown_leaderboard),width=4, style={'padding': '0px 15px 0px', "align" : "center"}),style={'padding':'2px 15px 15px 15px'}),

    # 2nd Row
    dbc.Row([
        dbc.Col(html.Div(
            dcc.Graph(id="leaderboard", style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white"})),
            width=6,
            style={'padding':'2px 15px 15px 15px'}),
        dbc.Col(html.Div(
            dcc.Graph(id="leaderboard_coins", style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white"})),
            width=6,
            style={'padding':'2px 15px 15px 15px'}),
    ],style={'padding':'2px 15px 15px 15px'}),

    # Intermediate Row - Story telling
    dbc.Row(dbc.Col(html.H2("Analyze a single coin by looking at the technical analysis built for you", style={'margin-bottom': '5px'})),style={'padding':'2px 15px 15px 15px'}),
    # Intermediate Row - DropDown Menu
    dbc.Row([dbc.Col(html.Div(dropdown_tech_analysis_coin),width=4, style={'padding': '0px 15px 0px', 'align' : "center"}),
        dbc.Col(html.Div(dropdown_tech_analysis_range),width=4, style={'padding': '0px 15px 0px', 'align' : "center"}),
        dbc.Col(html.Div(dropdown_tech_analysis_indicator),width=4, style={'padding': '0px 15px 0px', 'align' : "center"})],style={'padding':'2px 15px 15px 15px'}),

    # 2nd Row
    dbc.Row([
        dbc.Col(html.Div(
            dcc.Graph(id="technical_analysis", style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white"})),
            width=8,
            style={'padding':'2px 15px 15px 15px'}),
        dbc.Col([html.Div(
                html.Tr(id="table_info_coin", style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white", "font-size":"30px"}),style={'padding':'2px 15px 15px 15px'},
            ),
            html.Div(
                html.Tr(id="prediction_tomorrow", style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white", "font-size":"30px"}),style={'padding':'2px 15px 15px 15px'},
            ),
            html.Div(
                html.Tr(id="prediction_tomorrow2", style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white", "font-size":"30px"}),style={'padding':'2px 15px 15px 15px'},
            )],
            width=4,
            style={'padding':'2px 15px 15px 15px'}),
    ]),
    dbc.Row([
        dbc.Col(html.Div(
            dcc.Graph(id="technical_analysis_vol", style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white"})),
            width=8,
            style={'padding':'2px 15px 15px 15px'}), 
        dbc.Col(html.Div(
            dcc.Graph(id="buy_sell", style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white"})),
            width=4,
            style={'padding':'2px 15px 15px 15px'})
    ], style={'padding':'2px 15px 15px 15px'}),
],
#Container
fluid=True,
style={'background-color':'#dae9f5',
       'font-family': 'sans-serif',
       'color': '#606060',
       'font-size':'14px'
})

# ----------------------------------------------------------------------------------------------------------------------
# Callbacks

# 1st callback -> creates the leaderboard and leaderbord coins subplots
@app.callback(
    [Output(component_id='leaderboard', component_property='figure'),
     Output(component_id='leaderboard_coins', component_property='figure')],
    [Input('leaderboard_drop', 'value')])

def plot(range):
    data_lb, leaderboard = create_leaderboard(range)
    top1, coin1, top2, coin2, bot1, coin3, bot2, coin4 = get_top_bot(data_lb, leaderboard)
    plt_coins = make_subplots(rows = 2, cols = 2, subplot_titles=(coin1, coin2, coin3, coin4))
    plt_coins.add_trace(top1, row = 1, col = 1)
    plt_coins.add_trace(top2, row = 1, col = 2)
    plt_coins.add_trace(bot1, row = 2, col = 1)
    plt_coins.add_trace(bot2, row = 2, col = 2)
    plt_coins.update_layout(showlegend=False)
    plt_lb = plot_leaderboard(leaderboard)

    plt_coins.update_layout(
        title = "Top 2 and Worst 2 coins in the leaderboard",
        # xaxis_title = 'Date',
        xaxis = {"color" : "black"},
        # yaxis_title = f'Close Price',
        yaxis = {"color" : "black"},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    plt_coins.update_yaxes(tickprefix='$')
    
    return plt_lb, plt_coins

# 2nd callback -> builds technical analysis graph
@app.callback(
    [Output(component_id='technical_analysis', component_property='figure'),
    Output(component_id='technical_analysis_vol', component_property='figure'),
    Output(component_id='table_info_coin', component_property='children'),
    Output(component_id='prediction_tomorrow', component_property='children'),
    Output(component_id='prediction_tomorrow2', component_property='children'),
    Output(component_id='buy_sell', component_property='figure')],
    [Input('tech_analysis_coin_drop', 'value'),
    Input('tech_analysis_range_drop', 'value'),
    Input('tech_analysis_indicator_drop', 'value')])

def plot(coin, range, indicator):
    # first run of the dashboard
    if coin not in coins:
        coin = "BTC-USD"
    ta, ta_vol = plot_technical_analyis(coin, range, indicator)
    price_string, price_today = plot_info_coin(coin)
    pred1, pred2, price_tom, price_tom2= get_predictions(coin)
    buy_sell_plot = gauge_plot(price_tom2, price_today, 0.2, coin)
    return ta, ta_vol, price_string, pred1, pred2, buy_sell_plot

# ----------------------------------------------------------------------------------------------------------------------
# Running the app
if __name__ == '__main__':
    app.run_server(debug=False)
