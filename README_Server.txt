Configuração do Servidor:

Dentro do servidor, certificar que existe ligação à NAT e a uma rede local.
No terminal fazer os seguintes comandos:
	>> sudo apt update
	>> sudo apt install docker.io -y
	>> sudo apt install python3 -y
Download da pasta Logstash 
-> não esquecer de mudar o token e os emails de origem/destino no script de alerta (os campos em que está substituição deverá ser feita estão assinalados por comentário)
Correr o código dentro do terminal desta pasta (atenção que o sistema vai pedir palavra pass)
	>> ansible-playbook elk_master.yml -i inventory.ini --ask-vault-pass
Após a instalação feita confirmar se correu bem
	>> sudo docker ps

Integração com a Gateway
Ler o README_gateway.

Confirmar conectividade entre o servidor e a gateway
	>> ping [gateway ip address]
Após a confirmação fazer o Download da pasta Gateway
Trocar o endereço ip do ficheiro hosts.txt para o [gateway address] 
Correr o código no terminal 
	>> ansible-playbook -i hosts zigbee2mqtt_master3.yml -K
Depois da configuração estar terminada já é possível receber os dados dos sensores e vizualizá-los no site

