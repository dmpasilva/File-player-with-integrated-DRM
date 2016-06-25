# IEDCS - Identity Enabled Distribution Control System #

Trabalho desenvolvido por:
	David Silva (64152)
	Rui Ribeiro (68794)


Instruções de execução:

Virtualenv:
	Os diretórios client e server dizem, respetivamente, às implementações do cliente e do servidor.
	Os pacotes de cada um dos ambientes virtuais estão disponíveis nos ficheiros requirements_server.txt e requirements_client.txt

Cliente:
	Editar o ficheiro runme.sh para incluir o caminho para o interpretador do virtualenv do cliente
	Executar runme.sh

	Nota: Desassociar um cliente de um equipamento pode levar à perda das compras realizadas pelo mesmo se estas não tiverem sido realizadas também noutro computador.

Servidor:
	Editar o ficheiro runme_xxxxx.sh (onde xxxxx é o Sistema Operativo) para incluir o caminho para o interpretador do virtualenv do servidor
	Executar runme_osx.sh em OS X e runme_linux.sh em Linux

	Passwords: ambas as passwords pedidas são "iedcs_2k15" (sem aspas)
		No caso de a password do encfs estar incorreta, o erro no lado do cliente é a mensagem "This ebook was not purchase for this user".