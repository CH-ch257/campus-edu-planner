@echo off
chcp 65001 >nul
title 校园资料AI检索助手 - 一键启动
echo ============================================
echo   校园资料AI检索助手 一键启动
echo   启动后端(8000) + 前端(Vite)
echo ============================================
echo.

cd /d "%~dp0"

echo [1/2] 启动后端 (端口 8000) ...
start "后端-8000" cmd /k "cd /d %~dp0backend && venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000"

timeout /t 5 /nobreak >nul

echo [2/2] 启动前端 (Vite) ...
start "前端-Vite" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 6 /nobreak >nul

echo.
echo ============================================
echo   启动完成！请查看"前端-Vite"窗口中的地址
echo   默认:  http://localhost:5173
echo   (若 5173 被占用会自动切到 5174，以窗口显示为准)
echo   登录账号: admin/admin123 (管理员)
echo             teacher/teacher123 (教师)
echo             stu_demo/demo123 (学生)
echo ============================================
pause
