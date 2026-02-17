@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Create a .env file (copy from .env.example)
echo 2. Update DATABASE_URL in .env with your PostgreSQL credentials
echo 3. Run: venv\Scripts\activate
echo 4. Run: alembic revision --autogenerate -m "Initial migration"
echo 5. Run: alembic upgrade head
echo 6. Run: uvicorn app.main:app --reload
