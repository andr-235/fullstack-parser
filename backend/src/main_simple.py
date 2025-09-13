#!/usr/bin/env python3
"""
Упрощенная версия main.py для тестирования
"""

from fastapi import FastAPI

app = FastAPI(
    title="VK Comments Parser API",
    version="1.7.0",
    description="API для парсинга комментариев VK",
)

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {"message": "VK Comments Parser API", "version": "1.7.0"}

@app.get("/health")
async def health_check():
    """Проверка здоровья"""
    return {"status": "healthy", "version": "1.7.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
