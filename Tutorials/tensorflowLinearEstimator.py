# -*- coding: utf-8 -*-
"""
This code is taken from Tensorflow tutorials. I added in some cross feature columns to improve the 
accuracy to around 80%. This is my first look at using Estimators.

Link to tutorial: https://www.tensorflow.org/tutorials/estimator/linear
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import clear_output
from six.moves import urllib
import tensorflow as tf
import os
import sys
from sklearn.metrics import roc_curve


# Load dataset.
dftrain = pd.read_csv('https://storage.googleapis.com/tf-datasets/titanic/train.csv') # training data
dfeval = pd.read_csv('https://storage.googleapis.com/tf-datasets/titanic/eval.csv') # testing data
y_train = dftrain.pop('survived')
y_eval = dfeval.pop('survived')

# below is for visualizing some of the data using plots
# dftrain.age.hist(bins=20)
# dftrain.sex.value_counts().plot(kind='barh')
# dftrain['sex'].value_counts().plot(kind='barh')
# dftrain['class'].value_counts().plot(kind='barh')
# pd.concat([dftrain, y_train], axis=1).groupby('sex').survived.mean().plot(kind='barh').set_xlabel('% survive')

# below are the column headers for categorical (string) and numeric columns
CATEGORICAL_COLUMNS = ['sex', 'n_siblings_spouses', 'parch', 'class', 'deck',
                       'embark_town', 'alone']
NUMERIC_COLUMNS = ['age', 'fare']

# creates the feature columns
feature_columns = []
for feature_name in CATEGORICAL_COLUMNS:
  vocabulary = dftrain[feature_name].unique()  # gets a list of all unique values from given feature column
  feature_columns.append(tf.feature_column.categorical_column_with_vocabulary_list(feature_name, vocabulary))
for feature_name in NUMERIC_COLUMNS:
  feature_columns.append(tf.feature_column.numeric_column(feature_name, dtype=tf.float32))
# print(feature_columns[0])

def make_input_fn(data_df, label_df, num_epochs=10, shuffle=True, batch_size=32):
  """returns the bottom function for a reusable input function, format from tensorflow website"""
  def input_function():  # inner function, this will be returned
    """standard input function for models"""
    ds = tf.data.Dataset.from_tensor_slices((dict(data_df), label_df))  # create tf.data.Dataset object with data and its label
    if shuffle:
      ds = ds.shuffle(1000)  # randomize order of data
    ds = ds.batch(batch_size).repeat(num_epochs)  # split dataset into batches of 32 and repeat process for number of epochs
    return ds  # return a batch of the dataset
  return input_function  # return a function object for use

# creates input functions for model
train_input_fn = make_input_fn(dftrain, y_train)  # here we will call the input_function that was returned to us to get a dataset object we can feed to the model
eval_input_fn = make_input_fn(dfeval, y_eval, num_epochs=1, shuffle=False)

# shows the features and labels
ds = make_input_fn(dftrain, y_train, batch_size=10)()
for feature_batch, label_batch in ds.take(3): #input is number of batches to display
  print('Some feature keys:', list(feature_batch.keys()))
  print()
  print('A batch of class:', feature_batch['class'].numpy())
  print()
  print('A batch of Labels:', label_batch.numpy())

# Creates model without crossed columns
linear_est = tf.estimator.LinearClassifier(feature_columns=feature_columns)
# Trains model
linear_est.train(train_input_fn)  # train
# Tests model
result = linear_est.evaluate(eval_input_fn)  # get model metrics/stats by testing on tetsing data
clear_output()  # clears console output
print()
print(result['accuracy'])  # the result variable is simply a dict of stats about our model
print()
# print(result)


# crossed columns 
age_x_gender = tf.feature_column.crossed_column(['age', 'sex'], hash_bucket_size=100)
class_x_numberSiblingsSpouses = tf.feature_column.crossed_column(['class', 'n_siblings_spouses'], hash_bucket_size=100)
class_x_deck = tf.feature_column.crossed_column(['class', 'deck'], hash_bucket_size=100)
alone_x_class = tf.feature_column.crossed_column(['alone', 'class'], hash_bucket_size=100)
parch_x_class = tf.feature_column.crossed_column(['parch', 'class'], hash_bucket_size=100)
alone_x_age = tf.feature_column.crossed_column(['alone', 'age'], hash_bucket_size=100)
parch_x_alone = tf.feature_column.crossed_column(['parch', 'alone'], hash_bucket_size=100)
parch_x_numberSiblingsSpouses = tf.feature_column.crossed_column(['parch', 'n_siblings_spouses'], hash_bucket_size=100)
fare_x_class = tf.feature_column.crossed_column(['fare', 'class'], hash_bucket_size=100)
alone_x_gender = tf.feature_column.crossed_column(['alone', 'sex'], hash_bucket_size=100)
derived_feature_columns = [age_x_gender, class_x_numberSiblingsSpouses, 
                           class_x_deck, alone_x_class, parch_x_class, 
                           alone_x_age, parch_x_alone, parch_x_numberSiblingsSpouses,
                           fare_x_class, alone_x_gender]
# Creates model with crossed columns
linear_est = tf.estimator.LinearClassifier(feature_columns=feature_columns+derived_feature_columns)
# Trains model
linear_est.train(train_input_fn)
#Tests model 
result = linear_est.evaluate(eval_input_fn)
clear_output()
print(result)
print(result['accuracy'])
print()

# some code to show prediction results
pred_dicts = list(linear_est.predict(eval_input_fn)) #makes this a list because generators can't be looked at
# print(pred_dicts)
probs = pd.Series([pred['probabilities'][1] for pred in pred_dicts])
probs.plot(kind='hist', bins=20, title='predicted probabilities')
# some code to look at the test data compared to prediction
print(dfeval.loc[0])
print(y_eval.loc[0])
print('Died',pred_dicts[0]['probabilities'][0]) #died
print('Lived',pred_dicts[0]['probabilities'][1]) #survived


