from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import model
from routers import logs

app = FastAPI()

app.include_router(model.router)
app.include_router(logs.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # p/ permitir requisições do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "farcry backend working..."}