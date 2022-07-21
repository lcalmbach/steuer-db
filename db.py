import numpy as np
import pandas as pd
import const
import streamlit as st
import pyodbc 
import sqlalchemy
import urllib
import logging

import tools

logger = logging.getLogger(__name__)

def append_pd_table(df, table_name, fields):
    try:
        params = urllib.parse.quote_plus(get_conn_string(const.SERVER, const.DATABASE))   
        engine = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        if fields!=[]:
            df = df[fields]
        df.to_sql(table_name, engine, if_exists='replace')
        return 1
    except Exception as ex:
        print(ex)
        return 0


def get_conn_string(srv: str, db_name: str) -> str:
    return f"Driver={{SQL Server}};Server={srv};Database={db_name};Trusted_Connection=yes;Timeout=600"


def get_connection(srv:str, db_name:str):
    """Generates the connection string using the specified server and database name"""

    connection_string = get_conn_string(srv, db_name)
    return pyodbc.connect(connection_string)


def get_server_name(conn: object) -> str:
    """
    Gibt den Servername des Datenbankservers zurück
    """
    
    err_msg = ''
    ok = True
    qry = 'select @@servername as server_name'
    result, ok, err_msg = get_recordset(conn, qry)
    if ok:
        result = result['server_name'][0]
        logger.debug(f"Gibt Servername zurück: {result}")
    else:
        logger.error(f"Servername konnte nicht abgefragt werden: {qry}: {err_msg}")
        result = ''
    return result, ok, err_msg

def get_user_kuerzel(con: object)->str:
    """Gibt den User-Kürzel des Windows-Login zurück, z.b bs\ssscal"""

    qry = const.USER_LOGIN
    return get_recordset(conn, qry)['login'][0]


def get_user_info(conn: object, login: str) -> dict:
    """
    Gibt die wichtigsten User Attribute des current user zurück. Connection muss die Datenbank stata_produkte 
    enthalten
    """

    qry = const.USER_INFO.format(login)
    result = get_recordset(conn, qry).to_dict()

    return result


def get_sql_expr(value, is_string):
    """
    converts a value into a valid sql expression that can be used in an update statement
    None > Null
    Hans > 'Hans'
    50 > 50  
    """

    result = ''
    if value in (None, 'None'):
        result = 'Null'
    elif value in ('True','False'):
        result = 0 if value == 'False' else 1
    else:
        if is_string:
            value = value.replace("'", "''")
            result = f"'{value}'"
        else:
            result = value
    return result

def get_query_result_value(conn: object, query: str)->str:
    df = get_recordset(conn, query)
    return df.iloc[0]['result']

def get_recordset(conn: object, query: str) -> pd.DataFrame:
    """Returns a list of databases given a specified connection"""
    
    err_msg = ''
    ok = True
    result = pd.DataFrame()
    try:
        cursor = conn.cursor()
        result = pd.read_sql_query(query, conn)
        logger.debug(f'SQL query {query} wurde ausgeführt: {len(result)} rows')
    except Exception as ex:
        logger.error(f'SQL query {query} konnte nicht ausgeführt werden: {ex}')
        conn.rollback()
        ok=False
        err_msg = ex
    return result, ok, err_msg


def exec_non_query(conn: object, cmd: str) -> int:
    """
    Executes a command on the database
    """

    err_msg = ''
    ok = True
    try:
        cursor = conn.cursor()
        cursor.execute(cmd)
        conn.commit()
        logger.debug(f'SQL Query {cmd} wurde ausgeführt')
    except Exception as ex:
        logger.error(f'SQL Query {cmd} konnte nicht ausgeführt werden: {ex}')
        conn.rollback()
        ok=False
        err_msg = ex
    return ok, err_msg

def get_value(conn: object, query: str) -> str:
    """
    return a single value for a specified query
    """

    err_msg = ''
    ok = True
    result = pd.DataFrame()
    try:
        cursor = conn.cursor()
        result = pd.read_sql_query(query, conn)
    except Exception as ex:
        ok=False
        err_msg = ex

    if len(result) > 0:
        result = result['result'][0]
    else:
        result = None
    return result, ok, err_msg

def format_db_value(value: str, type: int):
    result = ''
    if type == 1:
        result = 'Null' if value in ('None','') else f"'{value}'"
    elif type == 2:
        result = 'Null' if value in ('None','') else value
    elif type == 3:
        result = 'Null' if value in ('None','') else value.replace(',','.')
    return result


def get_db_value(value: str, type: int):
    result = ''
    if type == 1:
        result = f"'{value}'"
    elif type == 2:
        result = 'Null' if value in ('None','') else value
    elif type == 3:
        result = 'Null' if value in ('None','') else value.replace(',','.')
    return result