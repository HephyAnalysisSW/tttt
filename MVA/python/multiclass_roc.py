#!/usr/bin/env python

import ROOT, os
from RootTools.core.standard import *
import Analysis.Tools.syncer as syncer
c1 = ROOT.TCanvas() # do this to avoid version conflict in png.h with keras import ...
c1.Draw()
c1.Print('/tmp/delete.png')

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--config',             action='store', type=str,   default='tttt_3l', help="Name of the config file")
argParser.add_argument('--name',               action='store', type=str,   default='default', help="Name of the training")
argParser.add_argument('--variable_set',       action='store', type=str,   default='mva_variables', help="List of variables for training")
argParser.add_argument('--output_directory',   action='store', type=str,   default='/groups/hephy/cms/cristina.giordano/www/tttt/plots')
argParser.add_argument('--input_directory',    action='store', type=str,   default=os.path.expandvars("/eos/vbc/user/cms/$USER/tttt_2l/training-ntuples-tttt/MVA-training") )
argParser.add_argument('--small',              action='store_true', help="small?")
argParser.add_argument('--add_LSTM',           action='store_true', help="add LSTM?")
argParser.add_argument('--selectionString',    action='store', type=str,   default='dilepVL-offZ1-njet4p-btag3p')
argParser.add_argument('--compile',            action='store', type=str, default='categorical')
argParser.add_argument('--trainingType',      action='store', type=str, default='multi')
argParser.add_argument("--isWeighted",        action='store_true', help="Are samples balanced?")
args = argParser.parse_args()

if args.add_LSTM:   args.name+="_LSTM"
if args.small:      args.name+="_small"

#Logger
import TMB.Tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )

# MVA configuration
import tttt.MVA.configs  as configs
config = getattr( configs, args.config)

import uproot
import awkward
import numpy as np
import pandas as pd
#import h5py

#########################################################################################
# Data import and preprocessing

import tttt.Tools.user as user

#Directories
plot_directory   = os.path.join( user.plot_directory, 'MVA', args.name, args.config, args.selectionString)
output_directory = os.path.join( args.output_directory, args.name, args.config)

# fix random seed for reproducibility
np.random.seed(1)

# get the training variable names
mva_variables = [ mva_variable[0] for mva_variable in getattr(config, args.variable_set) ]

n_var_flat   = len(mva_variables)
n_var_flat_1 = n_var_flat*2
n_var_flat_2 = n_var_flat+5
print(n_var_flat_1, n_var_flat_2)

df_file = {}
for i_training_sample, training_sample in enumerate(config.training_samples):
    upfile_name = os.path.join(os.path.expandvars(args.input_directory), args.config+"_"+args.selectionString, training_sample.name, training_sample.name+'.root')
    logger.info( "Loading upfile %i: %s from %s", i_training_sample, training_sample.name, upfile_name)
    upfile = uproot.open(os.path.join(os.path.expandvars(args.input_directory), args.config+"_"+args.selectionString, training_sample.name, training_sample.name+'.root'))
    df_file[training_sample.name]  = upfile["Events"].pandas.df(branches = mva_variables )
    # enumerate
    df_file[training_sample.name]['signal_type'] =  np.ones(len(df_file[training_sample.name])) * i_training_sample

df = pd.concat([df_file[training_sample.name] for training_sample in config.training_samples])


#Count the number of entried for dataset balance
category_counts = df['signal_type'].value_counts()

# Print the number of entries for each category
for category, count in category_counts.items():
    category_name = config.training_samples[int(category)].name
    print("Category {}: {} ".format(category_name, count))
# df = df.dropna() # removes all Events with nan -> amounts to M3 cut

# split dataset into Input and output data
dataset = df.values
# number of samples with 'small'
n_small_samples = 10000
if args.small:
    dataset = dataset[:n_small_samples]

X  = dataset[:,0:n_var_flat]
Y = dataset[:, n_var_flat]

from sklearn.preprocessing import label_binarize
classes = range(len(config.training_samples))
print(classes)
Y = label_binarize(Y, classes=classes)


# Loading vector branches for LSTM
if args.add_LSTM:
    vector_branches = ["mva_Jet_%s" % varname for varname in config.jetVarNames]
    max_timestep = 10 # for LSTM

    vec_br_f  = {}

    for i_training_sample, training_sample in enumerate(config.training_samples):
        upfile_name = os.path.join(os.path.expandvars(args.input_directory), args.config+"_"+args.selectionString, training_sample.name, training_sample.name+'.root')
        logger.info( "Loading vector branches %i: %s from %s", i_training_sample, training_sample.name, upfile_name)
        with uproot.open(upfile_name) as upfile:
            vec_br_f[i_training_sample]   = {}
            for name, branch in upfile["Events"].arrays(vector_branches).iteritems():
                vec_br_f[i_training_sample][name] = branch.pad(max_timestep)[:,:max_timestep].fillna(0)

    vec_br = {name: awkward.JaggedArray.concatenate( [vec_br_f[i_training_sample][name] for i_training_sample in range(len(config.training_samples))] ) for name in vector_branches}
    if args.small:
        for key, branch in vec_br.iteritems():
            vec_br[key] = branch[:n_small_samples]

    # put columns side by side and transpose the innermost two axis
    len_samples = len(vec_br.values()[0])
    V           = np.column_stack( [vec_br[name] for name in vector_branches] ).reshape( len_samples, len(vector_branches), max_timestep).transpose((0,2,1))

# Train test split (test_size = 0.2)
from sklearn.model_selection import train_test_split

options = {'test_size':0.2, 'random_state':7, 'shuffle':True}

if args.add_LSTM:
    X_train, X_test, Y_train, Y_test, V_train, V_test = train_test_split(X, Y, V, **options)
    validation_data = ( [X_test,  V_test], Y_test )
    training_data   =   [X_train, V_train]
else:
    X_train, X_test, Y_train, Y_test                  = train_test_split(X, Y, **options)
    validation_data = ( X_test,  Y_test)
    training_data   =   X_train

#########################################################################################
# Model
from keras.models import Sequential, Model
from keras.optimizers import SGD
from keras.layers import Input, Activation, Dense, Convolution2D, MaxPooling2D, Dropout, Flatten, LSTM, Concatenate
from keras.layers import BatchNormalization
from keras.utils import np_utils

compileDict = {"OG": {"optimizer": "adam", "loss": "mean_squared_error", "metric": "mean_absolute_percentage_error"},
               "binary": {"optimizer": "adam", "loss": "binary_crossentropy", "metric": "accuracy"},
               "categorical": {"optimizer": "adam", "loss": "categorical_crossentropy", "metric": "accuracy"}}

# Flat layers
flat_inputs = Input(shape=(n_var_flat, ))
x = BatchNormalization(input_shape=(n_var_flat, ))(flat_inputs)
x = Dense(n_var_flat*2, activation='sigmoid')(x)
x = Dense(n_var_flat+5, activation='sigmoid')(x)

inputs = flat_inputs

# LSTMs
if args.add_LSTM:
    vec_inputs = Input(shape=(max_timestep, len(vector_branches),) )
    v = LSTM(10, activation='relu', input_shape=(max_timestep, len(vector_branches)))( vec_inputs )
    x = Concatenate()( [x, v])
    inputs = ( flat_inputs, vec_inputs)

if args.trainingType=="multi":
    outputs = Dense(len(config.training_samples), kernel_initializer='normal', activation='sigmoid')(x)
    # for multiclassification it is best to consider the softmax!
elif args.trainingType=="one":
    outputs = Dense(1, kernel_initializer='normal', activation='sigmoid')(x)

model = Model( inputs, outputs )

model.compile(optimizer=compileDict[args.compile]["optimizer"], loss=compileDict[args.compile]["loss"], metrics=[compileDict[args.compile]["metric"]])
model.summary()

from keras.utils.vis_utils import plot_model

plot_model(model, to_file='modelPlot.eps', show_shapes=True, show_layer_names=True)

# define callback for early stopping
import tensorflow as tf
callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3) # patience can be higher if a more accurate result is preferred
                                                                        # I would recommmend at least 3, otherwise it might cancel too early
# train the model
if args.add_LSTM:
    batch_size = 1024 # otherwise the valScore is null
else:
    batch_size = 1024*6

from sklearn.utils.class_weight import compute_class_weight

Y_train_flat = np.argmax(Y_train, axis=1)
print(Y_train_flat)

class_weights = compute_class_weight('balanced', classes=np.unique(Y_train_flat), y=Y_train_flat)
class_weights_dict = {i: class_weights[i] for i in range(len(class_weights))}
print("Class Weights:", class_weights_dict)

import numpy as np

if args.isWeighted: args.name+="_isWeighted"

if not args.isWeighted:
    class_weight_ = None
else:
    class_weight_ = class_weights_dict

history = model.fit(training_data,
                    Y_train,
                    sample_weight = None,
                    class_weight=class_weight_,
                    epochs=100,
                    batch_size=batch_size,
                    #verbose=0, # switch to 1 for more verbosity, 'silences' the output
                    callbacks=[callback],
                    #validation_split=0.1
                    validation_data = validation_data,
                   )

loss_values = history.history['loss']
other_loss_values = history.history['val_loss']
print('training finished')

# saving
if not os.path.exists(output_directory):
    os.makedirs(output_directory)
if args.add_LSTM:
    fileName = "regression_model_"+args.compile+"_"+str(n_var_flat_1)+"_"+str(n_var_flat_2)+"_LSTM.h5"
else:
    fileName = "regression_model_"+args.compile+"_"+str(n_var_flat_1)+"_"+str(n_var_flat_2)+".h5"
output_file = os.path.join(output_directory, fileName)
local_file = fileName
model.save(output_file)
model.save(local_file)
logger.info("Written model to: %s", output_file)


#plot roc curves
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, roc_auc_score

if not args.small:
    formats = ['png', 'pdf']
    # Loss function plot
    plt.figure(figsize=(8, 6))
    plt.plot(loss_values, label='Training Loss', color='blue')
    plt.plot(other_loss_values, label='Test Loss', color='red')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.grid(True)
    for f in formats:
        plt.savefig(plot_directory+'/lossPlot.'+f)
    plt.close()


    if args.add_LSTM:
       Y_predict = model.predict( [X_test,  V_test] )
    else:
        Y_predict = model.predict(X_test)

    # I prefer the input weights in Swan
    # auc_scores = []
    # feature_auc_scores = {}
    #
    # X_test_original = X_test.copy()
    # for i_feature in range(X_test.shape[1]):
    #     feature_vals = X_test[:, i_feature].copy()
    #     np.random.shuffle(feature_vals)
    #     X_test[:, i_feature] = feature_vals
    #     Y_predict = model.predict(X_test)
    #     auc_score = roc_auc_score(Y_test, Y_predict)
    #     auc_scores.append(auc_score)
    #     feature_names = mva_variables[i_feature]
    #     feature_auc_scores[feature_names] = auc_score
    #     print("Feature {}".format(i_feature) + " shuffled, AUC score {}".format(auc_score))
    #     # reset to origin
    #     X_test[:, i_feature] = X_test_original[:, i_feature]
    #
    #
    # plt.figure(figsize=(10, 6))
    # plt.bar(range(len(feature_auc_scores)), list(feature_auc_scores.values()), tick_label=list(feature_auc_scores.keys()))
    # plt.xticks(rotation=45, ha='right')
    # plt.xlabel('Features')
    # plt.ylabel('AUC score')
    # plt.title('Feature Importance')
    # plt.tight_layout()
    # for f in formats:
    #     plt.savefig(plot_directory+"/feature_importance."+f)
    #
    # plt.close()

    #ROC curves
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    # for i in classes:
    if not args.trainingType=="oneVsAll":
        for i in range(len(config.classes)):
            fpr[i], tpr[i], _ = roc_curve(Y_test[:, i], Y_predict[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])

            plt.figure(figsize=(8, 6))
            plt.plot(fpr[i], tpr[i],  color='blue', lw=2, label='ROC curve (area = %0.2f)'%roc_auc[i])
            plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('False Positive Rate', fontsize=15)
            plt.ylabel('True Positive Rate', fontsize=15)
            plt.title('ROC Curve - {}'.format(config.classes[i]))
            plt.legend(loc="lower right")
            for f in formats:
                plt.savefig(plot_directory + '/ROC_curve_{}.'.format(config.classes[i])+f)
            plt.close()
    else:
        fpr, tpr, _ = roc_curve(Y_test, Y_predict)
        roc_auc = auc(fpr, tpr)
        plt.figure(figsize=(8, 6))
        plt.plot(fpr[i], tpr[i],  color='blue', lw=2, label='ROC curve (area = %0.2f)'%roc_auc[i])
        plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=15)
        plt.ylabel('True Positive Rate', fontsize=15)
        plt.title("Roc 4t vs tt")
        plt.legend(loc="lower right")
        for f in formats:
            plt.savefig(plot_directory + 'ROC_4tvstt.'+f)


    #signal vs all
    Y_predict_s = np.zeros((len(Y_predict), 2))
    Y_predict_s[:,0] = Y_predict[:,0]
    Y_predict_s[:,1] = Y_predict[:,1] + Y_predict[:,2] + Y_predict[:,3]
    for i, y in enumerate(Y_predict_s):
        Y_predict_s[i] = Y_predict_s[i] / np.sum(y)

    fpr, tpr, _ = roc_curve(Y_test[:, 0], Y_predict_s[:, 0])
    plt.clf()
    plt.plot([0, 1], [0, 1], 'k--')
    plt.plot(fpr, tpr, color='blue')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC - 4t vs Others (Predicted)')
    plt.legend(loc="lower right")
    plt.grid(True)
    for f in formats:
        plt.savefig(plot_directory+'/ROC_4tvsOthers.'+f)


    # Plot score distribution
    plt.figure(figsize=(8, 6))
    plt.hist(Y_predict_s[:,0], bins=30, color='skyblue', alpha=0.7, label='Class 0 (tttt)')
    plt.hist(Y_predict_s[:,1], bins=30, color='salmon', alpha=0.7, label='Class 1 (Others)')
    plt.xlabel('Predicted Score')
    plt.ylabel('Frequency')
    plt.title('Score Distribution')
    plt.legend()
    plt.grid(True)
    for f in formats:
        plt.savefig(plot_directory+'/score_4tvsOthers.'+f)

    print("Done with plots")
else:
    print("Done with small, no plotting")
