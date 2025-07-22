@echo off
REM Multi-User Flashcard Quiz App - Windows Launcher
REM This script helps you easily start the quiz server and clients

:menu
cls
echo.
echo ============================================
echo   🎓 Multi-User Flashcard Quiz App
echo ============================================
echo.
echo Please choose an option:
echo.
echo 1. 🧪 Run Tests (Verify Setup)
echo 2. 🖥️  Start Quiz Server
echo 3. 👤 Start Quiz Client
echo 4. 📖 View README
echo 5. ❌ Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto test
if "%choice%"=="2" goto server
if "%choice%"=="3" goto client
if "%choice%"=="4" goto readme
if "%choice%"=="5" goto exit
echo Invalid choice. Please try again.
pause
goto menu

:test
cls
echo 🧪 Running Quiz App Tests...
echo.
python test_quiz.py
echo.
pause
goto menu

:server
cls
echo 🖥️ Starting Quiz Server...
echo Press Ctrl+C to stop the server
echo.
python server.py
echo.
pause
goto menu

:client
cls
echo 👤 Starting Quiz Client...
echo.
python client.py
echo.
pause
goto menu

:readme
cls
echo 📖 Opening README file...
start README.md
goto menu

:exit
echo.
echo 👋 Thanks for using the Quiz App!
echo.
pause
exit
