#!/usr/bin/python
# -*- coding: utf-8 -*-
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config.settings import settings
from models.models import Requirement
from utils.logger import get_logger

logger = get_logger()


def analyze_requirement(llm, requirement):
    try:
        parser = JsonOutputParser(pydantic_object=Requirement)
        requirement_prompt = PromptTemplate.from_template(settings.REQUIREMENT_PROMPT).partial(
            format_instructions=parser.get_format_instructions())
        chain = requirement_prompt | llm | parser
        result = chain.invoke(requirement)
        return result
    except Exception as e:
        logger.debug(f"解析需求失败{str(e)}")

