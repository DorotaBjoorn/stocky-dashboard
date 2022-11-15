import pandas as pd
import os


class StockData:
    def __init__(self, data_folder_path: str) -> None:
        self._data_folder_path = data_folder_path

    def stock_dataframe(self, stockname: str) -> list:
        stock_df_list = []

        for path_ending in [
            "_TIME_SERIES_DAILY_ADJUSTED.csv",
            "_TIME_SERIES_INTRADAY_EXTENDED.csv",
        ]:
            # example:
            # data_folder_path: C:\Users\DorotaBjöörn-AI22GBG\Documents\GitHub\Databehandling-Dorota-Bjoorn\Code-alongs\stockdata
            # stockname: AAPL,
            # path_ending: _TIME_SERIES_DAILY_ADJUSTED.csv,
            # resulting path: C:\Users\DorotaBjöörn-AI22GBG\Documents\GitHub\Databehandling-Dorota-Bjoorn\
            #                   Code-alongs\stockdata\AAPL_TIME_SERIES_DAYILY_ADJUSTED.csv
            path = os.path.join(self._data_folder_path, stockname+path_ending)

            stock = pd.read_csv(path, index_col=0, parse_dates=True) #datumen blir index, pd.datetime för inläsning av datum
            stock.index.rename("Date", inplace=True)

            stock_df_list.append(stock)

        return stock_df_list #containging 2 st DFs
