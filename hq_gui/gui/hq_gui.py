#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import sys
import logging

from PyQt5 import QtWidgets, QtGui

from .mainwindow import MainWindow


logger = logging.getLogger(__name__)


def list_system_fonts(family=QtGui.QFontDatabase.SimplifiedChinese):
    font_db = QtGui.QFontDatabase()
    for name in font_db.families(family):
        logger.info(name)


def main():
    # fmt = '[%(module)-10s: %(levelname)-5s] %(message)s',
    fmt = '[%(levelname)-5s] %(message)s'
    logging_config = {
        'level': logging.DEBUG,
        'format': fmt,
    }
    logging.basicConfig(**logging_config)

    logger.info('Stock HQ Gui client')

    app = QtWidgets.QApplication(sys.argv)
    font = QtGui.QFont()
    font.setPointSize(10)
    app.setFont(font)
    logger.info('Font: %s' % font.toString())

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
