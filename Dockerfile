FROM python:3.11.9-slim

WORKDIR /app

# Installer dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY src ./src
COPY data ./data

# Commande par défaut
ENTRYPOINT ["python", "-m", "src.pipeline"]
CMD []
