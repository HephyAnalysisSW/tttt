# simple script for hyperparameter optimization
#!/usr/bin/env python
import uproot, os, awkward, ROOT
import numpy as np
import pandas as pd

from RootTools.core.standard import *
c1 = ROOT.TCanvas() # do this to avoid version conflict in png.h with keras import ...
c1.Draw()
c1.Print('/tmp/delete.png')

import tttt.Tools.user as user

import Analysis.Tools.syncer as syncer

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--config',             action='store', type=str,   default='tttt_3l', help="Name of the config file")
argParser.add_argument('--name',               action='store', type=str,   default='default', help="Name of the training")
argParser.add_argument('--variable_set',       action='store', type=str,   default='mva_variables', help="List of variables for training")
argParser.add_argument('--output_directory',   action='store', type=str,   default='/groups/hephy/cms/$USER/www/tttt/plots/MVA')
argParser.add_argument('--default',            action='store_true', help='default config of MVA')
argParser.add_argument('--model_directory',    action='store', type=str,   default='./configs/models')
argParser.add_argument('--add_LSTM',           action='store_true', help="add LSTM?")
argParser.add_argument('--input_directory',    action='store', type=str,   default=os.path.expandvars("/eos/vbc/user/cms/$USER/tttt/training-ntuples-tttt/MVA-training") )
argParser.add_argument('--small',              action='store_true', help="small?")
argParser.add_argument('--selectionString',    action='store', type=str,   default='dilepVL-offZ1-njet4p-btag3p')

args = argParser.parse_args()

if args.add_LSTM:   args.name+="_LSTM"
if args.small:      args.name+="_small"

#Logger
import TMB.Tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )

# MVA configuration
import tttt.MVA.configs  as configs
config = getattr( configs, args.config)


# directories
plot_directory   = os.path.join( user.plot_directory, 'MVA', args.name, args.config, args.selectionString)
output_directory = os.path.join( args.output_directory, args.name, args.config)
model_directory = os.path.normpath(args.model_directory)
# fix random seed for reproducibility
np.random.seed(1)

# get the training variable names
mva_variables = [ mva_variable[0] for mva_variable in getattr(config, args.variable_set) ]

n_var_flat   = len(mva_variables)
n_var_flat_1 = n_var_flat*2
n_var_flat_2 = n_var_flat+5

df_file = {}
for i_training_sample, training_sample in enumerate(config.training_samples):
    upfile_name = os.path.join(os.path.expandvars(args.input_directory), args.config+"_"+args.selectionString, training_sample.name, training_sample.name+'.root')
    logger.info( "Loading upfile %i: %s from %s", i_training_sample, training_sample.name, upfile_name)
    upfile = uproot.open(os.path.join(os.path.expandvars(args.input_directory), args.config+"_"+args.selectionString, training_sample.name, training_sample.name+'.root'))
    df_file[training_sample.name]  = upfile["Events"].pandas.df(branches = mva_variables )
    # enumerate
    df_file[training_sample.name]['signal_type'] =  np.ones(len(df_file[training_sample.name])) * i_training_sample

df = pd.concat([df_file[training_sample.name] for training_sample in config.training_samples])

#df = df.dropna() # removes all Events with nan -> amounts to M3 cut

# split dataset into Input and output data
dataset = df.values

# number of samples with 'small'
n_small_samples = 10000
# small
if args.small:
    dataset = dataset[:n_small_samples]

X  = dataset[:,0:n_var_flat]
# regress FI
Y = dataset[:, n_var_flat]

from sklearn.preprocessing import label_binarize
classes = range(len(config.training_samples))
Y = label_binarize(Y, classes=classes)

# loading vector branches for LSTM
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

# split data into train and test, test_size = 0.2 is quite standard for this
from sklearn.model_selection import train_test_split, GridSearchCV

options = {'test_size':0.2, 'random_state':7, 'shuffle':True}

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, **options)
validation_data = ( X_test,  Y_test)
training_data   =   X_train

import tensorflow as tf
from sklearn.model_selection import train_test_split, GridSearchCV

# define model (neural network)
from keras.models import Sequential, Model
from keras.optimizers import SGD
from keras.layers import Input, Activation, Dense, Convolution2D, MaxPooling2D, Dropout, Flatten, LSTM, Concatenate
from keras.layers import BatchNormalization
from keras.utils import np_utils

#import hyperopt for hyperarameter optimization
from hyperopt import fmin, tpe, hp
from hyperopt.pyll.base import scope


def nn_model(parameters):

    model = tf.keras.Sequential()
    model.add(tf.keras.layers.BatchNormalization(input_shape=(n_var_flat, )))
    if args.default:
        model.add(tf.keras.layers.Dense(n_var_flat*2, activation='sigmoid'))
        model.add(tf.keras.layers.Dense(n_var_flat+5, activation='sigmoid'))
    else:
        for n in range(parameters['layers']):
            model.add(tf.keras.layers.Dense(units=parameters['units'], activation=parameters['activation']))

    inputs = Input(shape=(n_var_flat, ))

    # LSTMs
    if args.add_LSTM:
        vec_inputs = tf.keras.layers.Input(shape=(max_timestep, len(vector_branches),) )
        v = tf.keras.layers.LSTM(10, activation='relu', input_shape=(max_timestep, len(vector_branches)))( vec_inputs )
        model.add(v)
        inputs = ( flat_inputs, vec_inputs)

    if args.default:
        model.add(tf.keras.layers.Dense(len(config.training_samples), kernel_initializer=parameters['kernel'], activation=parameters['activation']))
        model.compile(optimizer=parameters['optimizer'], loss=parameters['loss'], metrics=['accuracy'])
        model.summary()
    else:
        model.add(tf.keras.layers.Dense(len(config.training_samples), kernel_initializer='normal', activation='sigmoid'))
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        model.summary()
    return model


def objective(parameters):
    model = nn_model(parameters)
    callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3)
    history = model.fit(training_data, Y_train, sample_weight=None, verbose=0, callbacks=[callback], validation_data=validation_data)
    val_loss = history.history['val_loss'][-1]
    return val_loss


space = {
    'units':        hp.quniform('units', n_var_flat*2, n_var_flat+5, 20),
    'layers':       scope.int(hp.quniform('layers', 2 , 6 , 1)),
    'activation':   hp.choice('activation', ['relu', 'tanh', 'sigmoid', 'softmax']),
    'optimizer':    hp.choice('optimizer', ['adam', 'adadelta', 'adagrad']),
    'kernel':       hp.choice('kernel', ['normal', 'glorot_uniform']),
    'loss':         hp.choice('loss', ['categorical_crossentropy'])#??????????????????????????????????????????????????????????????
    }

# hyperparameter search
best = fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=10)
hyperparameters = open(output_directory+"/hyperparameters.txt", "w+")
print("Best set:", best)
hyperparameters.write(best)
