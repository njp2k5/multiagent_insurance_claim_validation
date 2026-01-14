from fastapi import FastAPI
from api.routes import auth, health
from db.base import Base
from db.session import engine
from models.user import User
from api.routes.claims import router as claims_router
from api.routes.chat import router as chat_router
from api.routes.agents import router as agents_router
from api.routes.identity import router as identity_router
from api.routes.policy import router as policy_router






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
    app.include_router(agents_router)
    app.include_router(claims_router)
    app.include_router(chat_router)
    app.include_router(identity_router)
    app.include_router(policy_router)

    return app


app = create_app()