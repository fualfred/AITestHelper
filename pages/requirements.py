#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

import pandas as pd
import streamlit as st
from utils.logger import get_logger
from utils.function_cases import generate_function_cases
from utils.parser import file_loader
from utils.requirements_analyze import analyze_requirement
from utils.utils import formate_reqs, generate_id

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
logger = get_logger()
# 初始化session state
if 'requirement_text' not in st.session_state:
    st.session_state.requirement_text = ""
if "req_generated_cases" not in st.session_state:
    st.session_state.req_generated_cases = pd.DataFrame()
if "req_cases_list" not in st.session_state:
    st.session_state.req_cases_list = []

logger.info(f"req_generated_cases:{st.session_state.req_generated_cases}")
BASE_PATH = st.session_state.base_path

st.subheader("📥 需求分析")
st.divider()
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
if st.session_state.requirement_text != "":
    st.divider()
    st.subheader("🔍 分析结果")
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
                # st.success("用例生成成功！")

req_generated_cases = pd.DataFrame(st.session_state.req_cases_list)
req_generated_cases.rename(
    columns={"module": "功能模块", "case_id": "用例编号", "title": "标题", "priority": "优先级",
             "preconditions": "前置条件", "steps": "测试步骤",
             "expected": "预期结果"},
    inplace=True)
st.session_state.req_generated_cases = req_generated_cases
if not st.session_state.req_generated_cases.empty:
    st.divider()
    st.subheader("📑 生成用例列表")
    # 添加筛选功能
    req_selected_priority = st.multiselect(
        "按优先级筛选",
        options=["P0", "P1", "P2", "P3", "P4"],
        default=["P0", "P1", "P2", "P3", "P4"]
    )
    # logger.info(f"筛选条件为{st.session_state.req_generated_cases}")
    req_filtered_cases = st.session_state.req_generated_cases[
        st.session_state.req_generated_cases["优先级"].isin(req_selected_priority)]
    tab1, tab2 = st.tabs(["表格视图", "导出选项"])
    with tab1:
        st.dataframe(
            req_filtered_cases,
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
        logger.info(f"导出格式为{export_format}")
        if st.button(f"⬇️ 下载{export_format}文件"):
            if export_format == "Excel":
                pd.DataFrame(req_filtered_cases).to_excel("test_cases.xlsx", index=False)
            elif export_format == "CSV":
                pd.DataFrame(req_filtered_cases).to_csv("test_cases.csv", index=False)
            else:
                pd.DataFrame(req_filtered_cases).to_json("test_cases.json", index=False, force_ascii=False)
            st.success(f"{export_format}文件已生成")
