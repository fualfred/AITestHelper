#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

import streamlit as st

from config.settings import settings
from models.models import get_db_session
from utils.embeddings import create_vector_db
from utils.get_llm import get_llm
from utils.logger import get_logger

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
# 初始化日志
st.session_state.logger = get_logger()

st.session_state.base_path = BASE_PATH
# 初始化llm
st.session_state.llm = get_llm(settings.COMPANY)
# 初始化数据库
st.session_state.db_session = get_db_session()

st.session_state.vector_db = create_vector_db()

st.set_page_config(page_title="AI测试工具", layout="wide")
test_cases_gen_page = st.Page("./pages/testcases_gen.py", title="🧪用例生成", default=True)
requirements_page = st.Page("./pages/requirements.py", title="📋需求分析")
AI_assistants_page = st.Page("./pages/AIassitants.py", title="🤖AI测试助手")
rag_page = st.Page("./pages/rag.py", title="📝RAG知识库")
pg = st.navigation([test_cases_gen_page, requirements_page, AI_assistants_page, rag_page])

pg.run()
