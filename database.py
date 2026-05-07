import os
from datetime import datetime
import psycopg


def get_connection():
    return psycopg.connect(os.environ.get("DATABASE_URL"))


def criar_tabela():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico_clima (
                    id SERIAL PRIMARY KEY,
                    cidade TEXT NOT NULL,
                    data TEXT NOT NULL,
                    umidade NUMERIC,
                    vento NUMERIC,
                    precipitacao NUMERIC,
                    temp_min NUMERIC,
                    temp_max NUMERIC
                )
            """)
        conn.commit()


def registro_existe(cidade: str, data: str) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM historico_clima WHERE cidade = %s AND data = %s LIMIT 1",
                (cidade.strip().lower(), data)
            )
            return cursor.fetchone() is not None


def salvar_clima(cidade: str, weather: dict) -> bool:
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    cidade_norm = cidade.strip().lower()

    if registro_existe(cidade_norm, data_hoje):
        return False

    primeiro_dia = weather.get("previsao", [{}])[0] if weather.get("previsao") else {}
    temp_min = primeiro_dia.get("temperatura_min")
    temp_max = primeiro_dia.get("temperatura_max")

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO historico_clima
                (cidade, data, umidade, vento, precipitacao, temp_min, temp_max)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                cidade_norm,
                data_hoje,
                weather.get("umidade"),
                weather.get("vento"),
                weather.get("precipitacao", 0),
                temp_min,
                temp_max,
            ))
        conn.commit()

    return True


def buscar_historico(cidade: str = None) -> list:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            if cidade:
                cursor.execute(
                    "SELECT * FROM historico_clima WHERE cidade = %s ORDER BY data DESC",
                    (cidade.strip().lower(),)
                )
            else:
                cursor.execute("SELECT * FROM historico_clima ORDER BY data DESC")

            rows = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]
            return [dict(zip(colunas, row)) for row in rows]
