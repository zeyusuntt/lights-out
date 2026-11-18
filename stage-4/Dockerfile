FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /srv

COPY requirements.txt constraints.txt ./
RUN pip install --no-cache-dir -r requirements.txt -c constraints.txt

COPY app ./app

RUN useradd --system --no-create-home dossier && mkdir -p /srv/data && chown dossier /srv/data
USER dossier

EXPOSE 8080
CMD ["python", "-m", "app.main"]
