import uproot
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import keras
from sklearn.model_selection import train_test_split
import random
seed_value= 0
random.seed(seed_value)
np.random.seed(seed_value)
from copy import deepcopy
from sklearn.utils import shuffle
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_curve, f1_score


import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
# argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='')
argParser.add_argument('--plotPath', action='store', nargs='?', default="/groups/hephy/cms/cristina.giordano/www/TruthStudies/plots/v12/RunII", help="where to write the plots" )
argParser.add_argument('--selection', action='store', default='trilep')
# argParser.add_argument('--sample', action='store', default='TTTT')
args = argParser.parse_args()

# filename = "../../dataFrame300.csv"
# filename = "/eos/vbc/group/cms/cristina.giordano/tttt/dataFrameAllTTTT.csv"
file2016_preVFP = "/eos/vbc/group/cms/cristina.giordano/tttt/dataFrame_TTTT_UL2016_preVFP_"+args.selection+".csv"
file2016 = "/eos/vbc/group/cms/cristina.giordano/tttt/dataFrame_TTTT_UL2016_"+args.selection+".csv"
file2017 = "/eos/vbc/group/cms/cristina.giordano/tttt/dataFrame_TTTT_UL2017_"+args.selection+".csv"
file2018 = "/eos/vbc/group/cms/cristina.giordano/tttt/dataFrame_TTTT_UL2018_"+args.selection+".csv"
filename = "/eos/vbc/group/cms/cristina.giordano/tttt/dataFrameOld/dataFrameAllTTTT_trilep.csv"
# filenameTTbar = "../../dataFrameTTHad/dataFrame5TTHad.csv"
# run2 = [file2016_preVFP, file2016, file2017, file2018]
run2 = [filename]
all_files = pd.concat([pd.read_csv(f) for f in run2])

data = all_files


class_1 = data[data['TopTruth'] == 1]
class_0 = data[data['TopTruth'] == 0]

class_0_subset = class_0.sample(n=len(class_1), random_state=42)

balanced_data = pd.concat([class_0_subset, class_1])
balanced_data = shuffle(balanced_data, random_state=42)

data_copy = deepcopy(balanced_data)
X = balanced_data.drop(columns=['TopTruth'])
# print(X.head())
Y = data_copy['TopTruth']
# print(Y.head())

print("Shape of X (TTTT):", X.shape)
print("Shape of Y (TTTT):", Y.shape)

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
X_train, X_val, Y_train, Y_val = train_test_split(X_train, Y_train, test_size=0.25, random_state=42)


from sklearn.preprocessing import RobustScaler

# Scaler (standard vs robust???)
scalerR = RobustScaler()

X_train_scaledR = scalerR.fit_transform(X_train)
X_test_scaledR = scalerR.transform(X_test)
X_val_scaledR = scalerR.fit_transform(X_val)


import tensorflow as tf
from keras.layers import Dense, Dropout
from keras.models import Sequential
import keras.backend as K

def focal_loss(alpha=0.25, gamma=2.0):
    def focal_loss_fixed(y_true, y_pred):
        epsilon = K.epsilon()
        y_pred = K.clip(y_pred, epsilon, 1.0 - epsilon)
        y_true = K.cast(y_true, K.floatx())

        alpha_t = y_true * alpha + (K.ones_like(y_true) - y_true) * (1 - alpha)
        p_t = y_true * y_pred + (K.ones_like(y_true) - y_true) * (1 - y_pred)
        fl = - alpha_t * K.pow((K.ones_like(y_true) - p_t), gamma) * K.log(p_t)

        return K.mean(fl)
    return focal_loss_fixed


# from keras
model = Sequential()

model.add(Dense(64, input_dim=X_train_scaledR.shape[1], activation='relu'))  # 64 relu
model.add(Dropout(0.2))
model.add(Dense(32, activation='relu'))  # 32 relu
model.add(Dropout(0.2))
model.add(Dense(1, activation='sigmoid'))  # sigmoid

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

model.summary()


callback_ = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3)

history = model.fit(X_train_scaledR, Y_train, epochs=20, batch_size=32, validation_split=0.2, callbacks=[callback_])

loss, accuracy = model.evaluate(X_test_scaledR, Y_test)

Y_val_pred_prob = model.predict(X_val_scaledR)

# Find the optimal threshold
precision, recall, thresholds = precision_recall_curve(Y_val, Y_val_pred_prob)
f1_scores = 2 * (precision * recall) / (precision + recall)
optimal_threshold = thresholds[np.argmax(f1_scores)]

print('Optimal threshold: {}'.format(optimal_threshold))

# Predict on test data using the optimal threshold
Y_test_pred_prob = model.predict(X_test_scaledR)
Y_test_pred = (Y_test_pred_prob >= optimal_threshold).astype(int)

print(confusion_matrix(Y_test, Y_test_pred))
print(classification_report(Y_test, Y_test_pred))

# rlronp=tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=1)
# estop=tf.keras.callbacks.EarlyStopping(monitor="val_loss",patience=3,restore_best_weights=True)
# callbacks_=[rlronp, estop]
print("Test Loss:", loss)
print("Test Accuracy:", accuracy)

plt.figure(figsize=(8, 6))
plt.plot(history.history['loss'], label='Training Loss', color='blue')
plt.plot(history.history['val_loss'], label='Validation Loss', color='red')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training and Validation Loss')
plt.legend()
plt.grid(True)
plt.show()
plt.savefig("lossPlot_"+args.selection+".png")


import h5py
model.save("classifierModel_"+args.selection+"_v4.h5")


from sklearn.metrics import accuracy_score
import keras.backend as K

# Function to compute input gradients
def compute_input_gradients(model, X):
    input_tensor = model.input
    gradients = K.gradients(model.output, input_tensor)[0]
    gradient_fn = K.function([input_tensor], [gradients])
    input_gradients = gradient_fn([X])[0]
    return input_gradients

# Function to compute permutation feature importance
def permutation_feature_importance(model, X, y):
    baseline_score = accuracy_score(y, model.predict_classes(X))
    feature_importance = np.zeros(X.shape[1])
    for i in range(X.shape[1]):
        X_permuted = X.copy()
        np.random.shuffle(X_permuted[:, i])
        permuted_score = accuracy_score(y, model.predict_classes(X_permuted))
        feature_importance[i] = baseline_score - permuted_score
    return feature_importance

# Compute input gradients
input_gradients = compute_input_gradients(model, X_train_scaledR)

# Compute permutation feature importance
perm_importance = permutation_feature_importance(model, X_train_scaledR, Y_train)

# Print feature importance scores
print("Input Gradients (Feature Importance):", np.mean(np.abs(input_gradients), axis=0))
print("Permutation Feature Importance:", perm_importance)
