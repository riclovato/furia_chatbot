FROM selenium/standalone-chrome:latest

# Mudando para usuário root para instalação
USER root

# Instala Python e pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Cria links simbólicos para compatibilidade
RUN ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# Define o diretório de trabalho
WORKDIR /app

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Cria diretório para logs com permissões corretas
RUN mkdir -p /app/logs && \
    chown -R seluser:seluser /app

# Volta para o usuário seluser (padrão da imagem selenium)
USER seluser

# Define variável de ambiente para o arquivo de log
ENV LOG_FILE=/app/logs/bot.log

EXPOSE 8080

# Comando para iniciar a aplicação
CMD ["python", "main.py"]