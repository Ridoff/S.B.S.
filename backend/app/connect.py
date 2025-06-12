import psycopg2
from cryptography.fernet import Fernet
from dotenv import dotenv_values
from io import StringIO

def load_key():
    """Загрузка ключа шифрования"""
    key_path = r"/Users/riddofftsss/SBSDB/keys/secret.key"
    try:
        with open(key_path, 'rb') as f:
            key = f.read().strip()
            if len(key) != 44:
                raise ValueError("Неверная длина ключа шифрования")
            return key
    except Exception as e:
        raise RuntimeError(f"Ошибка загрузки ключа: {e}")

def decrypt_db_config():
    """Расшифровка конфигурации БД"""
    try:
        key = load_key()
        fernet = Fernet(key)

        encrypted_path = r"/Users/riddofftsss/SBSDB/keys/dataBD.enc"
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = fernet.decrypt(encrypted_data).decode('utf-8')
        return dotenv_values(stream=StringIO(decrypted_data))

    except Exception as e:
        raise RuntimeError(f"Ошибка расшифровки конфига БД: {e}")

def create_connection():
    """Создание подключения к PostgreSQL с правильной кодировкой"""
    config = decrypt_db_config()
    try:
        conn = psycopg2.connect(
            host=config['DB_HOST'],
            database=config['DB_NAME'],
            user=config['DB_USER'],
            password=config['DB_PASSWORD'],
            port=config['DB_PORT'],
            connect_timeout=5,
        )
        conn.set_client_encoding('UTF8')

        cur = conn.cursor()
        cur.execute("SHOW client_encoding;")
        client_enc = cur.fetchone()

        return conn
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return None
