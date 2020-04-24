del /s *.pyc
del /s *.*~
FOR /d /r . %%d IN ("__pycache__") DO @IF EXIST "%%d" rd /s /q "%%d"