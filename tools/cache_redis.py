import json
import redis

def connect(host='192.168.40.133', port=6379, db=0):
    return redis.Redis(host=host, port=port, db=db)

def save_data(clave, datos, ttl=604800):
    redis_conn = connect()
    valor = json.dumps(datos)
    # redis_conn.set(clave, valor)
    redis_conn.setex(clave, ttl, valor)

def get_data(clave):
    redis_conn = connect()
    valor = redis_conn.get(clave)
    if valor:
        return json.loads(valor)
    return None
