import os
import psycopg2

clean_data_path = os.path.join(os.getcwd(), "data", "kaggle_dataset_clean")

for file in os.listdir(clean_data_path):
    with psycopg2.connect(user="admin", password="password", host="127.0.0.1", port="5432", database="sensor-db") as conn:
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SET DateStyle = 'ISO, DMY';")

        # Create the table
        table_name = file.split(".")[0]
        drop_query = f"DROP TABLE IF EXISTS {table_name} CASCADE;"
        create_table = f'''
        CREATE TABLE {table_name} (
            created_at TIMESTAMPTZ,
            entry_id SERIAL PRIMARY KEY,
            temperature FLOAT,
            turbidity FLOAT,
            dissolved_oxygen FLOAT,
            ph FLOAT,
            ammonia FLOAT,
            nitrate FLOAT,
            population INT,
            fish_length FLOAT,
            fish_weight FLOAT
        ); 
        '''
        cursor.execute(drop_query)
        cursor.execute(create_table)
        print(f"Successfully created table: {table_name}")

        sql = f"COPY {table_name} FROM STDIN WITH (FORMAT csv, HEADER true)"
        with open(os.path.join(clean_data_path, file), 'r') as f:
            cursor.copy_expert(sql, f)

        print(f"Successfully added {file} data to postgres db")

with psycopg2.connect(user="admin", password="password", host="127.0.0.1", port="5432", database="sensor-db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast');")
    print(cursor.fetchall())