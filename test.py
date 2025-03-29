#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import streamlit as st

# s = st.text_area("请输入你的需求", height=200)
# if st.button("生成"):
#     print(s)
#     st.write(f"你输入的内容是：{type(s)}")
#
# corpus = [
#     'This is the first document.',
#     'This is the this second second document.',
#     'And the third one.',
#     'Is this the first document?'
# ]
# vectorizer = CountVectorizer()
# print(vectorizer)
# X = vectorizer.fit_transform(corpus)
# print(X)
# print(vectorizer.get_feature_names_out())
# print(X.toarray())
# vectorizer = TfidfVectorizer()
# x = vectorizer.fit_transform(corpus)
# print('feature', vectorizer.get_feature_names_out(corpus))
# print(x.toarray())

reqs = {
    'functional': ['支持用户名、密码注册', '支持邮箱验证', '支持手机绑定', '支持用户名唯一性校验', '支持密码强度检测',
                   '支持图形验证码机制'], 'non_functional': ['账户安全性与用户身份真实性验证成功率不低于99.9%']}
# df = pd.DataFrame(reqs)
# print(df)
functional = reqs['functional']
non_functional = reqs['non_functional']
functional_all = []
for item in functional:
    functional_all.append({"类型": "功能需求", "需求点": item, "操作": "11"})
for item in non_functional:
    functional_all.append({"类型": "非功能需求", "需求点": item, "操作": "11"})

print(pd.DataFrame(functional_all))
