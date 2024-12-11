import psycopg2
import threading
from django.core.cache import cache
from config.config import DATABASE_NAME, DATABASE_USER, DATABASE_PASS, DATABASE_HOST, DATABASE_PORT