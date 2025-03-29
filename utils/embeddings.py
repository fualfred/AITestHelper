#!/usr/bin/python
# -*- coding: utf-8 -*-
from langchain_ollama import OllamaEmbeddings
import os
from langchain_chroma import Chroma
from config.settings import settings

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
embeddings = OllamaEmbeddings(
    model="nomic-embed-text:latest"
)


def get_embeddings():
    return embeddings


def create_vector_db():
    return Chroma(embedding_function=embeddings, persist_directory=settings.VECTOR_STORE_DIR)


def create_vector_db_from_texts(texts):
    return Chroma.from_texts(texts=texts, embedding=embeddings, persist_directory=settings.VECTOR_STORE_DIR,
                             collection_metadata={"hnsw:dimension": 768})


def create_vector_db_from_docs(docs):
    return Chroma.from_documents(docs=docs, embedding=embeddings, persist_directory=settings.VECTOR_STORE_DIR,
                                 collection_metadata={"hnsw:dimension": 768})


if __name__ == '__main__':
    pass
    # vector_db =create_vector_db()
    # # print(vector_db)
    # vector_db.add_texts(["1111"])
    # vector_db
    # print(vector_db.get(["1111"]))