import pandas as pd
import mysql.connector

# MySQL database connection parameters
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'ADT'
}

###
# CREATE TABLE malnutrition (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     ISO VARCHAR(3),
#     `Country Name` VARCHAR(255),
#     Year INT,
#     Sex VARCHAR(10),
#     Overweight FLOAT,
#     Wasting FLOAT,
#     Stunting FLOAT,
#     Mean FLOAT
# );
###
# Function to connect to the MySQL database
def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        print("Connected to MySQL database")
        return connection
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL database:", error)
        return None

# Function to insert data into the malnutrition table
def insert_data(connection, data):
    try:
        cursor = connection.cursor()
        # SQL query to insert data into the table
        insert_query = """
            INSERT INTO malnutrition (ISO,`Country Name`,Year,Sex,Overweight,Wasting,Stunting,Mean)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Execute the insert query for each row of data
        for row in data.itertuples(index=False):
            cursor.execute(insert_query, row)
        connection.commit()
        print("Data inserted successfully")
    except mysql.connector.Error as error:
        print("Failed to insert data into MySQL table:", error)

# Read data from CSV file
csv_file = 'malnutrition.csv'  # Update with your CSV file path
data = pd.read_csv(csv_file)

# Connect to the MySQL database
connection = connect_to_database()
if connection:
    # Insert data into the malnutrition_data table
    insert_data(connection, data)
    # Close the database connection
    connection.close()
