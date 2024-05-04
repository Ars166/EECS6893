from datetime import datetime, timedelta
from textwrap import dedent
import time

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
count = 0

def sleeping_function_2():
    """This is a function that will run within the DAG execution"""
    print("Sleeping for 2 seconds...")
    time.sleep(2)

def sleep_function():
    """Simulates task execution time."""
    print("Sleeping for 5 seconds...")
    time.sleep(5)
    print("Task completed!")


def count_function():
    global count
    count += 1
    print('count_increase output: {}'.format(count))
    time.sleep(2)

def print_function():
    global count
    count += 1
    print('printing...')
    time.sleep(2)

def wrong_sleeping_function():
    # this task is t2_1, t1 >> t2_1
    global count
    print('wrong sleeping function output: {}'.format(count))
    assert count == 1
    time.sleep(2)

def finish():
    print('finish')


echo_command = "echo 'This is an echo command.'"
system_command = 'ls ~/airflow/dags'

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
        'workflow',
        default_args=default_args,
        description='A simple toy DAG',
        schedule_interval=timedelta(minutes=30),
        start_date=datetime.now() - timedelta(minutes=30),
        catchup=False,
        tags=['example'],
) as dag:
##########################################
# DEFINE AIRFLOW OPERATORS
##########################################

# t* examples of tasks created by instantiating operators

    t1 = BashOperator(
        task_id='t1',
        bash_command = echo_command,
        dag=dag
    )

    t2 = BashOperator(
        task_id ='t2',
        bash_command=echo_command,
        dag=dag
    )

    t3 = BashOperator(
        task_id='t3',
        bash_command='python ~/airflow/dags/hello.py',
        dag=dag
    )

    t4 = PythonOperator(
        task_id='t4',
        python_callable=sleeping_function_2,
        dag=dag
    )

    t5 = BashOperator(
        task_id='t5',
        bash_command='python ~/airflow/dags/hello.py',
        dag=dag
    )

    t6 = BashOperator(
        task_id='t6',
        bash_command='echo 1',
        dag=dag
    )

    t7 = PythonOperator(
        task_id='t7',
        python_callable=count_function,
        dag=dag
    )

    t8 = PythonOperator(
        task_id='t8',
        python_callable=sleep_function,
        dag=dag
    )

    t9 = BashOperator(
        task_id='t9',
        bash_command='sleep 2',
        retries=3,
        dag=dag
    )

    t10 = BashOperator(
        task_id='t10',
        bash_command='sleep 2',
        retries=3,
        dag=dag
    )

    t11 = PythonOperator(
        task_id='t11',
        python_callable=count_function,
        dag=dag
    )

    t12 = PythonOperator(
        task_id='t12',
        python_callable=print_function,
        dag=dag
    )

    t13 = BashOperator(
        task_id='t13',
        bash_command='echo 2',
        retries=3,
        dag=dag
    )

    t14 = BashOperator(
        task_id='t14',
        bash_command="echo 'echo printing...'",
        retries=3,
        dag=dag
    )

    t15 = PythonOperator(
        task_id='t15',
        python_callable=sleep_function,
        dag=dag
    )

    t16 = PythonOperator(
        task_id='t16',
        python_callable=sleep_function,
        dag=dag
    )

    t17 = BashOperator(
        task_id='t17',
        bash_command="echo 'this is t17'",
        retries=3,
        dag=dag
    )

    t18 = BashOperator(
        task_id='t18',
        bash_command="sleep 5",
        retries=3,
        dag=dag
    )

    t19 = PythonOperator(
        task_id='t19',
        python_callable=finish,
        dag=dag
    )




##########################################
# DEFINE TASKS HIERARCHY
##########################################

    # task dependencies

    t1 >> [t2, t3, t4, t5]
    t2 >> t6
    t3 >> [t7, t12]
    t5 >> [t8, t9]
    t7 >> [t14, t13, t18]
    t8 >> [t10, t15]
    t9 >> [t11, t12]
    [t10, t11, t12] >> t14
    t14 >> [t16, t17]
    [t13, t14, t15, t17] >> t18
    [t16, t18] >> t19


