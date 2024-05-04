import yfinance as yf
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import os

def download_stock_data(ticker_symbol, start_date, end_date):
    data = yf.download(ticker_symbol, start=start_date, end=end_date)
    data.to_csv(f'{ticker_symbol}_stock_data.csv')

if __name__ == "__main__":

