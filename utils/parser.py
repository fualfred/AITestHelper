#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from langchain_community.document_loaders import TextLoader, CSVLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def file_loader(file_path):
    if file_path.endswith(".txt"):
        loader = TextLoader(file_path, autodetect_encoding=True)
    elif file_path.endswith(".csv"):
        loader = CSVLoader(file_path, autodetect_encoding=True)
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError("Unsupported file format")
    docs = loader.load()
    # 文本分块
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    splits = text_splitter.split_documents(docs)

    # 提取纯文本
    texts = [doc.page_content for doc in splits]
    metadatas = [doc.metadata for doc in splits]

    return texts, splits, metadatas


if __name__ == "__main__":
    pass
    # path = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/requirements/注册和登录系统需求说明.txt"
    # texts, splits, metadatas = file_loader(path)
    # print(metadatas)
