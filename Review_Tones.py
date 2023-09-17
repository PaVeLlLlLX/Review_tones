# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GbIF1ng1wU7zvBGbA14RjFzA0DHF2mFz
"""

import pandas as pd
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
np.set_printoptions(threshold=20)

table = pd.read_excel("doc_comment_summary.xlsx", header= None)
table = table.dropna() # Можно не использовать, так как drop() все равно уберет пропуски из-за их типа NaN
table = table.drop(table[(table[1] == 0) | (table[1].apply(type)!=int) | (table[0].apply(type)!=str)].index, axis=0)
table[2] = (table[1] > 0).astype(bool)
train, test = train_test_split(table, test_size= 0.2, random_state = 22)
for sample in [train, test]:
  print(sample.shape[0]) # Количество строк в каждой выборке
  print(sample[sample[2] == 1].shape[0] / sample.shape[0]) # Видно, что доля положительных комментариев в тестовой и тренировочной выборках близки, данные распределены равномерно

pipeline_base = Pipeline([
  ("vect", TfidfVectorizer()),
  ("clf", LogisticRegression(random_state=123)), # Воспользуемся логистической регрессией
  ], verbose = True)
Y_train = train[2].astype('float')
Y_test = test[2].astype('float')


param = {'clf__penalty': ['l1','l2'],
        'clf__C': [1.0, 5, 10],
        'clf__solver': ['lbfgs', 'liblinear'],
        'clf__max_iter': [25, 50, 100],
         'vect__ngram_range': [(1,1),(2,2)],
          'vect__max_df': [0.5, 1],
        } # Подбираемые параметры логистической регрессии и извлекателя признаков

grid = GridSearchCV(estimator=pipeline_base,
            param_grid= param,
            cv=3,
            scoring= 'accuracy', # Вывод метрики 
            verbose = 3 ) # Вывод большего количества информации в процессе обучения

"""

# Базовая Модель без подбора параметров
"""

pipeline_base.fit(train[0], Y_train) # Обучение без подбора параметров
result_proba = pipeline_base.predict_proba(test[0]) # Массив вероятностей тональности в каждой строке
result = pipeline_base.predict(test[0]) # Массив предсказанных тональностей

accuracy_score(Y_test, result) # Метрика правильности без подбора параметров

"""# Модель с подбираемыми параметрами"""

grid.fit(train[0], Y_train) # Обучение с лучшими параметрами

grid.best_params_

result_with_grid = grid.predict(test[0]) # Массив предсказанных тональностей с лучшими параметрами
accuracy_score(Y_test, result_with_grid) # И лучшая метрика правильности

"""#Итоги: Таблица со всеми параметрами и вывод лучшего набора

"""

Result_table = pd.DataFrame(grid.cv_results_).drop(['mean_fit_time','mean_score_time','std_score_time','std_test_score','rank_test_score','split0_test_score','split1_test_score','split2_test_score'], axis=1)
Result_table

Result_table[Result_table['mean_test_score'] == Result_table['mean_test_score'].max()] # Вывод лучшего набора

"""Значение метрики, если модель всегда возвращала бы негативную оценку"""

only_neg = Y_test.copy()
only_neg[only_neg >= 0] = 0.0 
accuracy_score(Y_test, only_neg)