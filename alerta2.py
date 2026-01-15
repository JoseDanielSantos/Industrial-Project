import smtplib
from email.mime.text import MIMEText
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta, timezone


ES_HOST = "http://localhost:9200"
ES_USER = "elastic" 
ES_PASS = "DkHgTURj1qghpxqNC3Vi" 

EMAIL_ORIGEM = "[insira o mail]"
EMAIL_PASSWORD = "[tokken do mail de origem]" 
EMAIL_DESTINO = "[insira o mail]"

LIMITE_TEMPERATURA = 25.0
INTERVALO_MINUTOS = 5  
INDEX_NAME = "logstash-*" # Deve corresponder ao padrão do Logstash

def verificar_temperatura():
    print("--- A verificar temperaturas... ---")
    
    try:
        es = Elasticsearch(ES_HOST, basic_auth=(ES_USER, ES_PASS), verify_certs=False)
        if not es.ping():
            print("ERRO: Não foi possível ligar ao Elasticsearch!")
            return
    except Exception as e:
        print(f"ERRO de conexão: {e}")
        return

    tempo_atras = datetime.now(timezone.utc) - timedelta(minutes=INTERVALO_MINUTOS)
    timestamp_str = tempo_atras.strftime('%Y-%m-%dT%H:%M:%SZ')

    query = {
        "bool": {
            "must": [
                {"range": {"temperature": {"gt": LIMITE_TEMPERATURA}}}, 
                {"range": {"@timestamp": {"gte": timestamp_str}}} 
            ]
        }
    }

    try:
        resposta = es.search(index=INDEX_NAME, query=query, size=1)
        
        hits = resposta['hits']['total']['value']
        if isinstance(hits, dict):
            hits = hits['value']
            
        print(f"Encontrados {hits} registos acima de {LIMITE_TEMPERATURA}ºC nos últimos {INTERVALO_MINUTOS} min.")

        if hits > 0:
            dado = resposta['hits']['hits'][0]['_source']
            valor_lido = dado.get('temperature', 'N/A')
            sensor = dado.get('sensor', 'Sensor Desconhecido') 
            
            enviar_email(sensor, valor_lido)
        else:
            print("Tudo normal.")
            
    except Exception as e:
        print(f"Erro na query ao Elastic: {e}")

def enviar_email(sensor, valor):
    assunto = f"ALERTA CRITICO: Temperatura {valor}C detetada!"
    corpo = f"""
    AVISO DE SEGURANÇA
    
    O sensor detetou uma temperatura de {valor}C.
    O limite definido e {LIMITE_TEMPERATURA}C.
    
    Verificar laboratorio imediatamente.
    Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """

    msg = MIMEText(corpo)
    msg['Subject'] = assunto
    msg['From'] = EMAIL_ORIGEM
    msg['To'] = EMAIL_DESTINO

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ORIGEM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ORIGEM, EMAIL_DESTINO, msg.as_string())
        server.quit()
        print(f"-> EMAIL ENVIADO COM SUCESSO! ({valor}C)")
    except Exception as e:
        print(f"Erro a enviar email: {e}")

if __name__ == "__main__":
    verificar_temperatura()
