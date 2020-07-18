

rmdir build /s /q
del dist\flask_mdict.exe

pyinstaller --onefile --name flask_mdict ^
--hidden-import pkg_resources.py2_warn ^
--add-data flask_mdict\templates;flask_mdict\templates ^
--add-data flask_mdict\static;flask_mdict\static ^
--icon flask_mdict\static\logo.ico ^
app.py
