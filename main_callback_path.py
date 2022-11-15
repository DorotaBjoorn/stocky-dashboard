import dash
import dash_bootstrap_components as dbc
import os
from load_data import StockData
from dash import html, dcc 
from dash.dependencies import Output, Input  
import plotly_express as px
from time_filtering import filter_time
import pandas as pd

#när jobbar med py filer så ha med absolute path för att .py play knappen utgår alltid från huvudmappen (dvs Databeh-Dor...).
# it will check where you are in terminal which is always DATABEHANDLING-DOROTA_BJOORN for this course
directory_path = os.path.dirname(__file__) # ger vilken mapp filen befinner sig i
path = os.path.join(directory_path, "stocksdata")

print(path)

# instantiate object from class StockData that we have imported by from load_data import StockData
# load_data.py fiunns i samma mapp
# sys.path.append(os.path.join(directory_path, "graphs")) om load_data.py låg i mappen graphs
stockdata_object = StockData(path)

# print 1 stock
# print(stockdata_object.stock_dataframe("AAPL"))

symbol_dict = {"AAPL": "Apple", "NVDA": "Nvidia", "TSLA": "Tesla", "IBM": "IBM"}

df_dict = {
    symbol: stockdata_object.stock_dataframe(symbol) for symbol in symbol_dict
}  # dict av dataframes, loopning genom dict tar automatiskt keys så symbol är key. dict.itomes skulle ge keys och values
    # 2 olika DF per nyckel så totalt 8 DFs: {"AAPL": [df_daily, df_intraday], "NVDA": [df_daily, df_intraday], ...}


# dropdown requres a list of dicts once layout is to be done
stock_options_dropdown = [{"label": name, "value": symbol} for symbol, name in symbol_dict.items()]
  # får lista av 4 dicts, name kommer synas, value kommer användas för att kunna filtreras

# this interactive (what?) requires list of dicts
ohlc_options = [
    {"label": option, "value": option} for option in ("open", "high", "low", "close")
]

# time slide requres a list of dicts
slider_marks = {
    i: mark
    for i, mark in enumerate(
        ["1 day", "1 week", "1 month", "3 months", "1 year", "5 year", "Max"]
    )
}

print(df_dict.keys())
# print(df_dict["TSLA"]) - får en lista av dictionaries

# create a Dash App måste finnas för att kunna börja kunna bygga på appen (även sista raderna i koden med if name...)
app = dash.Dash(__name__)

# building layout for the homepage
app.layout = html.Main(                         #children ex H1, P, Dropdown etc samlas i en lista nedan
    [
        html.H1("Techy stocks viewer"),         #kräver list om fler element
        html.P("Choose a stock"),
        dcc.Dropdown(
            id="stockpicker-dropdown",
            options=stock_options_dropdown,
            value="AAPL",
        ),
        html.P(id="highest-value"),
        html.P(id="lowest-value"),
        dcc.RadioItems(
            id="ohlc-radio", options=ohlc_options, value="close"
        ),  # open high low close
        dcc.Graph(id="stock-graph"),
        dcc.Slider(
            id="time-slider", min=0, max=6, marks=slider_marks, value=2, step=None
        ),
        # storing intermediate value on clinets browser in ordre to share between several callbacks
        dcc.Store(id="filtered-df"), #[E] changes which triggers [F] and [K]
    ]
)

#when the dorpdown value vhanges or the time lisder value changes iit will trhigger filter-df to run
# radioknapparna skulle också kunnat vara med som Input
@app.callback(
    Output("filtered-df", "data"),              # [D] New Output from [C], change in "filtered-df" thus change in [E]
    Input("stockpicker-dropdown", "value"),     # [A] "stockpicker-dropdown" changes when choose new value in droplist
    Input("time-slider", "value"),
)

# denna funktionen körs när values in Input under app.callback change
def filter_df(stock, time_index):               # [B] funktion körs triggat av [A]
    dff_daily, dff_intraday = df_dict[stock]
    dff = dff_intraday if time_index <= 2 else dff_daily
    days = {i: day for i, day in enumerate([1, 7, 30, 90, 365, 365 * 5])}
    dff = dff if time_index == 6 else filter_time(dff, days=days[time_index])
    return dff.to_json()                        # [C] returned is json object which goes to Output [D]
    # json objektet returnerras til dcc.Store(id="filtered-df") som då ändras och triggar de funktioner som har
    #filtered-df som Input i @app.callback som triggar underliggande funktion
    # ock det som returneras från funktionen går in i outputs i motsvarande @app.callback decoratorn


@app.callback(
    Output("highest-value", "children"),         # [I] output from function updates Output
    Output("lowest-value", "children"),          # [J] output from function updates Output     
    Input("filtered-df", "data"),                # [F] "filtered-df" changes triggering def higherst_lowest_value...
    Input("ohlc-radio", "value"),
)
def highest_lowest_value_update(json_df, ohlc): # [G] körs (Input ovan ändras och outputen går in som Output)
    dff = pd.read_json(json_df)                    
    highest_value = dff[ohlc].max()
    lowest_value = dff[ohlc].min()
    return highest_value, lowest_value          # [H] output from function goes to [I] and [J]
    #return f"MAX: {highest_value}, lowest_value" om vill skiva ut MAX: värde på hemsidan


@app.callback(
    Output("stock-graph", "figure"),            # [N] output från funktionen updaterar Output, dvs figuren
    Input("filtered-df", "data"),               # [K]  "filtered-df" changes triggering def upgrade graph()
    Input("stockpicker-dropdown", "value"),
    Input("ohlc-radio", "value"),
)
def update_graph(json_df, stock, ohlc):         #[L] funktioinen körs
    dff = pd.read_json(json_df)
    return px.line(dff, x=dff.index, y=ohlc, title=symbol_dict[stock])  #[M] output går till [N]


# dessa rader behövs för att kunna köra Dash Appen
if __name__ == "__main__":
    app.run_server(debug=True)
