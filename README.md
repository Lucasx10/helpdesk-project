# Sistema Help Desk - Python Django

Este projeto implementa um **sistema Help Desk** utilizando o **Django** para gestão de chamados de suporte técnico. Usuários podem abrir tickets, e a equipe de suporte pode gerenciar e resolver as solicitações de forma eficiente.

---

## Tecnologias Utilizadas

- Python 3.12.1  
- Django  
- SQLite (ou outro banco de dados de sua escolha)  
- Docker + Docker Compose  
- Nginx  
- Daphne (ASGI) 

---

## Clone o Repositório

```bash
git clone https://github.com/Lucasx10/helpdesk-project.git
cd helpdesk-project
```

## 🐳 Executando o Projeto com Docker (modo recomendado)

Este modo permite rodar a aplicação sem precisar configurar ambiente virtual local e facilita o deploy em múltiplas máquinas na mesma rede.

### Pré-requisitos

- Docker: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)  
- Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)  

---

### Estrutura do Docker

O projeto inclui:

- **Dockerfile**: Configura Python, instala dependências e roda **Daphne**  
- **docker-compose.yml**: Orquestra os serviços `django`, `nginx` 
- **nginx/default.conf**: Configura Nginx para servir arquivos estáticos e encaminhar requisições para Django

---

### Build e execução

```bash
docker-compose build
docker-compose up
Django/Daphne: porta 8000 dentro do container
Nginx: porta 80 do computador host
```

## Acesso à aplicação

- **Mesmo computador:** [http://localhost/](http://localhost/)  
- **Outro PC na rede local:** `http://IP_DO_HOST/`  

---

## Observações sobre WebSockets

- O projeto utiliza **Django Channels** e **ASGI**.  
- Nginx já está configurado para WebSockets:

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";

```
## 🖥️ Desenvolvimento Local (sem Docker)
### 1️⃣ Criar Ambiente Virtual
```
cd /caminho/do/seu/projeto
```
### Criar ambiente virtual
```
python -m venv meu_ambiente_virtual
```

### Ativar
### Windows
```
meu_ambiente_virtual\Scripts\activate
```
### macOS/Linux
```
source meu_ambiente_virtual/bin/activate
```

## Desativar o ambiente virtual:
```bash
deactivate
```

# 2️⃣ Instalar Dependências
```
pip install -r requirements.txt
```
# 3️⃣ Rodar o Projeto
# Migrações
```
python manage.py makemigrations
python manage.py migrate
```
# Coletar arquivos estáticos
```
python manage.py collectstatic --no-input
```
# Rodar servidor de desenvolvimento
```
python manage.py runserver
```
Acesse: http://localhost:8000

🎥 Video Demonstração

[https://github.com/Lucasx10/helpdesk-project/releases/download/main/Tutorial.HelpDesk.mp4](https://github.com/user-attachments/assets/0daae3c4-e8f7-41c4-9a57-4a55ccdb9387)
