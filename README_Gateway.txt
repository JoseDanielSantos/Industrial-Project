Configuração da Gateway:

Dentro da Gateway, certificar que existe ligação à NAT e a uma rede local.
No terminal fazer os seguintes comandos:
	>> sudo apt update
	>> sudo apt install docker.io -y
	>> sudo apt install python3 -y
Confirmar a secção no docker-compose.yml:
(...)
ports:
      - "8080:8080"
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0  # Porta onde o Zigbee está conectado 
    environment:
      - TZ=Europe/London

Ler o README_server e executar a configuração do gateway
Após a instalação feita confirmar se correu bem
	>> sudo docker ps

