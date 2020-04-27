del /s *.pyc
del /s *.bin
del /s *_1.json
del /s *_debug.log
del /s *.log
del /s *.*~
FOR /d /r . %%d IN ("__pycache__") DO @IF EXIST "%%d" rd /s /q "%%d"
FOR /d /r . %%d IN ("CaptureFolder1") DO @IF EXIST "%%d" rd /s /q "%%d"
FOR /d /r . %%d IN ("CaptureFolder2") DO @IF EXIST "%%d" rd /s /q "%%d"