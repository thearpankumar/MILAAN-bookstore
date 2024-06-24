from sqlalchemy import create_engine

def connect_to_database(host, port, user, password, database):
  """
  Attempts to connect to a MySQL database using SQLAlchemy.

  Args:
      host (str): The hostname or IP address of the MySQL server.
      port (int): The port number of the MySQL server.
      user (str): The username for connecting to the database.
      password (str): The password for the user.
      database (str): The name of the database to connect to.

  Returns:
      engine: A SQLAlchemy engine object if successful, None otherwise.
  """
  try:
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")
    engine.connect()
    print("Connection successful!")
    return engine
  except Exception as err:
    print("Connection failed:", err)
    return None

# Replace these values with your actual details
host = "localhost"
port = 3306
user = "root"
password = "book123"  # Replace with your actual password
database = "book_main"

engine = connect_to_database(host, port, user, password, database)

# Close the engine connection (implicit when garbage collected)
if engine:
  print("Connection closed.")
