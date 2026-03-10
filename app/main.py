from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import search_routes
from app.routes import report_routes
from app.routes import chat_routes

app = FastAPI()

# Configura los orígenes permitidos
origins = [
    "http://localhost:5173",  # puerto de tu frontend
    "http://127.0.0.1:5173",  # a veces Vite usa 127.0.0.1
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # o ["*"] para desarrollo
    allow_credentials=True,
    allow_methods=["*"],     # permite POST, GET, OPTIONS, etc.
    allow_headers=["*"],     # permite Content-Type y otros headers
)


app.include_router(chat_routes.router)
app.include_router(search_routes.router)
app.include_router(report_routes.router)
