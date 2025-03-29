#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from datetime import datetime
import streamlit as st
import hashlib


def format_size(size):
    units = ['B', 'KB', 'MB', 'GB']
    index = 0
    while size >= 1024 and index < 3:
        size /= 1024
        index += 1
    return f"{size:.2f} {units[index]}"


def get_file_list(path):
    files = []
    try:
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            stat = os.stat(full_path)
            files.append({
                "name": item,
                "size": format_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
            })
    except Exception as e:
        st.error(f"无法访问目录: {str(e)}")
    return files


def generate_id(text):
    return hashlib.sha256(text.encode()).hexdigest()[:8]


def formate_reqs(reqs: dict) -> list:
    try:
        functional = reqs['functional']
        non_functional = reqs['non_functional']
        functional_all = []
        for item in functional:
            functional_all.append({"类型": "功能需求", "需求点": item})
        for item in non_functional:
            functional_all.append({"类型": "非功能需求", "需求点": item})
        return functional_all
    except Exception as e:
        print(f"异常{str(e)}")
