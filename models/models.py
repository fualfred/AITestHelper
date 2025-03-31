#!/usr/bin/python
# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import List,Dict
from config.settings import settings
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

engine = create_engine(f"sqlite:///{settings.DB_PATH}")
local_session = sessionmaker(bind=engine)
def get_db_session():
    return local_session()


class FunctionCase(BaseModel):
    module: str = Field(..., description="功能模块")
    case_id: str = Field(..., description="用例编号")
    title: str = Field(..., description="测试用例标题")
    priority: str = Field(ge="P0", le="P4", description="优先级")
    preconditions: str = Field(..., description="前置条件")
    steps: List[str] = Field(..., min_items=1, description="测试步骤")
    expected: List[str] = Field(..., min_items=1, description="预期结果")
class AgentFunctionCase(BaseModel):
    module: str = Field(..., description="功能模块")
    case_id: str = Field(..., description="用例编号")
    title: str = Field(..., description="测试用例标题")
    priority: str = Field(ge="P0", le="P4", description="优先级")
    preconditions: str = Field(..., description="前置条件")
    steps: str = Field(..., min_items=1, description="测试步骤")
    expected: str = Field(..., min_items=1, description="预期结果")
class AgentFunctionCaseList(BaseModel):
    cases: List[AgentFunctionCase] = Field(..., min_items=2)
class FunctionCaseList(BaseModel):
    cases: List[FunctionCase] = Field(..., min_items=2, max_items=settings.MAX_CASE_NUM,
                                      description=f"测试用例，最多生成{settings.MAX_CASE_NUM}条")
class Requirement(BaseModel):
    functional: List[str] = Field(..., min_items=1, description="功能需求")
    non_functional: List[str]=Field(..., min_items=1, description="非功能需求")


class RagFileRecord(Base):
    __tablename__ = 'rag_file_record'
    id = Column(Integer, autoincrement=True, primary_key=True)
    file_name = Column(String(255), nullable=False)
    ids = Column(String(255), nullable=False)

if __name__ == '__main__':
    pass
    # Base.metadata.create_all(engine)