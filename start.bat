@echo off
echo Starting Mess Management System...

cd backend
start cmd /k "venv\Scripts\python.exe app.py"

cd ../frontend
start cmd /k "python -m http.server 8080"

echo Servers started!
echo Frontend is available at: http://localhost:8080/index.html
echo Backend is running at: http://localhost:5000/api
ping 127.0.0.1 -n 3 >nul
start http://localhost:8080/index.html
