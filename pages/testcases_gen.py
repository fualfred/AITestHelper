#!/usr/bin/python
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

from utils.function_cases import generate_function_cases
from utils.logger import logger

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
if 'test_cases' not in st.session_state:
    st.session_state.test_cases = pd.DataFrame()
st.subheader("🎯用例生成")
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
        logger.info(f"导出格式为{export_format}")
        if st.button(f"⬇️ 下载{export_format}文件"):
            if export_format == "Excel":
                pd.DataFrame(filtered_cases).to_excel("test_cases.xlsx", index=False)
            elif export_format == "CSV":
                pd.DataFrame(filtered_cases).to_csv("test_cases.csv", index=False)
            else:
                pd.DataFrame(filtered_cases).to_json("test_cases.json", index=False, force_ascii=False)
            st.success(f"{export_format}文件已生成")
