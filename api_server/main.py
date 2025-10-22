from fastapi import FastAPI, Query as FastAPIQuery, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from api_server.routers import login, inference, history, session

load_dotenv()

app = FastAPI(title="Medical System", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login.router)
app.include_router(inference.router)
app.include_router(history.router)
app.include_router(session.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


