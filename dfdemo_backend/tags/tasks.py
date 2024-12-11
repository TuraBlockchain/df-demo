import psycopg2
import threading
from django.core.cache import cache
from config.config import DATABASE_NAME, DATABASE_USER, DATABASE_PASS, DATABASE_HOST, DATABASE_PORT

def listen_to_tags_cardkv_changes():
    from .models import CardKV
    connection = psycopg2.connect(
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASS,
        host=DATABASE_HOST,
        port=DATABASE_PORT
    )
    connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute("LISTEN tags_cardkv_change;")

    print("Waiting for notifications on channel 'tags_cardkv_change'")

    while True:
        connection.poll()
        while connection.notifies:
            notify = connection.notifies.pop(0)
            print(f"Got NOTIFY: {notify.payload}")
            # 更新缓存
            update_cache()

def update_cache():
    from .models import CardKV
    kv_data = CardKV.objects.all()
    keys_list = []
    for kv in kv_data:
        cache.set(kv.key, kv.data)
        keys_list.append(kv.key)
    cache.set(CACHE_KEYS_LIST, keys_list)  # 更新所有键的列表
    print("Cache updated with keys:", keys_list)

def start_listening():
    # 初始缓存加载
    update_cache()
    # 启动监听线程
    listener_thread = threading.Thread(target=listen_to_tags_cardkv_changes, daemon=True)
    listener_thread.start()