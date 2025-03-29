#!/usr/bin/python
# -*- coding: utf-8 -*-
import os


class Settings:
    MODEL = "deepseek-r1"
    COMPANY = "tencent"  # deepseek/ollama/tencent
    MAX_CASE_NUM = 10
    DB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/aiTest.db"
    VECTOR_STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    "vector_store")
    FUNCTION_PROMPT = """作为测试专家，请为以下需求生成最多{max_case_nums}个测试用例：
    需求描述：
    {requirement}
    
    请严格按照JSON格式生成测试用例列表
    
    每条测试用例包含的属性：
   - 用例编号（格式TC-模块-序号，如TC-LOGIN-01）
   - 功能模块
   - 用例标题（简明描述测试目的）
   - 前置条件
   - 步骤（简明步骤描述  1.步骤1描述 2.步骤2描述）
   - 预期（预期结果  - 结果1（对应步骤1）结果2（对应步骤2））
   - 优先级（P0-P4，P0为最高）
    
    格式要求:
    {format_instructions}
    
    返回示例参考：
        {{
            "cases": [
                    {{
                       "case_id": "TC-LOGIN-01",
                        "module": "登录",
                        "title": "登录成功",
                        "preconditions": "用户名和密码正确",
                        "steps": ["1. 输入正确的用户名和密码", "2. 点击登录按钮"],
                        "expected": ["1.登录成功","2.跳转到首页"],
                        "priority": "P0",    
                    }},
                    {{
                       "case_id": "TC-LOGIN-02",
                        "module": "登录",
                        "title": "登录失败",
                        "preconditions": "用户名正确，密码错误",
                        "steps": ["1. 输入用户名和密码","2. 点击登录按钮"],
                        "expected": ["1.登录失败，提示帐号或密码错误","2.停留在登录页面"],
                        "priority": "P1",    
                    }}
        
                ],
        }}
    """
    FUNCTION_PROMPT_RAG = """作为测试专家，请为以下需求生成最多{max_case_nums}个测试用例：
        先参考到的内容
        {context}
        
        需求描述：
        {requirement}

        请严格按照JSON格式生成测试用例列表

        每条测试用例包含的属性：
       - 用例编号（格式TC-模块-序号，如TC-LOGIN-01）
       - 功能模块
       - 用例标题（简明描述测试目的）
       - 前置条件
       - 步骤（简明步骤描述  1.步骤1描述 2.步骤2描述）
       - 预期（预期结果  - 结果1（对应步骤1）结果2（对应步骤2））
       - 优先级（P0-P4，P0为最高）

        格式要求:
        {format_instructions}

        返回示例参考：
            {{
                "cases": [
                        {{
                           "case_id": "TC-LOGIN-01",
                            "module": "登录",
                            "title": "登录成功",
                            "preconditions": "用户名和密码正确",
                            "steps": ["1. 输入正确的用户名和密码", "2. 点击登录按钮"],
                            "expected": ["1.登录成功","2.跳转到首页"],
                            "priority": "P0",    
                        }},
                        {{
                           "case_id": "TC-LOGIN-02",
                            "module": "登录",
                            "title": "登录失败",
                            "preconditions": "用户名正确，密码错误",
                            "steps": ["1. 输入用户名和密码","2. 点击登录按钮"],
                            "expected": ["1.登录失败，提示帐号或密码错误","2.停留在登录页面"],
                            "priority": "P1",    
                        }}

                    ],
            }}
        """
    REQUIREMENT_PROMPT = """
    你是一个专业的需求分析师，请从以下文档内容中提取结构化需求：
    {format_instructions}
    
    文档内容：
    {context}
    
    输出要求：
    - 功能需求需包含动词短语
    - 非功能需求需包含性能指标
    - 干系人需明确角色名称
    - 优先级分类使用 High/Medium/Low
    """


settings = Settings()
