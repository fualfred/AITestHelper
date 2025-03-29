#!/usr/bin/python
# -*- coding: utf-8 -*-
from loguru import logger

import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 配置日志记录

logger.add(f"{BASE_PATH}/logs/aiTest.log", rotation="500 MB", retention="10 days", compression="zip")


def get_logger():
    return logger
