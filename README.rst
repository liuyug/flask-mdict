===========
Flask-MDict
===========

.. NOTE::

    Follow MIT and 996.ICU license.

Screenshot
==========

.. image:: mdict_screenshot.png

Usage
======
Install
--------
::

    git clone https://github.com/liuyug/flask-mdict.git

    cd flask-mdict
    pip3 install -r requirements.txt

    mkdir content
    # copy MDICT dictionary into content directory
    cp <mdict> content/

    # install word frequency database from ecdict csv
    ecdict.sh
    # or copy current flask_mdict_wfd.db to your content directory
    # cp flask_mdict_wfd.db content/


Run
----
Cli::

    python app.py

    python app.py --mdict-dir your_mdict_path

    python app.py --host 127.0.0.1:5248


Window usage::

    # 1. put files into path:
    # path\
    # path\flask_mdict.exe
    # path\flask_mdict_wfd.db
    # path\your_mdict_path

    # 2. run
    flask_mdict.exe

    # 3. Browser
    firefox http://127.0.0.1:5248


Config
-------

+ flask_mdict.json: server settings
+ flask_mdict.db: dictionary settings and searching history
+ flask_mdict_wfd.db: word frequency db [option]

Browser
--------
::

    firefox http://127.0.0.1:5248

.. note::

    +   MDict original query code come from mdx-server_
    +   Python3

.. _mdx-server: https://github.com/ninja33/mdx-server

Donate 捐赠
=============

.. |alipay_pay| image:: alipay_pay.jpg
    :width: 45%

.. |wx_pay| image:: wx_pay.png
    :width: 45%

|wx_pay| |alipay_pay|
