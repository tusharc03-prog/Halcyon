@echo off
setlocal
cd /d "%~dp0"
echo Building Halcyon India Technosys ERP...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --windowed --onedir ^
  --name "Halcyon_India_Technosys_ERP" ^
  --add-data "ui;ui" ^
  --collect-all PySide6 ^
  --collect-all shiboken6 ^
  app.py
if errorlevel 1 (
  echo.
  echo BUILD FAILED. Read the error above.
  pause
  exit /b 1
)
echo.
echo BUILD SUCCESSFUL.
echo EXE: dist\Halcyon_India_Technosys_ERP\Halcyon_India_Technosys_ERP.exe
pause
