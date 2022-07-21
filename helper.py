import pandas as pd
import pyodbc
import const as cn

def get_connection():
    """Generates the connection string using the specified server and database name"""

    connection_string = f"Driver={{SQL Server}};Server={cn.SERVER};Database={cn.DATABASE};Trusted_Connection=yes;Timeout=600"
    conn = pyodbc.connect(connection_string)
    return conn


def get_recordset(conn: object, query: str) -> pd.DataFrame:
    """Returns a list of databases given a specified connection"""
    
    err_msg = ''
    ok = True
    result = pd.DataFrame()
    try:
        cursor = conn.cursor()
        result = pd.read_sql_query(query, conn)
    except Exception as ex:
        conn.rollback()
        ok=False
        err_msg = ex
    return result, ok, err_msg

def execute_cmd(conn: object, cmd: str) -> pd.DataFrame:
    """executes a data manipulation sql command"""
    
    err_msg = ''
    ok = True
    try:
        cursor = conn.cursor()
        cursor.execute(cmd)
        conn.commit()
    except Exception as ex:
        conn.rollback()
        ok=False
        err_msg = ex
    return ok, err_msg