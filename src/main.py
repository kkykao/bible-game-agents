"""Bible Learning Game - Main Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Bible Learning Game API",
    description="AI agents for biblical learning",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Bible Game API is running"}

@app.get("/api/characters")
async def get_characters():
    return {
        "characters": [
            "Jesus", "Enoch", "Noah", "Abraham", "Isaac",
            "Jacob", "Joseph", "Moses", "Joshua",
            "Matthew", "Mark", "Luke", "John", "David", "Solomon"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
