# TODO 1: Välj en lättviktig officiel Python-image (t.ex. python:3.12-slim)
FROM python:3.14-slim

# Sätt arbetskatalog i containern:
WORKDIR /app

# Förhindra att python skapar .pyc-filer och buffrar utskrifter:
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Layer Caching: Kopiera bara requirements först
COPY requirements.txt .

# Installera berioenden utan att spara onödig pip-cache:
RUN pip install --no-cache-dir -r requirements.txt

# Kopiera resten av källkoden:
COPY main.py .

# Säkerhet: Skapa en icke-root användare och byt till den
RUN adduser --disabled-password --no-create-home appuser
USER appuser

# Exponera porten appen lyssnar på (t.ex. 8000):
EXPOSE 8000

# TODO 2: Startkommando för uvicorn
# Format: CMD ["program", "arg1", "arg2", ...]
# Kom ihåg att binda till "0.0.0.0" så att containern kan ta emot trafik utifrån!
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]