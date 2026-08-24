import os
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), '..','.env')
load_dotenv(dotenv_path=env_path)


class Config:
  def __init__(self):
    self.db_host = os.getenv('host')
    self.db_port = os.getenv('port')
    self.db_user = os.getenv('pg_user')
    self.db_password = os.getenv('pg_password')
    self.db_name = os.getenv('pg_database')

  def get_database_connection_string(self):
     return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"