from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Interacao(Base):
    __tablename__ = 'interacoes'

    id = Column(Integer, primary_key=True)
    nome_paciente = Column(String(100))
    numero = Column(String(20))
    mensagem_usuario = Column(Text)
    resposta_sistema = Column(Text)
    tipo_resposta = Column(String(20))
    data = Column(DateTime, default=datetime.utcnow)

engine = create_engine("sqlite:///interacoes.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
