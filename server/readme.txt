Implementação IEDCS

Trabalho desenvolvido por:
	David Silva (64152)
	Rui Ribeiro (68794)


Instruções de execução:

Virtualenv:
	Os diretórios client e server dizem, respetivamente, às implementações do cliente e do servidor.
	Os pacotes de cada um dos ambientes virtuais estão disponíveis nos ficheiros requirements_server.txt e requirements_client.txt

Nota importante:
Para permitir a correta execução do software, esta tem de ser a ordem de execução dos ficheiros python da primeira vez que é iniciada a máquina.

	Servidor
		1. Executar sql_init.py
			Criar a base de dados
		2. Executar sqlfill.py
			Adicionar valores iniciais à base de dados
		3. Executar server.py
			Ligar o servidor

	Cliente
		1. Executar client.py
			Inicia o módulo do cliente (por agora, o servidor tem de estar a correr; será corrigido na próxima versão.)

As ações do cliente podem ser modificadas no ficheiro client.py

Atualizado (8/dez/2015):

Nesta fase do trabalho preocupámo-nos em desenvolver uma estrutura de comunicação entre o cliente e o servidor eficientes com código o forma mais flexível possível de modo a reduzir o número de funções reescritas na próxima fase. A implementação das bases de dados do cliente e do servidor não são, neste momento, essenciais para o correto funcionamento do trabalho, apesar de muitos módulos de comunicação com as mesmas terem já sido escritos.

Face ao exposto, elementos como a interface gráfica e a loja online apenas serão implementados na próxima fase do trabalho, pelo que a noção de transação não se encontra completamente implementada, apesar de existirem, no código do cliente e do servidor, métodos que visam executar essas tarefas numa fase futura do trabalho. Assim, os únicos ficheiros que podem ser comprados/transferidos são IEDCSTest1 e IEDCSTest2, sendo que o segundo é aquele que está a ser pedido por defeito.
