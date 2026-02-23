from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter 
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler
from app.api.routes import auth, projects, statuses, tasks, access_requests, notifications

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Kanban Task Management API")

app.state.limiter = limiter 
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware) 



app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://to-do-i1al-iufe0zk1k-aadils-projects-6d01c15f.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(statuses.router)
app.include_router(tasks.router)
app.include_router(access_requests.router)
app.include_router(notifications.router)

@app.get("/")
@limiter.limit("10/minute")
async def root(request:Request):
    return {"message": "Kanban Task Management API"}
