Configuração da Interface Web e dos Relatórios:

1)Dentro da VM do servidor, abrir outro terminal na pasta do projeto (~/LogStash ou como for chamada na altura), criar o ambiente virtual:

	python3 -m venv venv
	source venv/bin/activate

2) Instalar as dependências (python para o reporting): venv ativo, ou seja (venv), instalar as bibliotecas necessárias:

	pip install flask elasticsearch fpdf2

3) Garantir que os seguintes itens existem na pasta do projeto:
/pasta_do_projeto
├── app.py                 (O servidor web Flask)
├── PICadvanced_logo.png   (Logótipo para o relatório PDF)
└── templates/				(nome da pasta onde se encontra index.html)
└── index.html         (a página web com o iFrame do Kibana)

-> não esquecer de mudar o user e a pass no script app.py (os campos em que está substituição deverá ser feita estão assinalados por comentário)

4) Execução do Site - para iniciar o servidor web na porta 5000: no (venv) ainda, python app.py (à partida ficará ligado sempre que o setup estiver ligado)

5) Para manter o site a correr em background (mesmo fechando o terminal): nohup python app.py > site.log 2>&1 &


A O site ficará disponível em: http://[IP_DO_SERVIDOR]:5000 O relatório PDF é gerado no botão "Download PDF Report". 

