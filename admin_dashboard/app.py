from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.context import CryptContext

from signal_controller.controller import SignalController
from traffic_analyzer.analyzer import TrafficAnalyzer
from database.manager import DatabaseManager
from config.settings import SECURITY

# Security configuration
SECRET_KEY = SECURITY["secret_key"]
ALGORITHM = SECURITY["algorithm"]
ACCESS_TOKEN_EXPIRE_MINUTES = SECURITY["access_token_expire_minutes"]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class TimingConfig(BaseModel):
    min_green: Optional[float] = None
    max_green: Optional[float] = None
    yellow: Optional[float] = None
    min_red: Optional[float] = None
    max_red: Optional[float] = None

# Mock user database - TODO: Replace with real database
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "disabled": False
    }
}

def create_dashboard_app(system) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Traffic Light Control Dashboard")
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Security functions
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_user(db, username: str):
        if username in db:
            user_dict = db[username]
            return UserInDB(**user_dict)
    
    def authenticate_user(fake_db, username: str, password: str):
        user = get_user(fake_db, username)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user
    
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    async def get_current_user(token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = get_user(fake_users_db, username=token_data.username)
        if user is None:
            raise credentials_exception
        return user
    
    # Routes
    @app.post("/token", response_model=Token)
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        user = authenticate_user(fake_users_db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    @app.get("/metrics")
    async def get_metrics(current_user: User = Depends(get_current_user)):
        """Get current traffic metrics."""
        return system.analyzer.get_traffic_metrics()
    
    @app.get("/state")
    async def get_state(current_user: User = Depends(get_current_user)):
        """Get current traffic light state."""
        return system.controller.get_current_state()
    
    @app.post("/timing")
    async def update_timing(
        timing: TimingConfig,
        current_user: User = Depends(get_current_user)
    ):
        """Update traffic light timing configuration."""
        # Only update provided fields
        update_dict = {k: v for k, v in timing.dict().items() if v is not None}
        system.controller.set_timing_config(update_dict)
        return {"status": "success"}
    
    @app.get("/historical")
    async def get_historical_data(
        start_time: datetime,
        end_time: datetime,
        current_user: User = Depends(get_current_user)
    ):
        """Get historical traffic data."""
        metrics = await system.db.get_historical_metrics(start_time, end_time)
        states = await system.db.get_signal_states(start_time, end_time)
        return {
            "metrics": metrics,
            "states": states
        }
    
    @app.post("/emergency/reset")
    async def reset_emergency(current_user: User = Depends(get_current_user)):
        """Reset emergency override state."""
        system.controller.reset_emergency_override()
        return {"status": "success"}
    
    return app 