#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by lljzhiwang on 2019/5/6
import numpy as np
from sklearn import metrics
import matplotlib.pyplot as plt

def simple_metrics(y_test, y_pred):

    acc=metrics.accuracy_score(y_test, y_pred)  #acc (TP+TN)/(P+N)
    print("acc=%.2f" %acc)
#     auc=metrics.roc_auc_score(y_test,y_pred,average=)
#     print('AUC=%.2f' %auc)
    print('-----------Confusion_Matrix---------')
    print(metrics.confusion_matrix(y_test,y_pred))
    print('-----------Classification_report---------')
    print(metrics.classification_report(y_test,y_pred))

def plot_roc(y_test,y_pred):
    n_classes = len(set(y_test))
    plt.figure()
    lw = 2
    plt.figure(figsize=(10, 10))
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    if n_classes==2:
        fpr, tpr, threshold = metrics.roc_curve(y_test,y_pred)
        auc = metrics.auc(fpr, tpr)
        plt.plot(fpr, tpr, color='darkorange', lw=lw, label='ROC curve AUC=%.2f' % auc)  ###假正率为横坐标，真正率为纵坐标做曲线
    if n_classes>2:
        colors=['darkorange','r','g','b','k']
        for i in range(min(5,n_classes)):
            fpr, tpr, threshold = metrics.roc_curve(y_test, y_pred, pos_label=i)
            auc = metrics.auc(fpr, tpr)
            plt.plot(fpr, tpr, color=colors[i], lw=lw, label='ROC curve pos_label=%d AUC=%.2f' %(i,auc))  ###假正率为横坐标，真正率为纵坐标做曲线
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.01])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()