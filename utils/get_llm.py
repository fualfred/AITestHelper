#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_deepseek import ChatDeepSeek

from config.settings import settings
from dotenv import load_dotenv

load_dotenv()


def get_llm(company):
    if company == "tencent":
        llm = ChatOpenAI(api_key=os.getenv("TENCENT_API_KEY"),
                         base_url=os.getenv("TENCENT_BASE_URL"), model=settings.MODEL, temperature=0.6, max_tokens=1000)
    elif company == "ollama":
        llm = ChatOllama(base_url=os.getenv("OLLAMA_BASE_URL"), model="deepseek-r1:8b", temperature=0.6)
    elif company == "deepseek":
        llm = ChatDeepSeek(model="deepseek-chat", temperature=1, max_tokens=1000)
    else:
        raise ValueError("Invalid company name")
    return llm


if __name__ == '__main__':
    pass
    # print(get_llm("deepseek"))
