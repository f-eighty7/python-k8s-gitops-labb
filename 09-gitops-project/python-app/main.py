from fastapi import FastAPI
import os

app = FastAPI(title="LIA DevOps Microservice")

# TODO 1: Skapa ett GET endpoint på "/" som returnerar en enkel dict/json
@app.get("/")
def read_root():
    return {
            # TODO: Returnera t.ex. "status": "running" och "version": "1.0.0"
            "status": "running",
            "message": "Välkommen till vår LIA-tjänst!",
            "version": "1.0.0"
        }


# Hälsokontroll för Kubernetes probes:
@app.get("/healthz")
def health_check():
    return {"status": "healthy"}

# Endpoint för att testa hemligheten:
@app.get("/secret")
def read_secret():
    # TODO 2: Läs in miljövariabeln "APP_SECRET" med os.getenv()
    secret = os.getenv("APP_SECRET")

    if not secret:
        return {"status": "error", "message": "Ingen hemlighet hittades i miljön!"}

    # Av säkerhetsskäll visar vi bara de första tecknen:
    masked_secret = secret[:2] + "****" if len(secret) > 2 else "****"
    return {
        "status": "success",
        "secret_masked": masked_secret
    }