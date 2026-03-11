# Use a imagem base do Python para Django
FROM python

# Configuração do ambiente de trabalho
ENV PYTHONUNBUFFERED=1
WORKDIR /code


# Instalação das dependências do sistema
RUN apt-get update && apt-get install -y 

# Instalação das dependências do Python
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Copia o código para o contêiner
COPY . /code/

RUN python manage.py collectstatic --no-input

# Comando padrão para executar o servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
