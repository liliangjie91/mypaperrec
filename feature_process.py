#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by lljzhiwang on 2019/6/27 
from __future__ import division
import util_common as uc
import numpy as np
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import re,os
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler

from sklearn.preprocessing import OneHotEncoder,LabelBinarizer,MultiLabelBinarizer

from sklearn import preprocessing
from sklearn.model_selection import train_test_split,cross_validate,GridSearchCV
from sklearn.neighbors import NearestNeighbors
import util_path as path
from Logginger import init_logger
logger=init_logger('FeaProcess',logging_path=path.logpath)

def data2csv():
    fnfeatpath = './data/highq_5w/fn18_5w_features.txt'
    fnfeas = uc.load2list(fnfeatpath)
    fns, cites, cites_w, authcodes, fundcodes, jigoucodes, productcodes, dates, pages, downs, citeds, ifs = [], [], [], [], [], [], [], [], [], [], [], []
    for i in fnfeas:
        if type(i) is str:
            iss = i.split()
            if len(iss) == 14:
                fns.append(iss[0])
                cites.append(iss[1])
                cites_w.append(iss[2])
                authcodes.append(iss[3])
                fundcodes.append(iss[4])
                jigoucodes.append(iss[5])
                productcodes.append(iss[6])
                dates.append(iss[7])
                pages.append(iss[8])
                downs.append(iss[9])
                citeds.append(iss[10])
                ifs.append(iss[11])
    exs = pd.DataFrame({'fns': fns, 'cites': cites, 'cites_w': cites_w, 'authcodes': authcodes, 'fundcodes': fundcodes,
                        'jigoucodes': jigoucodes, 'productcodes': productcodes, 'dates': dates, 'pages': pages,
                        'downs': downs, 'citeds': citeds, 'ifs': ifs})
    exs.to_csv('./data/highq_5w/fn18_5w_features.csv')

def simpleplot(csvdata,columname='cites',topcommon=20):
    c = Counter(list(csvdata[columname]))
    a = c.items()
    a = sorted(a, key=lambda x: x[0])
    citenum = []
    citecnt = []
    for i in a:
        citenum.append(i[0])
        citecnt.append(i[1])
    plt.plot(citenum, citecnt)
    plt.show()
    print(c.most_common(n=topcommon))
    print(csvdata[columname].describe())

def change_data_format(data):
    # 以下预处理都是基于dataframe格式进行的
    data_new = pd.DataFrame(data)
    return data_new

#缺失值处理
def nan2bivalue(dataf, columename, coverold=False):
    #对于部分有nan值太多的列，可以把是否有值作为特征
    data=pd.read_csv(dataf) if isinstance(dataf, str) else dataf
    data = data.replace('null', np.NAN)
    funds=data[columename]
    fundcode_bi = []
    for i in funds:
        if i is np.NAN:
            fundcode_bi.append(0)
        else:
            fundcode_bi.append(1)
    data['%s_bi' %columename]=fundcode_bi
    if coverold and isinstance(dataf,str): #覆盖原文件
        data.to_csv(dataf)
    return data

def nan_fill4clo_numbers(data, columname):
    #针对数值型列
#     columname='downs'
    columdata=data[columname]
    nancnt=np.isnan(columdata).sum() #nan值个数
    nanpct=nancnt/len(columdata) #nan值占比
    print('NaN cnt percent: %.2f%% in colume %s' %(nanpct*100,columname))
    coldesc=columdata.describe()
    # print(coldesc)
    col_mean=coldesc['mean']
    col_50 = coldesc['50%']
    res=columdata.fillna(col_50) #空值填充，此处使用中位数
    data.loc[:,columname]=res
    return data

def nan_fill4col_strs(data, columname):
    #针对字符串型列
#     columname='productcodes'
    columdata=data[columname].fillna('null')
    data[columname]=columdata
    return data

def nan_remove(dataf,nan_rate=0.5):
    #对于部分nan值过多的列，可以选择剔除
    data = pd.read_csv(dataf) if isinstance(dataf, str) else dataf
    all_cnt=data.shape[0] #总行数
    good_colum=[]
    for i in range(data.shape[1]):
        tmprate=np.isnan(np.array(data.iloc[:,i])).sum()/all_cnt
        if tmprate<nan_rate:
            good_colum.append(i)
    good_data=data.iloc[:,good_colum]
    return good_data

#离群点处理
def outliar_fill(data,colname):
    #四分位法
    splitlist=[0,25,50,75,100]
    percentile = np.percentile(data[colname],splitlist)
    iqr = percentile[3] - percentile[1]
    upLimit = percentile[3]+iqr*1.5
    downLimit = percentile[1]-iqr*1.5
    data.loc[data[colname]<downLimit,colname]=downLimit
    data.loc[data[colname]>upLimit,colname]=upLimit
    return data

def outliar_fill_simple(data,colname,mymax,mymin):
    #简单约束
    data.loc[data[colname]<mymin,colname]=mymin
    data.loc[data[colname]>mymax,colname]=mymax
    return data

#分箱
clos = ['cites','cites_w','citeds','downs','pages','ifs'] #['cites', 'cites_w', 'downs', 'citeds', 'ifs', 'pages']
mybins_cites = [-1, 0, 2, 5, 10, 15, 20, 30, 60, 100, 200000]
mybins_cites_w = [-1, 0, 2, 5, 10, 15, 20, 30, 40, 50000]
mybins_citeds = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10000]
mybins_downs = [-1, 0, 10, 20, 30, 50, 100, 200, 400, 600, 800, 1000, 110000]
mybins_pages = [0, 1, 2, 3, 4, 5, 10, 20, 30, 50, 70, 100, 130, 16000]
mybins_ifs = [-1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

mybins_dic={clos[0]:mybins_cites,
            clos[1]:mybins_cites_w,
            clos[2]:mybins_citeds,
            clos[3]:mybins_downs,
            clos[4]:mybins_pages,
            clos[5]:mybins_ifs}

def boxing_simple(data,colname,mybins):
    #简单分箱
#     mybins=[-1,0,2,5,10,15,20,30,60,100,200]
    c=pd.cut(data[colname],bins=mybins,labels=[i for i in range(1,len(mybins))])
    data[colname]=c
    return data

def run_binning(data):
    for i in range(6):
        coln = clos[i]
        tmpbins = mybins_dic[coln]
        data = boxing_simple(data, coln, tmpbins)

# 对需要multihot编码的特征单独处理
def col2multibinar(col,classes=None):
    #针对基金代码做的处理
    mlb=MultiLabelBinarizer(classes=classes)
    res=[]
    for i in col:
        i=i.upper().strip()
        if i == '0':
            i='NULLVAL'
        res.append(re.split('[;；]+',i))
    multihotcodes=mlb.fit_transform(res) if not classes else mlb.transform(res)
    return multihotcodes,mlb

# 对字符型且只需onehot编码的特征做处理
def col2onehot_str(col,classes=None):
    lbb=LabelBinarizer()
    if classes:
        lbb.classes_=classes
    onehotcodes=lbb.fit_transform(col) if not classes else lbb.transform(col)
    return onehotcodes,lbb

# 对数值型且只需onehot编码的特征做处理
def col2onehot_numbers(col,n_values='auto'):
    ohe = OneHotEncoder(n_values=n_values)
    # data= np.array(col).reshape(-1, 1)
    data=col
    ohes = ohe.fit_transform(data).toarray() if not isinstance(n_values,list) else ohe.transform(data).toarry()
    return ohes,ohe


class InputFeature2(object):
    def __init__(self,
                 uniqid,
                 uid,           #用户id
                 fn,            #文件名
                 uidvec,        #用户向量
                 fnvec,         #文件向量
                 fnnumsf,
                 fnfuncode,     #基金代码
                 fnprodcode,    #出版物代码
                 label=None          #是否被该用户下载
                 ):
        self.uniqid=uniqid
        self.uid=uid
        self.fn=fn
        self.uidvec=uidvec
        self.fnvec=fnvec
        self.fnnumsf=fnnumsf
        self.fnfuncode=fnfuncode
        self.fnprodcode=fnprodcode
        self.label=label

    def getvecs(self):
        return np.concatenate((self.uidvec,self.fnvec,self.fnnumsf,self.fnfuncode,self.fnprodcode))

    def get_x_y(self):
        return self.getvecs(),self.label


class InputFeature(object):
    #输入特征类
    def __init__(self,
                 uniqid,
                 uid,           #用户id
                 fn,            #文件名
                 uidvec,        #用户向量
                 fnvec,         #文件向量
                 fncite,        #引文数量
                 fncite_w,      #外文引文数量
                 fncited,       #被引频次
                 fndown,        #被下载频次
                 fnpage,        #论文页数
                 fnif,          #论文杂志影响因子
                 fnfuncode,     #基金代码
                 fnprodcode,    #出版物代码
                 label          #是否被该用户下载
                 ):
        self.uniqid=uniqid
        self.uid=uid
        self.fn=fn
        self.uidvec=uidvec
        self.fnvec=fnvec
        self.fncite=fncite
        self.fncite_w=fncite_w
        self.fncited=fncited
        self.fndown=fndown
        self.fnpage=fnpage
        self.fnif=fnif
        self.fnfuncode=fnfuncode
        self.fnprodcode=fnprodcode
        self.label=label

def exam2features(examples,vecdic_users,vecdic_fns,fn_features,respath=None,process_per=10000,earlystop=100):
    examps=uc.load2list(examples)
    vecdicu=uc.pickle_load(vecdic_users) if isinstance(vecdic_users,str) else vecdic_users
    vecdicf=uc.pickle_load(vecdic_fns) if isinstance(vecdic_fns,str) else vecdic_fns
    logger.info('loadding fn_features...')
    fnfeats=pd.read_csv(fn_features) if isinstance(fn_features,str) else fn_features
    fe_nums4onehot = ['cites','cites_w','citeds','downs','pages','ifs']
    fe_strs4onehot = ['productcodes']
    fe_strs4mulhot = ['fundcodes']
    logger.info('encoding onehot for number features')
    onehots_num,onehots_num_model=col2onehot_numbers(fnfeats[fe_nums4onehot])
    logger.info('encoding onehot for str features')
    onehots_str,onehots_str_model=col2onehot_str(fnfeats[fe_strs4onehot[0]])
    logger.info('encoding multihot for str features')
    mulhots_str,mulhots_model=col2multibinar(fnfeats[fe_strs4mulhot[0]])
    fn_indexdic = {}
    for index, fn in enumerate(list(fnfeats.fns)):
        fn_indexdic[fn] = index
    features=[]
    logger.info('generating features for model...')
    for index,ex in enumerate(examps):
        if index%process_per==0:
            logger.info('process %d' %index)
        (uid, fn, label)=ex.strip().split('+')
        fnindex=fn_indexdic[fn]
        uidvec=np.array(vecdicu[uid])
        fnvec=np.array(vecdicf[fn])
        features.append(InputFeature2(uniqid=index,
                                      uid=uid,
                                      fn=fn,
                                      uidvec=uidvec,
                                      fnvec=fnvec,
                                      fnnumsf=onehots_num[fnindex],
                                      fnfuncode=mulhots_str[fnindex],
                                      fnprodcode=onehots_str[fnindex],
                                      label=label))
        if index<10: #打印前10个样本
            logger.info("\n*** Example ***")
            logger.info('uniqid=%d' %index)
            logger.info('uid=%s' % uid)
            logger.info('fn=%s' % fn)
            logger.info('uidvec=%s' %(' '.join([str(i) for i in uidvec])))
            logger.info('fnvec=%s' % (' '.join([str(i) for i in fnvec])))
            logger.info('fnnumsf=%s' % (' '.join([str(i) for i in onehots_num[fnindex]])))
            logger.info('fnfuncode=%s' % (' '.join([str(i) for i in mulhots_str[fnindex]])))
            logger.info('fnprodcode=%s' % (' '.join([str(i) for i in onehots_str[fnindex]])))
            logger.info('label=%s' % str(label))
        if earlystop and index==earlystop-1:
            break
    if respath:
        uc.pickle_dump(features,respath=respath)
    return features

def exam2traindata_(examples, vecdic_users, vecdic_fns, fn_features,
                    process_per=50000, earlystop=100,
                    resname='traindata_nofnvec_01.pkl',
                    encoding=True, sample=''):
    #loading data
    examps=uc.load2list(examples)
    # examps_posi=examps[:641683]
    # examps_neg=examps[641683:]
    # if examplimit:
    #     examps=examps[:examplimit]
    if sample:
        # sampling
        # split example to X-Y for sampleing
        examps_X,examps_Y=[],[]
        for i in examps:
            (uid, fn, label) = i.strip().split('+')
            examps_X.append('%s+%s' %(uid,fn))
            examps_Y.append(int(label))
        logger.info("raw example y:")
        logger.info(Counter(examps_Y))
        if sample is 'up':
            ros = RandomOverSampler(random_state=0)
            X_resampled, y_resampled = ros.fit_sample(np.array(examps_X).reshape(-1,1), examps_Y)
            print(X_resampled.shape)
            X_resampled = X_resampled.reshape(-1)
            print(X_resampled.shape)
        elif sample is 'down':
            rus = RandomUnderSampler(random_state=0, replacement=True)
            X_resampled, y_resampled = rus.fit_sample(np.array(examps_X).reshape(-1,1), examps_Y)
            print(X_resampled.shape)
            X_resampled = X_resampled.reshape(-1)
            print(X_resampled.shape)
        elif sample is 'simpledown':
            #前641683个是正样本，后287464个是负样本。
            X_resampled, y_resampled = examps_X[:287464]+examps_X[641683:], examps_Y[:287464]+examps_Y[641683:]
        else:
            logger.info('sample methord not found : %s' %sample)
            X_resampled, y_resampled = examps_X, examps_Y
        examps_X, examps_Y = X_resampled, y_resampled
        logger.info("after example y:")
        logger.info(Counter(examps_Y))
        # concat X & Y for forther featear extraction
        examps_new=[]
        for x,y in zip(examps_X,examps_Y):
            examps_new.append('%s+%s' %(x,str(y)))
        examps=examps_new

    logger.info('generating features for model...')
    train_exs, test_exs = train_test_split(examps, test_size=0.3, random_state=2)

    # encoding features
        #loading features
    vecdicu=uc.pickle_load(vecdic_users) if isinstance(vecdic_users,str) else vecdic_users
    # vecdicf=uc.pickle_load(vecdic_fns) if isinstance(vecdic_fns,str) else vecdic_fns
    logger.info('loadding fn_features...')
    fnfeats=pd.read_csv(fn_features) if isinstance(fn_features,str) else fn_features
    fn_indexdic = {}
    for index, fn in enumerate(list(fnfeats.fns)):
        fn_indexdic[fn] = index

    fe_nums4onehot = ['cites','cites_w','citeds','downs','pages','ifs']
    fe_strs4onehot = ['productcodes']
    fe_strs4mulhot = ['fundcodes']
    if encoding:
        logger.info('encoding onehot for number features')
        onehots_num,onehots_num_model=col2onehot_numbers(fnfeats[fe_nums4onehot])
        # logger.info('encoding onehot for str features')
        # onehots_str,onehots_str_model=col2onehot_str(fnfeats[fe_strs4onehot[0]])
        logger.info('encoding multihot for str features')
        mulhots_str,mulhots_model=col2multibinar(fnfeats[fe_strs4mulhot[0]])

    logger.info('training data split get traindata %d, testdata %d' %(len(train_exs),len(test_exs)))
    def examples2x_y(exampls,ifencoding=encoding):
        X,Y=[],[]
        for index,ex in enumerate(exampls):
            if index%process_per==0:
                logger.info('examples2x_y process %d' %index)
            (uid, fn, label)=ex.strip().split('+')
            if fn in fn_indexdic:
                fnindex=fn_indexdic[fn]
            else:
                # print('fn not in fnfeatures %s' %fn)
                continue
            uidvec=np.array(vecdicu[uid])
            fnvec=[0] #np.array(vecdicf[fn])
            if ifencoding:
                x=np.concatenate((uidvec,fnvec,onehots_num[fnindex],mulhots_str[fnindex]))
            else:
                feature_notencoded=list(fnfeats.iloc[fnindex][['fns','cites','cites_w','citeds','downs','pages','ifs']])
                x=np.concatenate((uidvec,fnvec,feature_notencoded[1:]))
            y=int(label)
            X.append(x)
            Y.append(y)
        return X,Y

    x_train, y_train = examples2x_y(train_exs) #获取训练集特征
    x_test, y_test = examples2x_y(test_exs) #获取测试集特征
    logger.info('training data actrauly get traindata %d, testdata %d' % (len(y_train), len(y_test)))
    alldata=[x_train,x_test,y_train,y_test]
    if resname:
        traindatapath=os.path.join(path.path_datahighq5w , resname)
        if not os.path.exists(traindatapath):
            uc.pickle_dump(alldata,traindatapath)
        else:
            newtraindatapath=os.path.join(path.path_datahighq5w , 'newres_%s' %resname)
            logger.info('triandatapath %s allready exists,save this batch traindata to %s' %(traindatapath,newtraindatapath))
            uc.pickle_dump(alldata,newtraindatapath)
    return x_train,x_test,y_train,y_test

def exam2traindata(encoding=True,sample='',saveres=False):
    basedatap = './data/highq_5w/'
    examples = basedatap + 'realexams.txt'
    vecdic_users = basedatap + 'realvec_user.pkl'
    vecdic_fns = basedatap + 'realvec_fn.pkl'
    fn_features = basedatap + 'fnfeatures2use.csv'
    if encoding:
        featuresresanme = 'allexamfea_onehot_sample%s.pkl' %(sample)
    else:
        featuresresanme = 'allexamfea_values_sample%s.pkl' % (sample)
    if not saveres:
        featuresresanme=None
    x_train, x_test, y_train, y_test=exam2traindata_(examples, vecdic_users, vecdic_fns, fn_features,
                                                     resname=featuresresanme,encoding=encoding,sample=sample)
    return x_train,x_test,y_train,y_test

if __name__ == '__main__':
    # exam2traindata(encoding=False,sample='up',saveres=True)
    print('ok')