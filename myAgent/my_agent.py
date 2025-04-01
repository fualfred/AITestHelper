#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import Tool, AgentExecutor
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser

from utils.get_llm import get_llm
from langchain.memory import ConversationSummaryMemory
from utils.embeddings import create_vector_db
from models.models import AgentFunctionCaseList
from utils.logger import get_logger
from typing import Optional, Dict
from langchain_community.chat_message_histories import ChatMessageHistory
from config.settings import settings

logger = get_logger()


def knowledge_retrieval(retriever, query):
    """测试工具  上传到RAG的知识库 CSV格式：用例ID,场景,步骤,预期结果等"""
    docs = retriever.invoke(query)
    return "\n\n".join([
        f"参考条目 {doc.page_content[:200]}..."
        for doc in docs
    ])


class TestAgent:
    def __init__(self):
        self.welcome_message = """
                🎉 欢迎使用智能测试设计助手！我是您的AI测试小伙伴，请输入需求描述或者发送需求文档给我哦！
                1. 根据需求生成结构化测试用例
                2. 从知识库检索相似测试场景
                3. 提供测试设计最佳实践建议
                您可以像这样开始：
                "为登录功能设计测试用例"
                "需要性能测试场景"
                """
        self.llm = self._init_llm(settings.COMPANY)
        self.memory = self._init_memory()
        self.retriever = self._init_retriever()
        self.tools = self._init_tools()
        self.output_parser = self._output_parser()
        self.agent_executor = self._build_agent_chain()

    def _init_llm(self, company):
        return get_llm(company)

    def _init_memory(self) -> ConversationSummaryMemory:
        return ConversationSummaryMemory(llm=self.llm, chat_memory=ChatMessageHistory(), return_messages=True)

    def _init_retriever(self):
        return create_vector_db().as_retriever(search_kwargs={"k": 2})

    def _init_tools(self):
        tools = []
        if self.retriever:
            tools.append(Tool(
                name="TestKnowledgeBase",
                func=knowledge_retrieval,
                description="""
        访问测试知识库获取历史用例，输入应为自然语言查询，例如：
        '登录功能的边界测试场景'
        """))
        return tools

    def _build_agent_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("placeholder", "{history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        agent_chain = {
                          "input": lambda x: x["input"],
                          "history": lambda x: x.get("history", []),
                          "agent_scratchpad": lambda x: x["intermediate_steps"]
                      } | prompt | self.llm | self.output_parser
        return AgentExecutor(
            agent=agent_chain,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )

    def _get_system_prompt(self):
        return settings.AGENT_PROMPT

    def _output_parser(self):
        return OpenAIFunctionsAgentOutputParser(pydantic_object=AgentFunctionCaseList)

    def _retriver_knowledge(self, query):
        if self.retriever:
            docs = self.retriever.invoke(query)
            return "\n".join([
                f"[知识条目 {doc.page_content[:200]}..."
                for doc in docs
            ])

    def reset_memery(self):
        self.memory.clear()

    def update_knowlege(self, vector_db, docs):
        vector_db.add_documents(docs)

    def gernerate_test_cases(self, query, context: Optional[str] =

    None) -> Dict:
        """
        生成测试用例
        :param query: 用户需求描述
        :param context: 附加上下文信息
        :return: 数据的字典
        """
        try:
            retriever = self._retriver_knowledge(query)
            full_query = f"需求：{query}\n上下文{context or ''}\n知识库：{retriever}"
            logger.info(f"测试用例生成请求：{full_query}")
            response = self.agent_executor.invoke({"input": full_query})
            logger.info(f"llm返回的数据：{response}")
            logger.info(f"测试用例生成结果：{response['output']}")
            return response['output']
        except Exception as e:
            logger.error(f"测试用例生成异常：{e}")
            return {
                "status": "error",
                "message": str(e),
                "suggestion": "请检查输入格式或重试"
            }

    def rag_test_cases(self, query, context: Optional[str] = None) -> Dict:
        try:
            full_query = f"请你根据以下意见进行更新：{query}"
            logger.info(f"测试用例生成请求：{full_query}")
            response = self.agent_executor.invoke({"input": full_query})
            logger.info(f"llm返回的数据：{response}")
            logger.info(f"测试用例生成结果：{response['output']}")
            return response['output']
        except Exception as e:
            logger.error(f"测试用例生成异常：{e}")
            return {
                "status": "error",
                "message": str(e),
                "suggestion": "请检查输入格式或重试"
            }


if __name__ == "__main__":
    pass
    # pass
    # 测试用例生成
    # agent = TestAgent()
    # # print(agent)
    # print("first")
    # print("check memory")
    # print(agent.memory.load_memory_variables({}))
    # result = agent.gernerate_test_cases("登录注册功能")
    # print(result)
    # print("update")
    # result2 = agent.rag_test_cases('增加安全相关的用例')
    # print(result2)
    # print("check memory")
    # print(agent.memory.load_memory_variables({}))
