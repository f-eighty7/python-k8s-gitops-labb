from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
import json
import urllib.request

# Konstanter för Kubernetes och OpenBao:
K8S_TOKEN_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"
OPENBAO_ADDR = os.getenv("OPENBAO_ADDR", "http://openbao.openbao.svc.cluster.local:8200")
OPENBAO_ROLE = os.getenv("OPENBAO_ROLE", "lia-role")

def fetch_secret_from_openbao() -> str | None:
    """Hämtar APP_SECRET från OpenBao via Kubernetes Auth."""
    if not os.path.exists(K8S_TOKEN_PATH):
        # Vi körs antagligen lokalt under utveckling
        return None

    try:
        # TODO 1: Läs in poddens JWT-token från K8S_TOKEN_PATH
        # Tips: Öppna filen och läs innehållet som en sträng (.strip())
        with open(K8S_TOKEN_PATH, "r") as f:
            jwt_token = f.read().strip()

        # TODO 2: Förbered inloggningsanropet till OpenBao
        # URL: f"{OPENBAO_ADDR}/v1/auth/kubernetes/login"
        # Payload (JSON): {"jwt": jwt_token, "role": OPENBAO_ROLE}
        login_url = f"{OPENBAO_ADDR}/v1/auth/kubernetes/login"
        login_payload = json.dumps({"jwt": jwt_token, "role": OPENBAO_ROLE}).encode("utf-8")

        
        # TODO 3: Skicka POST-request med urllib.request.Request och hämta client_token
        login_req = urllib.request.Request(
            login_url,
            data=login_payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(login_req) as response:
            # TODO: Läs svaret med response.read() och konvertera från json med json.loads()
            login_data = json.loads(response.read())
            # TODO: Hämta ut client_token från login_data
            client_token = login_data["auth"]["client_token"]
        # TODO 4: Gör en GET-request till hemligheten i OpenBao
        secret_url = f"{OPENBAO_ADDR}/v1/secret/data/lia-app"
        # TODO: Skapa ett Request-objekt för secret_url med headern "X-Vault-Token": client_token
        secret_req = urllib.request.Request(
            secret_url,
            headers={"X-Vault-Token": client_token}
        )
        
        with urllib.request.urlopen(secret_req) as response:
            # TODO: Läs och avkoda JSON-svaret
            secret_data = json.loads(response.read())
            # TODO: Plocka ut "APP_SECRET" från secret_data (kom ihåg: två nivåer av "data"!)
            secret_value = secret_data["data"]["data"]["APP_SECRET"]
        return secret_value

    except Exception as e:
        print(f"Kunde inte hämta hemlighet från OpenBao: {e}")
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Vid applikationsstart:
    secret = fetch_secret_from_openbao()
    if secret:
        os.environ["APP_SECRET"] = secret
        print("Laddade APP_SECRET framgångsrikt från OpenBao!")
    else:
        print("Kör med befintlig miljövariabel för APP_SECRET.")
    yield


app = FastAPI(title="LIA DevOps Microservice", lifespan=lifespan)

@app.get("/")
def read_root():
    return {
        "status": "running",
        "message": "Välkommen till vår LIA-tjänst!",
        "version": "1.0.0"
    }

@app.get("/healthz")
def health_check():
    return {"status": "healthy"}

@app.get("/secret")
def read_secret():
    secret = os.getenv("APP_SECRET")
    if not secret:
        return {"status": "error", "message": "Ingen hemlighet hittades i miljön!"}

    masked_secret = secret[:2] + "****" if len(secret) > 2 else "****"
    return {
        "status": "success",
        "secret_masked": masked_secret
    }