
""" 
    SQL Server handlers for creating and updaing DB Tables
"""

from sqlalchemy import text, inspect, select
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, UnicodeText

import pandas as pd
import ast

from create_sql_db_engine import create_my_engine
from my_logger import print_info, print_error
import csv_utils

db_engine = create_my_engine()
metadata = MetaData()
print("db engine started")

def get_attractions_table_name(country):
    return f"{country.lower()}_attractions"


def create_attractions_table(country:str):
    # Define table schema
    table_name = get_attractions_table_name(country)
    # attractions_columns = ['Name', 'Type', 'NearestCity', 'Latitude', 'Longitude', 'GoogleId']
   
    # Check if the table exists in the database
   
    # Use SQLAlchemy's inspector to check if a table exists
    inspector = inspect(db_engine)
    tables = inspector.get_table_names()

    if table_name not in tables:
        my_table = Table(
            table_name, metadata,
            Column('id', Integer, primary_key=True),
            Column('Name', UnicodeText(255)),  # Correct type
            # Column('YOB', Integer),
            Column('Type', String(100)),        
            Column('NearestCity', UnicodeText(100)),
            Column('Latitude', Float),
            Column('Longitude', Float),
            Column('GoogleId', String(100))
        )
        
        # Create the table
        metadata.create_all(db_engine)
    
##################################################################################################
# Define the SQL for checking if the record exists
def check_exists_sql(table_name):
    return f"SELECT 1 FROM {table_name} WHERE Name = "

def insert_attractions_prefix(country):
    table_name = get_attractions_table_name(country)
    return f"INSERT INTO {table_name} (Name, Type, NearestCity, Latitude, Longitude, GoogleId) VALUES "

#### --------------------------------------------------------------------------------
def insert_attraction(row, country):
    
    if(len(row)) < 6:
        print_error("cant add roo. too short!")
        return None
    
    table_name = get_attractions_table_name(country)
    table_obj = Table(table_name, metadata, autoload_with=db_engine)

    with db_engine.connect() as connection:
        # connection.execute(create_table_text)
        tuple_value = tuple(row)
        row_name = tuple_value[0]
        
        check_query = table_obj.select().where(table_obj.c.Name == row_name)
        result = connection.execute(check_query).fetchone()
    
        # query = check_exists_sql(table_name) + f"'{row_name}'"
        # result = connection.execute(text(query)).fetchone()
        
        if result:
            print_info(f"attraction {row_name} already exists in db table {table_name}")
            return None
        else:
            result = connection.execute(table_obj.insert().values(
                Name=row[0], Type=row[1], NearestCity=row[2], Latitude=row[3], Longitude=row[4], GoogleId=row[5]))

            # query = insert_attractions_prefix(country) + f"{tuple_value}"
            # result = connection.execute(text(query))
            connection.commit() 

        return result
    
#### -------------------------------------------------------------------------------

    # print(connection.execute(text('SELECT * from players')).fetchall())
        
    
def test():
    country = 'poland'
    create_attractions_table(country)
    
    row = ['Krupówki Street', 'Urban/Shopping', 'zakopane', 49.29385449999999, 19.9538936, 'ChIJOdwFMZHyFUcRceAH7r6DNWM']
    result = insert_attraction(row, country)
    result = insert_attraction(row, country)  # try to add again
    
# test()

