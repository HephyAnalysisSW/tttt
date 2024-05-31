import keras
from sklearn.model_selection import train_test_split
import uproot
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import awkward as ak
seed_value= 0

import random
random.seed(seed_value)
np.random.seed(seed_value)

import pandas as pd
from copy import deepcopy
from sklearn.utils import shuffle


# filename = "/eos/vbc/group/cms/cristina.giordano/tttt/dataFrameAllTT.csv"
filename = "/eos/vbc/group/cms/cristina.giordano/tttt/dataFrameAllTTHad50.csv"
# filename = "../../dataFrame300.csv"

data = pd.read_csv(filename)
# data['TopTruth'] = 1 - data['TopTruth']

class_0 = data[data['TopTruth'] == 0]
class_1 = data[data['TopTruth'] == 1]

class_0_subset = class_0.sample(n=len(class_1), random_state=42)

balanced_data = pd.concat([class_0_subset, class_1])
balanced_data = shuffle(balanced_data, random_state=42)


data_copy = deepcopy(balanced_data)
X = balanced_data.drop(columns=['TopTruth'])
print(X.head())
Y = data_copy['TopTruth']
print(Y.head())

print("Shape of X (TTTT):", X.shape)
print("Shape of Y (TTTT):", Y.shape)


X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

from sklearn.preprocessing import RobustScaler
scalerR = RobustScaler()
X_train_scaledR = scalerR.fit_transform(X_train)
X_test_scaledR = scalerR.transform(X_test)


from keras.layers import Dense, Dropout
from keras.models import Sequential
# print(keras.__version__)
# from keras
import tensorflow as tf
model = Sequential()

model.add(Dense(64, input_dim=X_train_scaledR.shape[1], activation='relu'))  # 64 relu
model.add(Dropout(0.2))
model.add(Dense(32, activation='relu'))  # 32 relu
model.add(Dense(1, activation='sigmoid'))  # sigmoid

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

model.summary()



import h5py

from keras.models import load_model

myModel = load_model('classifierModel_v3.h5')

# history = myModel.history

Y_pred = myModel.predict(X_test_scaledR).ravel()
# print(Y_pred)


from sklearn.metrics import roc_curve, auc

fpr, tpr, thresholds = roc_curve(Y_test, Y_pred)
roc_auc = auc(fpr, tpr)

# Plot ROC curve
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate', fontsize=15)
plt.ylabel('True Positive Rate', fontsize=15)
# plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")
plt.grid(True)
plt.savefig("ROC_DNN_TTHad_v3.png")
plt.clf()



plt.figure(figsize=(8, 6))
plt.hist(Y_pred[Y_test == 0], bins=30, color='skyblue', alpha=0.7, label='Class 0')
plt.hist(Y_pred[Y_test == 1], bins=30, color='salmon', alpha=0.7, label='Class 1')
plt.xlabel('Predicted Score')
plt.ylabel('Frequency')
plt.title('Score Distribution')
plt.legend()
plt.grid(True)
plt.savefig("scorePlot_TTHad_v3.png")
plt.clf()
