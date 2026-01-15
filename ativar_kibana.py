import requests
import time

# Configurações
url = "http://localhost:9200/_security/user/kibana_system/_password"
auth_admin = ("elastic", "changeme") 
nova_senha = {"password": "changeme"} 

print("A tentar configurar a password do utilizador kibana_system...")

for i in range(10):
    try:
        r = requests.post(url, auth=auth_admin, json=nova_senha)
        
        if r.status_code == 200:
            print("✅ SUCESSO! Password do kibana_system definida.")
            print("Agora podes arrancar o Kibana.")
            break
        elif r.status_code == 401:
             print("❌ Erro de Autenticação: A password do user 'elastic' não é 'changeme'.")
             break
        else:
            print(f"⚠️ Erro {r.status_code}: {r.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"⏳ O Elasticsearch ainda não está pronto... (Tentativa {i+1}/10)")
    
    time.sleep(5)
