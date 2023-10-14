import psycopg2
from psycopg2 import sql
from loguru import logger
from datetime import datetime
from src.utils import load_yaml_file
import pandas as pd
from extract import extract

def store_data_in_postgresql(data_list, db_params):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=db_params['host'],
            database=db_params['dbname'],
            user=db_params['user'],
            password=db_params['password']
        )
        cursor = connection.cursor()

        # Create the table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS transcripts (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR,
            title VARCHAR,
            date DATE,
            time VARCHAR,
            crawled_date DATE,
            link VARCHAR,
            content TEXT
        )
        """
        cursor.execute(create_table_query)
        connection.commit()

        # Insert data into the table
        insert_query = """
        INSERT INTO transcripts (ticker, title, date, time, crawled_date, link, content)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        for data in data_list:
            values = (
                data['ticker'],
                data['title'],
                data['date'],
                data['time'],
                data['crawled_date'],
                data['link'],
                data['content']
            )
            cursor.execute(insert_query, values)
            connection.commit()

        logger.info("Data stored successfully in PostgreSQL database.")

    except (Exception, psycopg2.Error) as error:
        logger.error("Error while connecting to PostgreSQL:", error)

    # finally:
    #     if connection:
    #         cursor.close()
    #         connection.close()

def main():
    db_params = load_yaml_file('src/config/db_config.yaml')
    data_list = extract()
    store_data_in_postgresql(db_params=db_params, data_list=data_list)