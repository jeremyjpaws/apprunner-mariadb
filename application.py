from os import environ as env
import mariadb
import json
from flask import Flask
import logging
import time
from datetime import datetime

app = Flask(__name__)

if __name__ != '__main__':
  gunicorn_logger = logging.getLogger('gunicorn.error')
  app.logger.handlers = gunicorn_logger.handlers
  app.logger.setLevel(gunicorn_logger.level)

# mariadb configs
db_host = env.get('DBHOSTNAME')
db_port_str = env.get('DBPORT')
db_port = int(db_port_str)
db_user = env.get('DBUSERNAME')
db_pswd = env.get('DBUSERPSWD')
db_name = env.get('DBNAME') # name ='test'

def app_init():
  db_entries = {}

  #confirm tables present in databases on init
  try:
    start_time = datetime.now()
    db = mariadb.connect(
      host=db_host,
      port=db_port,
      user=db_user,
      password=db_pswd,
      database=db_name
    )
  except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")
  else:
    app.logger.debug(f"database connection established to: {db_host}")
    cursor = db.cursor()
    cursor.execute("Show tables;")
    db_tables = list(cursor.fetchall())
    app.logger.debug(f"tables present in {db_host}: {db_tables}")
    cursor.close()
    db.close()
    end_time = datetime.now()
    
    conn_time = end_time - start_time
    app.logger.debug(f"connection to mariadb took: {conn_time}")
    db_entries['mariadb_tables'] = db_tables


  return db_entries


#init
app_start = app_init()
newline = "\n"
app.logger.debug(f"Finished start. Successfully connected to your mariadb. Tables are: {app_start['mariadb_tables']}")


@app.route("/")
def index():  
  return "Hello World! 4"

@app.route("/hello")
def hello():
  newline = '\n'
  return f"Hello back! Successfully connected to your mariadb on start. Tables are: {app_start['mariadb_tables']}"
  


@app.route("/dbmaria")
def dbmaria():
  app.logger.debug(f"database endpoint: {db_host}")
  try:
    db = mariadb.connect(
      host=db_host,
      port=db_port,
      user=db_user,
      password=db_pswd,
      database=db_name
    )
  except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")
  else:
    app.logger.debug(f"database connection established to: {db_host}")
    cursor = db.cursor()

  # execute a SQL statement
  cursor.execute("Show tables;")    
  db_tables = list(cursor.fetchall())

  cursor.execute("select * from people")

  # serialize results into JSON
  row_headers=[x[0] for x in cursor.description]
  rv = cursor.fetchall()
  json_data=[]
  for result in rv:
    json_data.append(dict(zip(row_headers,result)))

  if json_data:
    cursor.close()
    db.close()
    
  return f"Successfully connected to database endpoint: {db_host}. tables: {db_tables}. data: {json.dumps(json_data)}"

@app.route("/health")
def health():
  healthcheck = app_init()

  selected_date = datetime.now()
  data = ""
  status_code = 500
  if healthcheck["mariadb_tables"]:
    data = f"{selected_date} - health check result - mariadb: {healthcheck['mariadb_tables']}"
    status_code = 200

    return data, status_code
  else :
    return "Error", status_code


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=80, debug=False)
