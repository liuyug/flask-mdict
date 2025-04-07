

pyinstaller ^
--icon "flask_mdict/static/favicon.ico" ^
--onefile ^
--console ^
--noconfirm ^
--add-data "flask_mdict/templates:flask_mdict/templates" ^
--add-data "flask_mdict/static:flask_mdict/static" ^
--add-data "flask_mdict/plugins:flask_mdict/plugins" ^
--hidden-import translators ^
--hidden-import urllib3 ^
--hidden-import urllib3_future ^
app.py

copy dist\app.exe dist\flask_mdict.exe /y
copy flask_mdict_wfd.db dist\ /y
del dist\app.exe /q
