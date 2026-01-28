from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from api.routes import auth, health
from db.base import Base
from db.session import engine
from models.user import User
from api.routes.identity import router as identity_router
from api.routes.policy import router as policy_router
from api.routes.documents import router as documents_router
from api.routes.fraud import router as fraud_router
from api.routes.chat import router as chat_router
from api.routes.master import router as master_router
from api.routes.basic import router as basic_router






def create_app() -> FastAPI:
    app = FastAPI(title="Multi Agent Insurance Claim Validation System")

    @app.on_event("startup")
    def startup() -> None:
        try:
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully.")
        except Exception as e:
            print(f"Error during startup: {e}")

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(identity_router)
    app.include_router(policy_router)
    app.include_router(documents_router)
    app.include_router(fraud_router)
    app.include_router(chat_router)
    app.include_router(master_router)
    app.include_router(basic_router)
    return app


app = create_app()