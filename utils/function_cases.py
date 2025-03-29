#!/usr/bin/python
# -*- coding: utf-8 -*-
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config.settings import settings
from models.models import FunctionCaseList
from langchain_core.runnables import RunnablePassthrough

from utils.logger import get_logger

logger = get_logger()


def generate_function_cases(llm, requirement, retriviever=None, is_rag=False):
    try:
        parser = JsonOutputParser(pydantic_object=FunctionCaseList)

        if is_rag and retriviever:
            function_prompt_rag = PromptTemplate.from_template(settings.FUNCTION_PROMPT_RAG).partial(
                format_instructions=parser.get_format_instructions(), max_case_nums=settings.MAX_CASE_NUM)
            chain = {"context": retriviever,
                     "requirement": RunnablePassthrough()} | function_prompt_rag | llm | parser
            result = chain.invoke(requirement)
        else:
            function_prompt = PromptTemplate.from_template(
                settings.FUNCTION_PROMPT
            ).partial(format_instructions=parser.get_format_instructions(), max_case_nums=settings.MAX_CASE_NUM)
            chain = function_prompt | llm | parser
            result = chain.invoke({"requirement": requirement})
        logger.info(f"测试用例是{result}")
        # format_result = FunctionCaseList.model_dump(result)
        cases_list = result["cases"]
        for case in cases_list:
            case["steps"] = "\n".join(case["steps"])
            case["expected"] = "\n".join(case["expected"])
        return cases_list
    except Exception as e:
        logger.error(f"生成测试用例异常{str(e)}")
        print(str(e))


if __name__ == "__main__":
    pass
    # cases = generate_function_cases("计算两个数的和")
    # import pandas as pd
    #
    # df = pd.DataFrame(cases)
    # df.rename(columns={"priority": "优先级"})
    # print(df)
    # print(df["priority"].isin(["P0", "P1", "P2"]))
    #
    # llm = ChatOpenAI(api_key=os.getenv("TENCENT_API_KEY"),
    #                  base_url=os.getenv("TENCENT_BASE_URL"), model=settings.MODEL, temperature=0.6)

    # print(os.getenv("BASE_URL"))
    # llm = ChatOllama(base_url="http://127.0.0.1:11434", model="deepseek-r1:8b", temperature=0.6)
    # print(llm.invoke("你好"))
    # prompt = ChatPromptTemplate.from_messages(
    #     [("system", "你是一个世界级的专家"), ("user", "{input}")]
    # )
    # chain = prompt | llm
    # result = chain.invoke({"input": "请你帮我写一篇ai的文章 20个字"})
    # print(result)
