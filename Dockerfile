FROM python:3.10-slim

# Installer curl et les certificats
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Installer uv via le script officiel
ADD https://astral.sh/uv/0.6.9/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ajouter uv au PATH
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

COPY requirements.txt .

# ✅ Installer dans le système (pas dans une venv)
RUN uv pip install --system -r requirements.txt

COPY app.py .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
