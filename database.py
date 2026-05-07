import os
import psycopg

def get_connection():
    return psycopg.connect(os.environ.get("DATABASE_URL"))

def criar_tabela():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clima (
                    id SERIAL PRIMARY KEY,
                    cidade TEXT,
                    temperatura TEXT,
                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()

def salvar_clima(cidade, temperatura):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO clima (cidade, temperatura) VALUES (%s, %s)",
                (cidade, temperatura)
            )
        conn.commit()

def buscar_historico():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM clima ORDER BY data DESC")
            dados = cur.fetchall()
            colunas = [desc[0] for desc in cur.description]
            return [dict(zip(colunas, row)) for row in dados]
