import requests

# URL para mudar a senha do utilizador de sistema do Kibana
url = "http://localhost:9200/_security/user/kibana_system/_password"

# Usamos o ADMIN (elastic) para mudar a senha do sub-utilizador
auth_admin = ("elastic", "changeme")

# Esta é a senha que tem de bater certo com o docker-compose
nova_senha = {"password": "changeme"}

print("A tentar definir a password do kibana_system...")

try:
    r = requests.post(url, auth=auth_admin, json=nova_senha)
    
    if r.status_code == 200:
        print("✅ SUCESSO! A password foi aceite.")
        print("Podes reiniciar o Kibana agora.")
    elif r.status_code == 401:
        print("❌ ERRO: A senha do admin 'elastic' não é 'changeme'. Mudaste-a?")
    else:
        print(f"⚠️ Erro inesperado ({r.status_code}): {r.text}")

except Exception as e:
    print(f"Erro de conexão: {e}")
    print("Verifica se o Elasticsearch está ligado.")
