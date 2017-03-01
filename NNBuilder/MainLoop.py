# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 19:37:12 2016

@author: aeloyq
"""
#TODO:类化，装饰器加入，处理extension
import timeit
import theano
import numpy as np
import copy
import config

def Train(model_stream, datastream,extension):
    datastream,train_model,valid_model,test_model,sample_model,debug_model,model,NNB_model,optimizer=model_stream
    train_X, valid_X, test_X, train_Y, valid_Y, test_Y = datastream
    print "\r\nTrainning Model:\r\n"
    train_minibatches, valid_minibatches, test_minibatches=get_minibatches_idx(datastream)
    sample_data=[datastream[0],datastream[3]]
    batch_size=config.batch_size
    max_epoches=config.max_epoches
    iteration_total=[0]
    epoch_time=[0.]
    train_result=[]
    debug_result=[]
    train_error=[1.]
    test_error=[1.]
    best_valid_error=[1.]
    best_iter=[0]
    epoches=[0]
    errors=[]
    costs=[]
    first=True
    dict={}
    dict['prepare_data']=prepare_data
    dict['get_sample_data']=get_sample_data
    dict['conf'] = config
    dict['batch_size']=config.batch_size
    dict['model_stream']=model_stream
    dict['iteration_total']=iteration_total
    dict['minibatches']=[train_minibatches,valid_minibatches,test_minibatches]
    dict['data_stream']=datastream
    dict['sample_data']=sample_data
    dict['epoch_time'] = epoch_time
    dict['train_error'] = train_error
    dict['train_result'] = train_result
    dict['test_error'] = test_error
    dict['debug_result'] = debug_result
    dict['best_valid_error'] = best_valid_error
    dict['best_iter'] = best_iter
    dict['epoches'] = epoches
    dict['errors'] = errors
    dict['costs'] = costs
    dict['stop']=False
    extension_instance=[]
    for ex in extension:ex.config.kwargs=dict;ex.config.init();extension_instance.append(ex.config)
    # Main Loop
    print '        ','Training Start'
    for ex in extension_instance:   ex.before_train()
    if dict['stop']:
        return -1, [], [], debug_result
    while(True):
        # Train model iter by iter
        for _,index in train_minibatches:
            data=prepare_data(train_X,train_Y,index)
            train_result=train_model(*data)
            dict['train_result'] = train_result
            train_cost=train_result[0]
            iteration_total[0] += 1
            for ex in extension_instance:   ex.after_iteration()
            if dict['stop']:
                return epoches[0],errors,costs,debug_result
            # Stop When Sucess
            if train_error == 0:
                testdatas = []
                for _, index in test_minibatches:
                    data = prepare_data(test_X,test_Y, index)
                    testdatas.append(data)
                if np.mean([test_model(*tuple(testdata)) for testdata in testdatas]) == 0:
                    best_iter[0] = iteration_total
                    print "\r\n●Trainning Sucess●\r\n"
                    break
        # After epoch
        testdatas = []
        for _, index in test_minibatches:
            data = prepare_data(test_X,test_Y, index)
            testdatas.append(data)
        train_error[0] = np.mean([test_model(*tuple(testdata)) for testdata in testdatas])
        errors.append(train_error[0])
        costs.append(train_cost)
        epoches[0] += 1
        for ex in extension_instance:   ex.after_epoch()
        # Stop When Timeout
        if epoches[0] > max_epoches - 1 and max_epoches != -1:
            print "⊙Trainning Time Out⊙"
            break
    for ex in extension_instance:   ex.after_train()
    return epoches[0],errors,costs,debug_result

def prepare_data(data_x,data_y,index):
    if not config.trans_input:
        x = [data_x[t] for t in index]
        y = [data_y[t] for t in index]
        data = [x, y]
        data = tuple(data)
        return  data
    else:
        x = [data_x[t] for t in index]
        y = [data_y[t] for t in index]
        maxlen=max([len(d) for d in x])
        x=np.array(x)
        mask=np.ones([len(index),maxlen])
        for idx,i in enumerate(x):
            for j in range(len(i), maxlen):
                i.append(np.zeros_like(i[0]).tolist())
                mask[idx,j]=0.
        x_new=[]
        for idx in range(len(x[0])):
            x_new.append([x[i][idx] for i in range(len(x))])
        x=np.array(x_new).astype(theano.config.floatX)
        y=np.array(y).astype(theano.config.floatX)
        mask=mask.transpose().astype(theano.config.floatX)
        data=[x,y,mask]
        data = tuple(data)
        return data

def get_minibatches_idx(datastream, shuffle=False):
    train_X, valid_X, test_X, train_Y, valid_Y, test_Y = datastream
    valid_X = valid_X[0]
    test_X = test_X[0]
    minibatch_size=config.batch_size
    valid_minibatch_size=config.valid_batch_size
    try:
        n_train = train_X.get_value().shape[0]
        n_valid = valid_X.get_value().shape[0]
        n_test= test_X.get_value().shape[0]
    except:
        n_train = len(train_X)
        n_valid = len(valid_X)
        n_test = len(test_X)

    def get_(n,minibatch_size,shuffle=None):
        idx_list = np.arange(n, dtype="int32")

        if shuffle:
            np.random.shuffle(idx_list)

        minibatches = []
        minibatch_start = 0
        for i in range(n // minibatch_size):
            minibatches.append(idx_list[minibatch_start:
                                        minibatch_start + minibatch_size])
            minibatch_start += minibatch_size

        if (minibatch_start != n):
            # Make a minibatch out of what is left
            minibatches.append(idx_list[minibatch_start:])

        return zip(range(len(minibatches)), minibatches)
    train_minibatches=get_(n_train,minibatch_size)
    valid_minibatches = get_(n_valid, valid_minibatch_size)
    test_minibatches = get_(n_test, valid_minibatch_size)
    return train_minibatches,valid_minibatches,test_minibatches

def get_sample_data(datastream):
    if not config.trans_input:
        train_X, valid_X, test_X, train_Y, valid_Y, test_Y = datastream
        try:
            n_train = train_X.get_value().shape[0]
        except:
            n_train = len(train_X)
        idx=config.rng.randint(0,n_train)
        sample_x=train_X[idx]
        sample_y=train_Y[idx]
        data=[[sample_x],[sample_y]]
        return data
    else:
        train_X, valid_X, test_X, train_Y, valid_Y, test_Y = datastream
        try:
            n_train = train_X.get_value().shape[0]
        except:
            n_train = len(train_X)
        idx=config.rng.randint(0,n_train)
        data=prepare_data(train_X,train_Y,[idx])
        return data



