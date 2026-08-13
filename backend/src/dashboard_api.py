from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import db

app = FastAPI()

# Enable CORS for http://localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/call-stats")
async def get_stats():
    return db.get_call_stats()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
