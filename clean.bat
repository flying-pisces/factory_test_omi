@echo off
echo Cleaning up temporary files...

del /s /q *.pyc 2>nul
del /s /q *.bin 2>nul
del /s /q *_1.json 2>nul
del /s /q *_debug.log 2>nul
del /s /q *.log 2>nul
del /s /q *.*~ 2>nul
del /s /q Thumbs.db 2>nul

echo Removing cache directories...
FOR /d /r . %%d IN ("__pycache__") DO @IF EXIST "%%d" rd /s /q "%%d" 2>nul
FOR /d /r . %%d IN ("CaptureFolder1") DO @IF EXIST "%%d" rd /s /q "%%d" 2>nul  
FOR /d /r . %%d IN ("CaptureFolder2") DO @IF EXIST "%%d" rd /s /q "%%d" 2>nul

echo Cleanup complete!