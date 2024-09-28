""" 
    Creating MS SQL Server Database engine 
    but can be overwritten by other sql server by simply replacing server and connection string
"""

from sqlalchemy import create_engine, text

# from sqlalchemy import text
import pyodbc
from sqlalchemy.exc import SQLAlchemyError
import os

DOCKER_MODE = os.getenv('DOCKER_MODE')

database = 'Naya'

if DOCKER_MODE:
    server = 'host.docker.internal\MSSQLSERVER01'
    # for SQLite
    connection_string = "sqlite+pysqlite:///:memory:"
else:    
    server = 'localhost\MSSQLSERVER01'
    # for MS SQL Server
    connection_string = 'mssql+pyodbc://' + server + '/' + database + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server'


def create_my_engine():
    # print(pyodbc.drivers())
    print(connection_string + "\n\n")
    
    engine = create_engine(connection_string , echo=False)
    # engine = create_engine(connection_string , echo=False, connect_args={"charset": "utf8"})

    # if DOCKER_MODE:
    #     try:
    #         with engine.connect() as connection:
    #             result = connection.execute(text("SELECT 1"))
    #             for row in result:
    #                 print(row)
    #     except SQLAlchemyError as e:
    #         print(f"Error occurred: {str(e)}")
        
    return engine




