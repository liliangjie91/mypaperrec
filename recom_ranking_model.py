#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by lljzhiwang on 2019/7/9
import lightgbm as lgb
import pandas as pd
import numpy as np
import util_common as uc
from sklearn.metrics import mean_squared_error
from sklearn import datasets
from sklearn.model_selection import train_test_split,cross_validate,GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Perceptron,LogisticRegression,SGDClassifier
from sklearn import metrics
from sklearn.ensemble import GradientBoostingClassifier,RandomForestClassifier,AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
import util_path as path
from Logginger import init_logger
logger=init_logger('RMODEL',logging_path=path.logpath)

params_gbdt = {
    'task': 'train',
    'boosting_type': 'gbdt',
    'objective': 'binary',
    'metric': {'binary_logloss','l2', 'auc'},
    'num_leaves': 30,
    'max_depth': 5,
    'min_data_in_leaf': 450,
    'num_trees': 100,
    'learning_rate': 0.05,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': 0
}

def simple_metrics(y_test, y_pred):
    acc=metrics.accuracy_score(y_test, y_pred)  #acc (TP+TN)/(P+N)
    logger.info("acc=%.2f" %acc)
#     auc=metrics.roc_auc_score(y_test,y_pred,average=)
#     print('AUC=%.2f' %auc)
    logger.info('-----------Confusion_Matrix---------')
    logger.info(metrics.confusion_matrix(y_test,y_pred))
    logger.info('-----------Classification_report---------')
    logger.info(metrics.classification_report(y_test,y_pred))

def lr(X_train_std, y_train,X_test_std,y_test,batchsize=100):
    #使用逻辑回归预测
    logger.info('\nLR:****************')
    if len(X_train_std)>100000:
        lr=SGDClassifier(loss='log')
        datatrain=zip(X_train_std,y_train)
        cnt=0
        xs,ys=[],[]
        for x,y in datatrain:
            cnt+=1
            if cnt%batchsize==0:
                # print("LR process %d" %cnt)
                lr.partial_fit(xs,ys,classes=np.unique(ys))
                xs, ys = [], []
            xs.append(x)
            ys.append(y)
        if xs:
            lr.partial_fit(xs, ys)
    else:
        lr=LogisticRegression(penalty='l2')
        lr.fit(X_train_std, y_train)
    y_pred_label,y_pred_score=[],[]
    tmpxs = []
    cnt=0
    for x in X_test_std:
        tmpxs.append(x)
        cnt+=1
        if cnt % batchsize == 0:
            ylabel = lr.predict(tmpxs)
            yscore = lr.predict_proba(tmpxs)
            tmpxs = []
            y_pred_label.extend(ylabel)
            y_pred_score.extend(yscore)
    if tmpxs:
        ylabel = lr.predict(tmpxs)
        yscore = lr.predict_proba(tmpxs)
        y_pred_label.extend(ylabel)
        y_pred_score.extend(yscore)

    simple_metrics(y_test,y_pred_label)
    return y_pred_label,y_pred_score,lr

def perceptron(X_train_std, y_train,X_test_std,y_test):
    logger.info('\nPerceptron:****************')
    # 训练感知机模型
    # n_iter：可以理解成梯度下降中迭代的次数
    # eta0：可以理解成梯度下降中的学习率
    # random_state：设置随机种子的，为了每次迭代都有相同的训练集顺序
    ppn = Perceptron(max_iter=40, eta0=0.1, random_state=0)
    ppn.fit(X_train_std, y_train)
    # 分类测试集，这将返回一个测试结果的数组
    y_pred_ppn = ppn.predict(X_test_std)
    simple_metrics(y_test,y_pred_ppn)
    return y_pred_ppn

def gbdt(X_train, y_train, X_test, y_test,
         iflightgbm=True, params=params_gbdt,gbdtmodelpath=path.path_model+'/ml/model_onlygbdt_test.txt',
         ifpreleaves=False):
    #训练GBDT
    logger.info('\nGBDT:****************')
    if iflightgbm:
        train_data = lgb.Dataset(X_train, y_train)
        logger.info('Start training GBDT model...')
        gbm = lgb.train(params, train_data, num_boost_round=100, valid_sets=train_data,early_stopping_rounds=5)
        logger.info('Save GBDT model to %s' % gbdtmodelpath)
        gbm.save_model(gbdtmodelpath)
        logger.info('Start predicting gbdt labels...')
        # y_pred_train = gbm.predict(X_train, pred_leaf=True)
        y_predprob = gbm.predict(X_test,num_iteration=gbm.best_iteration)
        y_pred=[]
        threshold = 0.5
        for pred in y_predprob:
            result = 1 if pred > threshold else 0
            y_pred.append(result)
        if ifpreleaves:
            y_pred_leaves=gbm.predict(X_test,pred_leaf=True)
    else:
        gbm = GradientBoostingClassifier(random_state=10)
        gbm.fit(X_train, y_train)
        y_pred = gbm.predict(X_test)
        y_predprob = gbm.predict_proba(X_test)[:, 1]
    if isinstance(y_test[0],str):
        y_test=np.array([int(i) for i in y_test])
    simple_metrics(y_test,y_pred)
    logger.info("AUC Score (Train): %f" % metrics.roc_auc_score(y_test, y_predprob))

def svmm(X_train_std, y_train,X_test_std,y_test):
    logger.info('\nSVM:****************')
    svm0=SVC()
    svm0.fit(X_train_std, y_train)
    y_pred = svm0.predict(X_test_std)
    simple_metrics(y_test,y_pred)

def rf(X_train_std, y_train,X_test_std,y_test):
    logger.info('\nRandom Forests:****************')
    rf0 = RandomForestClassifier(oob_score=True, random_state=10)
    rf0.fit(X_train_std,y_train)
    y_pred = rf0.predict(X_test_std)
    y_score = rf0.predict_proba(X_test_std)[:,1]
    simple_metrics(y_test,y_pred)
    logger.info('auc=%.3f' % metrics.roc_auc_score(y_test,y_pred))

def adab(X_train_std, y_train,X_test_std,y_test):
    logger.info('\nADaboost:****************')
    bdt = AdaBoostClassifier(DecisionTreeClassifier(max_depth=2, min_samples_split=20, min_samples_leaf=5),
                         algorithm="SAMME",
                         n_estimators=200, learning_rate=0.8)
    bdt.fit(X_train_std, y_train)
    y_pred = bdt.predict(X_test_std)
    simple_metrics(y_test,y_pred)
    logger.info("Score:", bdt.score(X_train_std, y_train))

def LR_GBDT(X_train,y_train,X_test,y_test,
            params=params_gbdt,gbdtmodelpath='data/model/ml/model_lrgbdt_test.txt'):
    #GBDT+LR 模型
    logger.info('\n\nLR+GBDT model:****************')
    #GBDT model
    train_data = lgb.Dataset(X_train, y_train)
    # eval_data = lgb.Dataset(X_test, y_test, reference=train_data)

    num_leaf = params['num_leaves']

    logger.info('Start training GBDT model...')
    gbm = lgb.train(params, train_data, num_boost_round=100, valid_sets=train_data)
    logger.info('Save GBDT model to %s' %gbdtmodelpath)
    gbm.save_model(gbdtmodelpath)
    logger.info('Start predicting gbdt labels...')
    y_pred_train = gbm.predict(X_train, pred_leaf=True)
    y_pred_test = gbm.predict(X_test, pred_leaf=True)

    def gbdtlabels2onehot(gbdtlabels,num_leaf=num_leaf):
        #根据gbdt预测的叶子节点序列，生成对应的onehot编码
        transformed_matrix = np.zeros([len(gbdtlabels), len(gbdtlabels[0]) * num_leaf],
                                               dtype=np.int64)  # N * num_tress * num_leafs
        for i in range(0, len(gbdtlabels)):
            temp = np.arange(len(gbdtlabels[0])) * num_leaf + np.array(gbdtlabels[i])
            transformed_matrix[i][temp] += 1
        return transformed_matrix

    logger.info('Writing transformed training data')
    onehotencode_gbdt_traindata = gbdtlabels2onehot(y_pred_train)

    logger.info('Writing transformed testing data')
    onehotencode_gbdt_testdata = gbdtlabels2onehot(y_pred_test)

    del X_train,X_test
    # LR model
    ypred_label, ypred_score, lrmodel=\
        lr(onehotencode_gbdt_traindata,y_train,onehotencode_gbdt_testdata,y_test)
    ypred_score=np.array(ypred_score)
    if isinstance(y_test[0],str):
        y_test=np.array([int(i) for i in y_test])
    metrics.roc_auc_score(y_test, ypred_score[:, 1])

if __name__ == '__main__':
    import feature_process as fp
    # traindatap='./data/highq_5w/traindata_nofnvec_01.pkl'
    # traindatap='./data/highq_5w/allexamfea_values_samplesimpledown.pkl'
    # alldata=uc.pickle_load(traindatap)
    # x_train, x_test, y_train, y_test = alldata

    x_train, x_test, y_train, y_test=fp.exam2traindata(encoding=False,sample='up',saveres=True)
    x_train, y_train, x_test, y_test = np.array(x_train), np.array(y_train), np.array(x_test), np.array(y_test)
    # lr(x_train,y_train,x_test,y_test)
    gbdt(x_train,y_train,x_test,y_test)
    # LR_GBDT(x_train,y_train,x_test,y_test)