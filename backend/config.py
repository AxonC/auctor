import os
import logging

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_POST", 5432)
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "docker")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "auctor")

SECRET_KEY_AUTH=os.getenv("SECRET_KEY_AUTH", "secret-key")

logging.basicConfig(level=logging.DEBUG)