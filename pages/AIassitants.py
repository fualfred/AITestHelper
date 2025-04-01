#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import re
import streamlit as st
import random
import time
from myAgent.my_agent import TestAgent
from utils.parser import file_loader
import pandas as pd
from utils.logger import get_logger

# 初始化

st.session_state.agent = TestAgent()
BASE_PATH = st.session_state.base_path
logger = get_logger()
st.subheader("🤖AI测试助手")
st.divider()


def dataframe_stream_generator(df, chunk_size=5):
    """
    流式生成DataFrame分块
    参数:
        df (pd.DataFrame): 原始数据集
        chunk_size (int): 每批加载行数
    """
    total = len(df)

    # 先输出表头
    # yield df.head(0).to_markdown(index=False) + "\n"

    # 分块加载数据
    for i in range(0, total, chunk_size):
        chunk = df.iloc[i:i + chunk_size]

        # 转换为Markdown表格（带进度）
        md_table = chunk.to_markdown(index=False) + f"\n\n**已加载 {min(i + chunk_size, total)}/{total} 行**"

        yield md_table
        time.sleep(0.1)  # 控制加载速


if "firstTimeChat" not in st.session_state:
    st.session_state.firstTimeChat = True
if "downcases" not in st.session_state:
    st.session_state.downcases = pd.DataFrame()

if "processed" not in st.session_state:
    st.session_state.processed = False

if "agentcases" not in st.session_state:
    st.session_state.agentcases = pd.DataFrame()
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": st.session_state.agent.welcome_message})
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
prompt = st.chat_input("What is up?", accept_file=True, file_type=["txt", "csv", "docx"])

if prompt:
    # Add user message to chat history
    if prompt and prompt["files"]:
        file = prompt['files'][0]
        file_name = file.name
        with open(f"{BASE_PATH}/aiAgentDocs/{file_name}", "wb") as f:
            f.write(file.getvalue())
        texts, splits, metadatas = file_loader(f"{BASE_PATH}/aiAgentDocs/{file_name}")
        prompt_send = "".join(texts)
        prompt = f"已上传文件📃{file_name}"
    else:
        prompt = prompt.text
        prompt_send = prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container

    with st.chat_message("assistant"):
        with st.spinner('🤖AI助手正在思考中...', show_time=True):
            if st.session_state.firstTimeChat:
                response = st.session_state.agent.gernerate_test_cases(prompt_send)
                st.session_state.firstTimeChat = False
            else:
                response = st.session_state.agent.rag_test_cases(prompt_send)
            clean_response = response.replace("json", "").replace("```", "").strip()
            logger.info(f"clean_response:{clean_response}")
            response = json.loads(clean_response)
            if "status" not in response:
                cases = response["cases"]
                logger.info(f"cases:{cases}")
                agent_case = pd.DataFrame(cases)
                agent_case.rename(
                    columns={"case_id": "用例编号", "module": "功能模块", "title": "标题", "preconditions": "前置条件",
                             "priority": "优先级",
                             "steps": "测试步骤",
                             "expected": "预期结果"},
                    inplace=True)
        if "status" not in response:
            st.session_state.agentcases = agent_case

            response_str = st.write_stream(dataframe_stream_generator(st.session_state.agentcases, chunk_size=100))
            st.session_state.processed = True
        else:
            response_str = st.write_stream(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_str})

if st.session_state.downcases.empty:
    st.session_state.downcases = st.session_state.agentcases
else:
    st.session_state.downcases = pd.concat([st.session_state.downcases, st.session_state.agentcases])
if st.session_state.processed:
    if st.button("⬇️下载用例"):
        logger.info("下载用例")
        pd.DataFrame(st.session_state.downcases).to_excel("test_cases.xlsx", index=False)
        st.session_state.processed = False
