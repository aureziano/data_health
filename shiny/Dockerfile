# Use a imagem base oficial do Python
FROM python:3.12-slim

# Instalar dependências de sistema necessárias para o LightGBM e bibliotecas científicas
RUN apt-get update && apt-get install -y \
    libgomp1 \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Definir o diretório de trabalho
WORKDIR /app
# Copiar apenas os arquivos necessários para o container
COPY requirements_shiny.txt .
RUN pip install --no-cache-dir -r requirements_shiny.txt

# Copiar os modelos pré-treinados, dados e o código da aplicação
COPY app.py .
COPY *.joblib .
COPY *.csv .
COPY www/ ./www/

# Expor a porta que o Shiny usa por padrão
EXPOSE 8000

# Comando para rodar a aplicação escutando em todas as interfaces
CMD ["shiny", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]
