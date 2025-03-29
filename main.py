#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime

import streamlit as st
import pandas as pd
import ast

from utils.function_cases import generate_function_cases
from utils.utils import get_file_list, generate_id
import os
from utils.parser import file_loader
from langchain_chroma import Chroma
from config.settings import settings
from utils.embeddings import create_vector_db
from models.models import get_db_session, RagFileRecord
from sqlalchemy import select, delete
from utils.get_llm import get_llm
from utils.logger import get_logger
from utils.requirements_analyze import analyze_requirement
from utils.utils import formate_reqs

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
# 初始化日志
st.session_state.logger = get_logger()

# 初始化llm
st.session_state.llm = get_llm(settings.COMPANY)
# 初始化数据库
st.session_state.db_session = get_db_session()

st.session_state.vector_db = create_vector_db()
# 页面样式设置
st.set_page_config(page_title="AI测试工具", layout="wide")
# 自定义CSS样式
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

# 初始化session state
if 'requirement_text' not in st.session_state:
    st.session_state.requirement_text = ""
if 'test_cases' not in st.session_state:
    st.session_state.test_cases = pd.DataFrame()
st.session_state.ragFileList = get_file_list(f"{BASE_PATH}/rag")

# 侧边栏导航
with st.sidebar:
    st.header("🔧 AI测试工具")
    page = st.radio(
        "功能导航",
        options=["🧪 智能测试用例生成", "📋 需求分析"],
        format_func=lambda x: x.split(" ")[1],
        help="选择需要使用的功能模块"
    )

# 需求分析页面
if page == "📋 需求分析":

    with st.expander("📥 请上传需求文档", expanded=True):
        req_file = st.file_uploader("上传需求文档", type=["txt", "csv", "docx"], accept_multiple_files=False)
        if req_file is not None:
            with open(os.path.join(f"{BASE_PATH}/requirements", req_file.name), "wb") as f:
                f.write(req_file.read())
            st.success("文件上传成功！")
    col1 = st.columns(1)
    with col1[0]:
        with st.spinner("🔍 正在分析需求文档，请稍候...", show_time=True):
            if st.button("🚀 执行分析", use_container_width=True) and req_file:
                texts, splits, metadatas = file_loader(os.path.join(f"{BASE_PATH}/requirements", req_file.name))
                st.session_state.requirement_text = texts
                resp_reqs = analyze_requirement(st.session_state.llm, "\n".join(texts))
                st.session_state.format_reqs = formate_reqs(resp_reqs)

    if st.session_state.requirement_text:
        st.divider()
        st.subheader("🔍 分析结果")
        st.session_state.req_cases_list = []
        req_col = st.columns([4, 3, 2])
        req_col[0].markdown("**需求类型**")
        req_col[1].markdown("**需求点**")
        req_col[2].markdown("**操作**")
        for req in st.session_state.format_reqs:
            req_col1 = st.columns([4, 3, 2])
            req_col1[0].markdown(f"*{req['类型']}*")
            req_col1[1].markdown(f"*{req['需求点']}*")
            with st.spinner("🎯 正在生成用例，请稍候", show_time=True):
                if req_col1[2].button("🎯 生成用例", key=generate_id(req["需求点"])):
                    req_retrievers = st.session_state.vector_db.as_retriever(search_kwargs={"k": 2})
                    req_cases = generate_function_cases(st.session_state.llm, req["需求点"], retriviever=req_retrievers,
                                                        is_rag=True)
                    st.session_state.req_cases_list.extend(req_cases)
                    st.success("用例生成成功！")
        if len(st.session_state.req_cases_list) > 0:
            req_generated_cases = pd.DataFrame(st.session_state.req_cases_list)
            st.session_state.req_generated_cases=req_generated_cases
            req_generated_cases.rename(
                columns={"module": "功能模块", "case_id": "用例编号", "title": "标题", "priority": "优先级",
                         "preconditions": "前置条件", "steps": "测试步骤",
                         "expected": "预期结果"},
                inplace=True)
            st.divider()
            st.subheader("📑 生成用例列表")

            # 添加筛选功能
            req_selected_priority = st.multiselect(
                "按优先级筛选",
                options=["P0", "P1", "P2", "P3", "P4"],
                default=["P0", "P1", "P2", "P3", "P4"]
            )

            req_filtered_cases = st.session_state.req_generated_cases[
                st.session_state.req_generated_cases["优先级"].isin(req_selected_priority)
            ]
            st.dataframe(
                req_filtered_cases,
                use_container_width=True,
                height=400,
                hide_index=True
            )

# 测试用例生成页面
elif page == "🧪 智能测试用例生成":
    indexTab1, indexTab2 = st.tabs(["📝 测试用例生成", "📝 RAG知识库"])
    with indexTab1:
        with st.form("testcase_form"):
            requirement = st.text_area("需求描述", placeholder="示例：用户登录失败处理流程")
            with st.spinner("🎯 正在生成用例，请稍候...", show_time=True):
                agree = st.checkbox("📝 RAG增强")
                if st.form_submit_button("🎯 生成用例", type="primary") and len(requirement) > 0:
                    reqs = requirement
                    if agree:
                        st.session_state.logger.info("使用RAG增强")
                        retrievers = st.session_state.vector_db.as_retriever(search_kwargs={"k": 2})
                        cases = generate_function_cases(st.session_state.llm, reqs, retriviever=retrievers,
                                                        is_rag=True)
                    else:
                        cases = generate_function_cases(st.session_state.llm, reqs)
                    generated_cases = pd.DataFrame(cases)
                    generated_cases.rename(
                        columns={"module": "功能模块", "case_id": "用例编号", "title": "标题", "priority": "优先级",
                                 "preconditions": "前置条件", "steps": "测试步骤",
                                 "expected": "预期结果"},
                        inplace=True)
                    st.session_state.test_cases = generated_cases
        if not st.session_state.test_cases.empty:
            st.divider()
            st.subheader("📑 生成用例列表")

            # 添加筛选功能
            selected_priority = st.multiselect(
                "按优先级筛选",
                options=["P0", "P1", "P2", "P3", "P4"],
                default=["P0", "P1", "P2", "P3", "P4"]
            )

            filtered_cases = st.session_state.test_cases[
                st.session_state.test_cases["优先级"].isin(selected_priority)
            ]

            tab1, tab2 = st.tabs(["表格视图", "导出选项"])
            with tab1:
                st.dataframe(
                    filtered_cases,
                    use_container_width=True,
                    height=400,
                    hide_index=True
                )
            with tab2:
                export_format = st.radio(
                    "导出格式",
                    ["CSV", "Excel", "JSON"],
                    horizontal=True
                )
                if st.button(f"⬇️ 下载{export_format}文件"):
                    if export_format == "Excel":
                        pd.DataFrame(filtered_cases).to_excel("test_cases.xlsx", index=False)
                    elif export_format == "CSV":
                        pd.DataFrame(filtered_cases).to_csv("test_cases.csv", index=False)
                    else:
                        pd.DataFrame(filtered_cases).to_json("test_cases.json", index=False, force_ascii=False)
                    st.success(f"{export_format}文件已生成")

    with indexTab2:
        uploaded_file = st.file_uploader("Choose a file", type=["txt", "csv", "docx"],
                                         accept_multiple_files=False)
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
