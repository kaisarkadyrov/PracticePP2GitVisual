import psycopg2

def connect(config):
    return psycopg2.connect(
        host=config['host'],
        database=config['database'],
        user=config['user'],
        password=config['password'],
        port=config.get('port', 5432)
    )