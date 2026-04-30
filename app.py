from dotenv import load_dotenv
from flask import Flask, request, render_template

from weather_service import buscar_clima_por_cidade
from database import criar_tabela, salvar_clima, buscar_historico

load_dotenv()

app = Flask(__name__)

# Cria a tabela ao iniciar (não faz nada se já existir)
criar_tabela()


@app.route('/', methods=['GET'])
def home():
    cidade = request.args.get('cidade')
    weather = None
    error = None
    salvo = None  # None = nenhuma busca; True = salvo; False = já existia

    if cidade:
        result = buscar_clima_por_cidade(cidade)
        if result['error']:
            error = result['message']
        else:
            weather = result['data']
            salvo = salvar_clima(cidade, weather)

    return render_template('index.html',
                           weather=weather,
                           error=error,
                           cidade=cidade,
                           salvo=salvo)


@app.route('/historico')
def historico():
    cidade = request.args.get('cidade')
    registros = buscar_historico(cidade)
    return render_template('historico.html', registros=registros, cidade=cidade)


if __name__ == '__main__':
    app.run(debug=True)