# -*- coding: utf-8 -*-
"""
Created on  三月 18 19:58 2017

@author: aeloyq
"""

import nnbuilder
from nnbuilder.data import *
from nnbuilder.layers.simple import *
from nnbuilder.layers.sequential import *
from nnbuilder.algrithms import *
from nnbuilder.extensions import *
from nnbuilder.model import *
from nnbuilder.main import *
import dictionary

#theano.config.profile=True
#theano.config.profile_memory=True
#theano.config.optimizer='fast_compile'
debugmode.config.debug_time=3
debugmode.config.debug_batch=5

sample.config.sample_freq=20
sample.config.sample_times=2
sample.config.sample_func=dictionary.mt_sample

saveload.config.save_freq=500

source_vocab_size=30000
target_vocab_size=30000

source_emb_dim=620
target_emb_dim=620

enc_dim=1000
dec_dim=1000

config.vocab_source='./data/vocab.en-fr.en.pkl'
config.vocab_target='./data/vocab.en-fr.fr.pkl'

sgd.config.learning_rate=0.0001
sgd.config.grad_clip_norm=1.
sgd.config.if_clip=True

adadelta.config.if_clip=True
sgd.config.grad_clip_norm=1.

config.name='mt_demo'
config.data_path='./data/datasets.npz'
config.batch_size=80
config.valid_batch_size=64
config.max_epoches=1000
config.savelog=True
config.transpose_x=True
config.transpose_y=True
config.mask_x=True
config.mask_y=True
config.int_x=True
config.int_y=True

monitor.config.report_iter_frequence=1
monitor.config.report_iter=True



model=model(source_vocab_size,Int2dX,Int2dY)
model.sequential(Int2dMask,Int2dMask)
model.add(embedding(source_emb_dim))
model.add(encoder(enc_dim))
model.add(decoder(dec_dim,target_emb_dim,target_vocab_size,in_dim=enc_dim))


data=Load_mt(maxlen=50,sort_by_asc=False)


result=train(datastream=data,model=model,algrithm=sgd,extension=[monitor])

