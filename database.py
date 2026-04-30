import os
from datetime import datetime

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Retorna uma conexão com o banco PostgreSQL usando variáveis do .env"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def criar_tabela():
    """Cria a tabela historico_clima se ainda não existir."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_clima (
            id           SERIAL PRIMARY KEY,
            cidade       TEXT    NOT NULL,
            data         TEXT    NOT NULL,
            umidade      NUMERIC,
            vento        NUMERIC,
            precipitacao NUMERIC,
            temp_min     NUMERIC,
            temp_max     NUMERIC
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def registro_existe(cidade: str, data: str) -> bool:
    """Retorna True se já existe registro para essa cidade e data."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM historico_clima WHERE cidade = %s AND data = %s LIMIT 1",
        (cidade.strip().lower(), data)
    )
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    return resultado is not None


def salvar_clima(cidade: str, weather: dict) -> bool:
    """
    Salva os dados climáticos no banco PostgreSQL.
    Retorna True se salvou, False se já existia registro para hoje.

    O dict 'weather' vem de transformar_dados_clima() no weather_service.py.
    Campos usados: umidade, vento, precipitacao,
                   temperatura_min e temperatura_max (do primeiro dia da previsao)
    """
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    cidade_norm = cidade.strip().lower()

    if registro_existe(cidade_norm, data_hoje):
        return False  # já existe, não duplica

    # temperatura_min e temperatura_max vêm do primeiro dia da previsão
    primeiro_dia = weather.get("previsao", [{}])[0] if weather.get("previsao") else {}
    temp_min = primeiro_dia.get("temperatura_min")
    temp_max = primeiro_dia.get("temperatura_max")

    conn = get_connection()
    cursor = conn.cursor()
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
    cursor.close()
    conn.close()
    return True


def buscar_historico(cidade: str = None) -> list:
    """Retorna todo o histórico, ou filtra por cidade se informada."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if cidade:
        cursor.execute(
            "SELECT * FROM historico_clima WHERE cidade = %s ORDER BY data DESC",
            (cidade.strip().lower(),)
        )
    else:
        cursor.execute("SELECT * FROM historico_clima ORDER BY data DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(r) for r in rows]