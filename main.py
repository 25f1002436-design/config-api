from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULTS = {"port": 8000, "workers": 1, "debug": False,
            "log_level": "info", "api_key": "default-secret-000"}
YAML_LAYER = {"port": 8824, "workers": 13, "log_level": "info",
              "api_key": "key-ynqvo949ui"}
DOTENV_LAYER = {"APP_LOG_LEVEL": "error", "APP_API_KEY": "key-s2ezj9dwpu"}
OS_ENV_LAYER = {"APP_PORT": "8209", "APP_WORKERS": "15"}


def norm_key(k):
    k = k.strip()
    if k.upper().startswith("APP_"):
        k = k[4:]
    k = k.lower()
    if k == "num_workers":
        k = "workers"
    return k


def coerce(k, v):
    if k in ("port", "workers"):
        try:
            return int(str(v).strip())
        except ValueError:
            return v
    if k == "debug":
        if isinstance(v, bool):
            return v
        return str(v).strip().lower() in ("true", "1", "yes", "on")
    return str(v)


@app.get("/")
def home():
    return {"status": "ok"}


@app.get("/effective-config")
def effective_config(set_: list[str] = Query(default=[], alias="set")):
    cfg = dict(DEFAULTS)
    for layer in (YAML_LAYER, DOTENV_LAYER, OS_ENV_LAYER):
        for k, v in layer.items():
            cfg[norm_key(k)] = v
    for item in set_:
        if "=" in item:
            k, _, v = item.partition("=")
            cfg[norm_key(k)] = v
    out = {k: coerce(k, v) for k, v in cfg.items()}
    out["api_key"] = "****"
    return out
