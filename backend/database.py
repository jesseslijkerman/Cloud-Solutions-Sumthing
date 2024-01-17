import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from google.cloud.sql.connector import Connector, IPTypes
from google.oauth2 import service_account
# from google.cloud import secretmanager

import pymysql.cursors
import sqlalchemy

# Fetch the service account key from Secret Manager
secret_manager_client = secretmanager.SecretManagerServiceClient()
project_id = "project-id"
secret_name = "secret-name"

response = secret_manager_client.access_secret_version(name=f"projects/{project_id}/secrets/{secret_name}/versions/latest")
secret_credentials = response.payload.data.decode("UTF-8")

# Placeholder data
instance_connection_name = "project-id:region:instance"
db_user = "user"
db_pass = "password"
db_name = "database"

ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

connector = Connector(ip_type, credentials=secret_credentials)

def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

engine = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
