from fastapi import FastAPI, Request, Form, Depends, WebSocket, WebSocketDisconnect, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from starlette.middleware.sessions import SessionMiddleware
from database import SessionLocal
from models import Message, User
from database import get_db
import models
import secrets
import json

app = FastAPI()

# DB + Middleware setup
models.Base.metadata.create_all(bind=models.engine)
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(16))

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


active_connections = {}

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    users = db.query(User).filter(User.username != username).all()
    return templates.TemplateResponse("index.html", {"request": request, "username": username, "users": users})

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=username).first()
    if not user or user.password != password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    request.session["username"] = user.username
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@app.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
def signup(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(username=username).first()
    if existing:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username already exists"})
    new_user = User(username=username, password=password)
    db.add(new_user)
    db.commit()
    request.session["username"] = username

    for user, ws in active_connections.items():
        try:
            ws.send_json({"type": "new_user", "username": username})
        except:
            pass

    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

# WebSocket handler
@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    print(f"[WS CONNECTED] {username}")
    await websocket.accept()

    old_socket = active_connections.get(username)
    if old_socket:
        try:
            await old_socket.close()
        except:
            pass

    active_connections[username] = websocket
    await notify_all_status()

    try:
        while True:
            data = await websocket.receive_json()
            receiver = data["to"]
            content = data["message"]

            with SessionLocal() as db:
                msg = Message(sender=username, receiver=receiver, content=content)
                db.add(msg)
                db.commit()

            if receiver in active_connections:
                await active_connections[receiver].send_json({
                    "from": username,
                    "to": receiver,
                    "message": content
                })

    except WebSocketDisconnect:
        print(f"[WS DISCONNECTED] {username}")
        if username in active_connections:
            del active_connections[username]
        await notify_all_status()

# Λήψη status χρηστών
async def notify_all_status():
    online_users = list(active_connections.keys())
    message = json.dumps({"type": "status_update", "online": online_users})
    for user, ws in active_connections.items():
        try:
            await ws.send_text(message)
        except:
            pass


@app.get("/messages/{sender}/{receiver}")
def get_messages(sender: str, receiver: str, db: Session = Depends(get_db)):
    try:
        messages = db.query(Message).filter(
            or_(
                and_(Message.sender == sender, Message.receiver == receiver),
                and_(Message.sender == receiver, Message.receiver == sender)
            )
        ).order_by(Message.timestamp).all()

        # Mark all messages from sender to receiver as read
        db.query(Message).filter(
            and_(
                Message.sender == receiver,
                Message.receiver == sender,
                Message.read == False
            )
        ).update({Message.read: True})
        db.commit()

        return [
            {"sender": m.sender, "content": m.content, "timestamp": m.timestamp.isoformat()}
            for m in messages
        ]

    except Exception as e:
        print(f" Error in /messages/{sender}/{receiver}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

#  για unread counts
@app.get("/unread_counts/{username}")
def get_unread_counts(username: str, db: Session = Depends(get_db)):
    counts = db.query(Message.sender, func.count(Message.id)).filter(
        and_(
            Message.receiver == username,
            Message.read == False
        )
    ).group_by(Message.sender).all()

    return {sender: count for sender, count in counts}

@app.get("/online")
def get_online_users():
    return list(active_connections.keys())

@app.get("/get_users")
def get_users(request: Request, db: Session = Depends(get_db)):
    current_user = request.session.get("username")
    users = db.query(User).filter(User.username != current_user).all()
    return [user.username for user in users]

@app.get("/test")
def test():
    return {"message": "ok"}
