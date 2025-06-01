from flask import Flask, request, jsonify, render_template, redirect
import re, requests
from models import Interacao, Session
from datetime import datetime

app = Flask(__name__)

# Dados UltraMsg
INSTANCE_ID = "instance123210"
TOKEN = "xvzw57m7xorc6jkw"

# Função para enviar mensagem via UltraMsg
def enviar_mensagem(numero, texto):
    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
    payload = {
        "token": TOKEN,
        "to": numero,
        "body": texto
    }
    response = requests.post(url, data=payload)
    return response.json()

# Padrões de respostas automáticas
respostas_automaticas = {
    r"como (tomar|usar)": "Você deve seguir a posologia da receita. Quer ajuda com algum medicamento específico?",
    r"efeitos? colaterais?": "Os efeitos colaterais mais comuns estão na bula. Informe o nome do medicamento.",
    r"pode (beber|álcool)": "Em geral, não é indicado beber durante o tratamento. Qual o nome do medicamento?",
    r"esqueci de tomar": "Tome assim que lembrar, mas nunca tome dose dupla. Quer verificar para qual medicamento?",
}

@app.route("/webhook", methods=["POST"])
def receber_resposta():
    dados = request.json
    mensagem_usuario = dados.get("mensagem", "").lower()
    numero_usuario = dados.get("numero", "")
    nome_paciente = dados.get("nome", "Paciente")

    tipo_resposta = "humano"
    resposta_sistema = "Obrigado pelo retorno! Sua dúvida foi encaminhada a um atendente. Em breve, entraremos em contato. 🩺"

    for padrao, resposta in respostas_automaticas.items():
        if re.search(padrao, mensagem_usuario):
            tipo_resposta = "automatica"
            resposta_sistema = resposta
            enviar_mensagem(numero_usuario, resposta_sistema)
            break

    session = Session()
    interacao = Interacao(
        nome_paciente=nome_paciente,
        numero=numero_usuario,
        mensagem_usuario=mensagem_usuario,
        resposta_sistema=resposta_sistema,
        tipo_resposta=tipo_resposta
    )
    session.add(interacao)
    session.commit()
    session.close()

    return jsonify({
        "resposta": resposta_sistema,
        "tipo": tipo_resposta
    })

@app.route("/historico")
def historico():
    busca = request.args.get("busca", "").lower()
    session = Session()

    if busca:
        interacoes = session.query(Interacao).filter(
            (Interacao.nome_paciente.ilike(f"%{busca}%")) | 
            (Interacao.numero.ilike(f"%{busca}%"))
        ).order_by(Interacao.data.desc()).all()
    else:
        interacoes = session.query(Interacao).order_by(Interacao.data.desc()).all()

    session.close()
    return render_template("historico.html", interacoes=interacoes, busca=busca)

@app.route("/simular", methods=["POST"])
def simular():
    nome = request.form.get("nome")
    numero = request.form.get("numero")
    mensagem = request.form.get("mensagem")

    with app.test_client() as client:
        client.post("/webhook", json={
            "nome": nome,
            "numero": numero,
            "mensagem": mensagem
        })

    return redirect("/historico")

if __name__ == "__main__":
    app.run(debug=True)
