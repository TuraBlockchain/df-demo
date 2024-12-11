import psycopg2
import threading
from django.core.cache import cache
from config.config import DATABASE_NAME, DATABASE_USER, DATABASE_PASS, DATABASE_HOST, DATABASE_PORT

def start_listening():
    # 初始缓存加载
    update_cache()
    # 启动监听线程
    listener_thread = threading.Thread(target=listen_to_tags_cardkv_changes, daemon=True)
    listener_thread.start()