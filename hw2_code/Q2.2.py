from airflow import DAG
from datetime import datetime, timedelta
from textwrap import dedent
import time
import os
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
import yfinance as yf
import pandas as pd
from sklearn import preprocessing
import numpy as np
import math
from sklearn.linear_model import LinearRegression


def download_stock_data(ticker_symbol, start_date, end_date):
    data = yf.download(ticker_symbol, start=start_date, end=end_date)
    data.to_csv(f'{ticker_symbol}_stock_data.csv')


def read_data(ticker_symbol):
    relative_error=[]
    path=f'{ticker_symbol}_stock_data.csv'
    data = pd.read_csv(path)
    data.set_index('Date', inplace=True)
    X = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    data['next_High'] = data['High'].shift(1)
    data.fillna(-99999, inplace=True)
    y = data['next_High']
    current_date = '2023-10-09'
    date = ['2023-10-10', '2023-10-11', '2023-10-12', '2023-10-13', '2023-10-16']
    # train data
    X_train = X[:current_date]
    y_train = y[:current_date]

    # train model
    model = LinearRegression()
    model.fit(X_train, y_train)

    for i in range(5):
        # predict next_high
        slice=X.loc[date[i]]
        X_test = pd.DataFrame(slice).T
        y_true = y[date[i]]
        y_pred = model.predict(X_test)

        error = (y_pred - y_true) / y_true
        print(error)
        num_array = np.array(error)
        err = float(num_array[0])
        relative_error.append(err)

    error_df = pd.DataFrame(date, columns=['Date'])
    error_df[ticker_symbol] = relative_error
    error_df['Date'] = date
    print(error_df)

    csv_file = f'{ticker_symbol}_predict_data.csv'

    error_df.to_csv(csv_file, index=False)
    print(f"DataFrame written to {csv_file}")

def combine():
    # read and set index
    df1 = pd.read_csv('AAPL_predict_data.csv')
    df1.set_index('Date', inplace=True)

    df2 = pd.read_csv('GOOGL_predict_data.csv')
    df2.set_index('Date', inplace=True)

    df3 = pd.read_csv('META_predict_data.csv')
    df3.set_index('Date', inplace=True)
    df4 = pd.read_csv('MSFT_predict_data.csv')
    df4.set_index('Date', inplace=True)
    df5 = pd.read_csv('AMZN_predict_data.csv')
    df5.set_index('Date', inplace=True)

    # join according to index
    result = df1.join(df2)
    result = result.join(df3)
    result = result.join(df4)
    result = result.join(df5)
    csv_file = 'relative_errors .csv'

    result.to_csv(csv_file)
    print(f"DataFrame written to {csv_file}")



############################################
# DEFINE AIRFLOW DAG (SETTINGS + SCHEDULE)
############################################

default_args = {
    'owner': 'shiyan',
    'depends_on_past': False,
    'email': ['sw3828@columbia.edu'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

with DAG(
        'Q2.2',
        default_args=default_args,
        description='A simple toy DAG',
        start_date= datetime(2023, 10, 15),
        schedule_interval=None,
        catchup=False,
        tags=['example'],
) as dag:

    download_AAPL = PythonOperator(
        task_id='download_AAPL',
        python_callable=download_stock_data,
        op_args=['AAPL', '2023-01-01', '2023-10-17'],
        dag=dag
    )

    download_GOOGL = PythonOperator(
        task_id='download_GOOGL',
        python_callable=download_stock_data,
        op_args=['GOOGL', '2023-01-01', '2023-10-17'],
        dag=dag
    )

    download_META = PythonOperator(
        task_id='download_META',
        python_callable=download_stock_data,
        op_args=['META', '2023-01-01', '2023-10-17'],
        dag=dag
    )

    download_MSFT = PythonOperator(
        task_id='download_MSFT',
        python_callable=download_stock_data,
        op_args=['MSFT', '2023-01-01', '2023-10-17'],
        dag=dag
    )

    download_AMZN = PythonOperator(
        task_id='download_AMZN',
        python_callable=download_stock_data,
        op_args=['AMZN', '2023-01-01', '2023-10-17'],
        dag=dag
    )

    calcu_AAPL = PythonOperator(
        task_id='calcu_AAPL',
        python_callable=read_data,
        op_args=['AAPL'],
        dag=dag
    )

    calcu_GOOGL = PythonOperator(
        task_id='calcu_GOOGL',
        python_callable=read_data,
        op_args=['GOOGL'],
        dag=dag
    )

    calcu_META = PythonOperator(
        task_id='calcu_META',
        python_callable=read_data,
        op_args=['META'],
        dag=dag
    )

    calcu_MSFT = PythonOperator(
        task_id='calcu_MSFT',
        python_callable=read_data,
        op_args=['MSFT'],
        dag=dag
    )


    calcu_AMZN = PythonOperator(
        task_id='calcu_AMZN',
        python_callable=read_data,
        op_args=['AMZN'],
        dag=dag
    )

    sum = PythonOperator(
        task_id='sum',
        python_callable=combine,
        dag=dag
    )

##########################################
# DEFINE TASKS HIERARCHY
##########################################

    # task dependencies

    download_AAPL >> calcu_AAPL
    download_GOOGL >> calcu_GOOGL
    download_META >> calcu_META
    download_MSFT >> calcu_MSFT
    download_AMZN >> calcu_AMZN
    [calcu_AAPL, calcu_AMZN, calcu_MSFT,calcu_META,calcu_GOOGL]>>sum

