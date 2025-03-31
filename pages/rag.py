#!/usr/bin/python
# -*- coding: utf-8 -*-
import ast
import os

import streamlit as st
from sqlalchemy import select, delete
import time
from models.models import RagFileRecord
from utils.parser import file_loader

st.markdown("""
<style>
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stRadio [role=radiogroup] {
        gap: 8px;
    }
    .stRadio [data-testid=stMarkdown] {
        font-size: 16px;
        padding: 12px;
        border-radius: 4px;
        transition: all 0.3s;
    }
    .stRadio [data-testid=stMarkdown]:hover {
        background-color: #e9ecef;
    }
    .st-eb {
        padding: 20px !important;
    }
</style>
""", unsafe_allow_html=True)
st.subheader("🧀RAG知识库")
uploaded_file = st.file_uploader("Choose a file", type=["txt", "csv", "docx"],
                                 accept_multiple_files=False)
BASE_PATH = st.session_state.base_path
if uploaded_file is not None:
    with open(os.path.join(f"{BASE_PATH}/rag", uploaded_file.name), "wb") as f:
        f.write(uploaded_file.read())
        st.success("文件上传成功✅")
    file_path = os.path.join(f"{BASE_PATH}/rag", uploaded_file.name)
    if os.path.exists(file_path):
        with st.spinner("🎯 正在创建知识库，请稍候...", show_time=True):
            texts, splits, metadatas = file_loader(file_path)
            ids = st.session_state.vector_db.add_documents(splits)
            rag_file_record = RagFileRecord(file_name=uploaded_file.name, ids=str(ids))
            st.session_state.db_session.add(rag_file_record)
            st.session_state.db_session.commit()
            st.success("知识库创建成功✅")
            st.session_state.logger.info("知识库创建成功✅")
            # st.rerun()
result = st.session_state.db_session.execute(select(RagFileRecord)).scalars().all()
st.session_state.ragFileList = result
st.subheader("RAG知识库")
if len(st.session_state.ragFileList) > 0:
    cols = st.columns([4, 2])
    cols[0].markdown("**文件名**")
    cols[1].markdown("**操作**")
    for file in st.session_state.ragFileList:
        cols = st.columns([4, 2])
        cols[0].markdown(f"- {file.file_name}")
        delete_key = f"delete_{file.file_name}"
        with st.spinner("正在删除文件，请稍候...", show_time=True):
            if cols[1].button("🗑️ 删除", key=delete_key):
                ids = st.session_state.db_session.execute(select(RagFileRecord).filter(
                    RagFileRecord.file_name == file.file_name)).scalar().ids
                ids = ast.literal_eval(ids)
                st.session_state.vector_db.delete(ids)
                st.session_state.db_session.execute(
                    delete(RagFileRecord).where(RagFileRecord.file_name == file.file_name))
                st.session_state.db_session.commit()
                if os.path.exists(f"{BASE_PATH}/rag/{file.file_name}"):
                    st.session_state.logger.info(f"{file.file_name}文件存在")
                    os.remove(f"{BASE_PATH}/rag/{file.file_name}")
                st.success("文件删除成功✅")
                st.rerun()
