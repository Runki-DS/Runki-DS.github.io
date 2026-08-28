import os
import json
import subprocess
import tempfile
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Brusnika Prepay API")

# Разрешаем запросы с фронтенда (для локальной разработки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class InnRequest(BaseModel):
    inn: str

@app.post("/api/check")
async def check_inn(request: InnRequest):
    inn = request.inn.strip()

    if not inn.isdigit() or len(inn) not in (10, 12):
        raise HTTPException(status_code=400, detail="ИНН должен содержать 10 или 12 цифр")

    # Создаём временную директорию для работы скрипта
    with tempfile.TemporaryDirectory() as tmpdir:
        # Путь к вашему скрипту brusnika_prepay.py (укажите абсолютный или относительный)
        script_path = os.path.join(os.path.dirname(__file__), "brusnika_prepay.py")

        if not os.path.exists(script_path):
            raise HTTPException(status_code=500, detail="Скрипт brusnika_prepay.py не найден")

        # Запускаем скрипт с переданным ИНН
        # Скрипт должен уметь работать в режиме CLI: python brusnika_prepay.py --inn 1234567890 --json
        # Если ваш скрипт не поддерживает аргументы, обёртка будет ниже
        try:
            result = subprocess.run(
                ["python", script_path, "--inn", inn, "--json"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=30
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=504, detail="Скрипт превысил время выполнения")

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка выполнения скрипта: {result.stderr.strip()}"
            )

        # Парсим JSON-вывод скрипта
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail="Скрипт вернул некорректный JSON"
            )

        # Приводим данные к единому формату (можно расширить)
        return {
            "inn": data.get("inn", inn),
            "shortName": data.get("short_name", "Неизвестно"),
            "age": data.get("age", 0),
            "bo": data.get("bo", "no"),
            "year": data.get("year"),
            "prepay": data.get("prepay", "no"),
            "maxDebt": data.get("max_debt", 0),
            "maxDebtShift": data.get("max_debt_shift", "0%"),
            "credDay": data.get("cred_day", 0),
            "credDayShift": data.get("cred_day_shift", "0%"),
            "equity": data.get("equity", 0)
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)