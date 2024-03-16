set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890

timeout /t 60 /nobreak

C:\Apps\Scoop\apps\miniconda3\current\envs\web\python.exe C:\Codes\daily-helper\main.py
