#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os.path

from six.moves.configparser import ConfigParser


config = None


def get_config():
    global config
    if config:
        return config

    cfg_path = os.getenv('STOCK_CONFIG') or 'config/default.ini'
    if not os.path.exists(cfg_path):
        raise Exception('Do not find config file: ' + cfg_path)

    config = ConfigParser()
    config.read(cfg_path)
    return config
