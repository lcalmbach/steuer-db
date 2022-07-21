import pyodbc

def get_connection(srv:str, db_name:str):
    """Generates the connection string using the specified server and database name"""

    connection_string = f"Driver={{SQL Server}};Server={srv};Database={db_name};Trusted_Connection=yes;Timeout=600"
    return pyodbc.connect(connection_string)


cursor = conn.cursor()
cursor.execute("SELECT * from items") 
row = cursor.fetchone() 
while row: 
    print(row[0])
    row = cursor.fetchone()
