import pandas as pd
import mysql.connector

# MySQL database connection parameters
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'ADT'
}

# Function to connect to the MySQL database
def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        print("Connected to MySQL database")
        return connection
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL database:", error)
        return None

# Function to insert data into the population_data table in batches
def insert_data(connection, data, batch_size=345655):
    try:
        cursor = connection.cursor()
        total_rows = len(data)
        rows_inserted = 0
        
        # SQL query to insert data into the table
        insert_query = """
            INSERT INTO population_data (Gender,Year,Mean,Country,ISO,Continent,GDD_Variable_Label)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        # Execute the insert query in batches
        for batch_start in range(0, total_rows, batch_size):
            batch_data = data.iloc[batch_start:batch_start+batch_size]
            values = [tuple(row) for row in batch_data.itertuples(index=False)]
            cursor.executemany(insert_query, values)
            rows_inserted += cursor.rowcount
            
            # Calculate and print progress percentage
            progress = min((batch_start + batch_size) / total_rows * 100, 100)
            print(f"Progress: {progress:.2f}%")
        
        connection.commit()
        print(f"{rows_inserted} rows inserted successfully")
    except mysql.connector.Error as error:
        print("Failed to insert data into MySQL table:", error)


# Read data from CSV file
csv_file = 'gdd.csv'  # Update with your CSV file path
data = pd.read_csv(csv_file)

# Connect to the MySQL database
connection = connect_to_database()
if connection:
    # Insert data into the population_data table
    insert_data(connection, data)
    # Close the database connection
    connection.close()
