from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from jose import jwt
from datetime import datetime, timedelta
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import Security

# ---- Initialization ----
app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update this if the frontend URL changes
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

SECRET_KEY = "supersecretkey123"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class PaymentRequest(BaseModel):
    amount: float

# In-memory user storage for simplicity
users_db = {
    "user1": {"username": "user1", "password": "password123", "role": "user"},
    "admin": {"username": "admin", "password": "admin123", "role": "admin"}
}

# ---- Utility Functions ----
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates a JWT token with an optional expiration.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_token(token: str):
    """
    Decodes a JWT token and validates its content.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Verifies the current user from the JWT token.
    """
    payload = decode_token(token)
    username = payload.get("sub")
    if username not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    return users_db[username]

# ---- Dependency for Authentication ----
def require_authenticated_user(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user

# ---- Models ----
class User(BaseModel):
    username: str
    role: str

class PaymentNotification(BaseModel):
    payment_id: str
    status: str
    amount: float

# ---- Error Handling ----
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for validation errors.
    """
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation Error", "errors": exc.errors()}
    )

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for HTTP exceptions to return detailed error messages.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# ---- Endpoints ----

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates a user and returns a JWT token.
    """
    user = users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Retrieves details about the currently logged-in user.
    """
    return {"username": current_user["username"], "role": current_user["role"]}

@app.post("/payments/charge")
async def process_payment(request: PaymentRequest, current_user: dict = Security(require_authenticated_user)):
    """
    Process a payment (requires authentication).
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    amount = request.amount

    if amount <= 0:
        raise HTTPException(status_code=422, detail="Invalid payment amount")

    if current_user["role"] != "admin" and amount > 100:
        raise HTTPException(status_code=403, detail="Not authorized for large payments")

    await asyncio.sleep(2)  # Simulate delay
    return {"status": "success", "amount": amount}

@app.post("/webhooks/payment")
async def payment_webhook(notification: PaymentNotification):
    """
    Listens for payment notifications from a payment gateway.
    """
    print(f"Received webhook: {notification}")

    asyncio.create_task(handle_payment_notification(notification))
    return {"status": "received"}

# ---- Background Tasks ----

async def handle_payment_notification(notification: PaymentNotification):
    """
    Handles payment updates asynchronously.
    """
    await asyncio.sleep(1)  # Simulate processing time
    print(f"Processed payment: {notification.payment_id} with status {notification.status}")

@app.get("/")
async def root():
    """
    Test endpoint to verify the app is running.
    """
    return {"message": "FastAPI app is running!"}
