# Sistema Help Desk - Python Django

Este projeto implementa um **sistema Help Desk** utilizando o **Django** para gestão de chamados de suporte técnico. Através deste sistema, usuários podem abrir tickets, e a equipe de suporte pode gerenciar e resolver as solicitações de forma eficiente.

# Tecnologias Utilizadas
- Python 3.13.1 - Linguagem de programação
- Django - Framework web para desenvolvimento rápido e eficaz
- SQLite (ou outro banco de dados de sua escolha) - Banco de dados relacional utilizado para armazenar dados do sistema

## Clone o repositório 

```bash
git clone https://github.com/Lucasx10/helpdesk-project.git
```

## Instalação

### Crie um Ambiente Virtual com o venv
O venv é uma biblioteca Python padrão, disponível nas versões 3.3 e posteriores. Para criar um ambiente virtual, siga os passos abaixo:

1. Abra um Terminal

Abra o terminal ou prompt de comando do seu sistema operacional.

2. Navegue até o Diretório do Projeto

Use o comando cd para navegar até o diretório raiz do seu projeto.
```bash
cd /caminho/do/seu/projeto
```

3. Crie o Ambiente Virtual

Use o comando `python -m venv nome_do_ambiente` para criar um ambiente virtual com o nome desejado. Substitua nome_do_ambiente pelo nome que você escolher para o ambiente virtual.

```bash
python -m venv meu_ambiente_virtual
```

4. Ative o Ambiente Virtual

Dependendo do seu sistema operacional, o comando para ativar o ambiente virtual varia:

No Windows:

```bash
meu_ambiente_virtual\Scripts\activate
```

No macOS e Linux:
```bash
source meu_ambiente_virtual/bin/activate
```

Você verá o nome do ambiente virtual atual no prompt do terminal, indicando que o ambiente foi ativado com sucesso.

Como Desativar um Ambiente Virtual
Para desativar um ambiente virtual e retornar ao ambiente global do Python, basta digitar:

```bash
deactivate
```
## Instalar as Dependências
Como Instalar Pacotes em um Ambiente Virtual

Com o ambiente virtual ativado, você pode instalar pacotes e bibliotecas específicos para o seu projeto sem afetar o ambiente global do Python. Use o comando pip para instalar pacote django:

```bash
pip install Django
```

## Executar o Projeto
Agora que você tem o ambiente virtual configurado e as dependências instaladas, você pode rodar o projeto.

1. Realize as Migrações do Banco de Dados

Execute o seguinte comando para criar as tabelas no banco de dados:

```bash
python manage.py makemigrations
python manage.py migrate
```

Execute o Servidor de Desenvolvimento

Por fim, inicie o servidor de desenvolvimento com o comando:

```bash
python manage.py runserver
```
O sistema estará disponível em http://localhost:8000.
