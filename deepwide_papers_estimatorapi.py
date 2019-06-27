import tensorflow as tf
import numpy as np
import os
import pandas as pd
from gensim.models.doc2vec import Doc2Vec,TaggedDocument
import time

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
pd.set_option('display.width',None)
pd.set_option('display.max_colwidth',150)
pd.set_option('display.max_columns', 200)

datapath = r'C:/Users/lx/Desktop/Machine Learning/myPaperRrec/myPaperRrec/data'
useridcolumn=[]
_CSV_COLUMNS =[]
_CSV_COLUMN_DEFAULTS=[]
for i in range(100):
    useridcolumn.append("id"+str(i))
_CSV_COLUMNS.append("paperid")
_CSV_COLUMN_DEFAULTS.append([''])
_CSV_COLUMNS.append("label")
_CSV_COLUMN_DEFAULTS.append([0])
_CSV_COLUMNS.append("userid")
_CSV_COLUMN_DEFAULTS.append([''])
for i in range(3,103):
    _CSV_COLUMNS.append("id" + str(i-3))
    _CSV_COLUMN_DEFAULTS.append([0.1])
_CSV_COLUMNS.append("fe1")
_CSV_COLUMN_DEFAULTS.append([0])
_CSV_COLUMNS.append("fe2")
_CSV_COLUMN_DEFAULTS.append([0])
_CSV_COLUMNS.append("fe5")
_CSV_COLUMN_DEFAULTS.append([''])
_CSV_COLUMNS.append("fe6")
_CSV_COLUMN_DEFAULTS.append([''])
_CSV_COLUMNS.append("fe8")
_CSV_COLUMN_DEFAULTS.append([0])
_CSV_COLUMNS.append("fe9")
_CSV_COLUMN_DEFAULTS.append([0])


modelfolder = datapath + r'/model/testlx'
sample_pos=datapath+r'/highq_5w/sample_highq5w_posi.txt'
sample_neg=datapath+r'/highq_5w/sample_highq5w_neg.txt'
paperfeature=datapath+r'/highq_5w/fn18_5w_features.txt'
traindata=datapath+r'/highq_5w/traindata_l2norm_x100.csv'
cvdata=datapath+r'/highq_5w/cvdata_l2norm_x100.csv'

def generatedata():
    df_paperfeature=pd.read_csv(paperfeature,sep='\s+',header=None,error_bad_lines=False,usecols=[0,1,2,5,6,8,9])
    df_paperfeature.columns=['paperid','fe1','fe2','fe5','fe6','fe8','fe9',]
    def fe5(str):
        val=str.split(';')
        if str=='nan':
            return '0200000'
        if val:
            return val[0]
        return str

    df_paperfeature['fe5']=df_paperfeature['fe5'].astype(str).map(fe5)
    df_paperfeature.fillna(0)


    df_sample_pos=pd.read_csv(sample_pos,sep='\s+',header=None,error_bad_lines=False,nrows=100000)
    df_sample_neg=pd.read_csv(sample_neg,sep='\s+',header=None,error_bad_lines=False,nrows=100000)
    df_sample=pd.concat([df_sample_neg,df_sample_pos],ignore_index=True)

    df_sample['userid']=df_sample.iloc[:,0].map(lambda x :x.split('+')[0])
    df_sample[0]=df_sample[0].map(lambda x:x.split('+')[1])
    df_sample.columns=['paperid','label','userid']
    print(df_sample.shape)


    modelget = Doc2Vec.load(modelfolder + '/lx1_size100_l2norm.model')
    useridlist=modelget.docvecs.offset2doctag
    useridarray=np.array(useridlist)
    df_useridarray=pd.DataFrame(useridarray,columns=['userid'])
    vecarray=modelget.docvecs.vectors_docs
    df_uservec=pd.DataFrame(vecarray,columns=useridcolumn)
    df_uservec=df_uservec.multiply(100)
    #df_uservec=df_uservec.astype(float)
    df_uservec=pd.concat([df_useridarray,df_uservec],axis=1)
    del useridlist,useridarray,vecarray

    df_sample=pd.merge(df_sample,df_uservec,how='left',on='userid')
    #print(df_sample[df_sample.isnull().values==False].shape)
    #print(modelget['3160718100802186423'])
    df_sample=pd.merge(df_sample,df_paperfeature,how='left',on='paperid')

    df_sample=df_sample.sample(frac=1.0).reset_index().drop(['index'],axis=1)
    print(df_sample.shape)
    df_train=df_sample.loc[0:120000]
    df_cv=df_sample.loc[120001:199999]
    del df_sample
    df_train=df_train.dropna(axis=0,how='any')
    df_train[['fe8','fe9','fe1','fe2','label']]=df_train[['fe8','fe9','fe1','fe2','label']].astype(int)
    df_train[['fe5','fe6']] = df_train[['fe5','fe6']].astype(str)
    df_cv=df_cv.dropna(axis=0,how='any')
    df_cv[['fe8','fe9','fe1','fe2','label']]=df_cv[['fe8','fe9','fe1','fe2','label']].astype(int)
    df_cv[['fe5','fe6']] = df_cv[['fe5','fe6']].astype(str)
    print(df_train.shape)
    print(df_train.head(2))

    df_train.to_csv(traindata,header=False,index=False)
    df_cv.to_csv(cvdata,header=False,index=False)

def inputfile(filepath,epochs,batchsize=512,shuffle=False):
    def try1(line):
    #    dict={}
        columns = tf.decode_csv(line,record_defaults=_CSV_COLUMN_DEFAULTS)
    #    dict[str(ab+1)]=line
        features = dict(zip(_CSV_COLUMNS, columns))
        labels = features.pop('label')
#        features.pop('userid')
        return features, tf.equal(labels,1)
#        return  features,features['workclass']

    dataset2=tf.data.TextLineDataset(filepath).map(try1)
    #textlinedataset将文件按行读入，返回dataset， 每行内容做为一个元素,类型为str类型的tensor
    #使用map后每个元素，即每行的str类型的tensor，变为（dict，tensor）
    # ，dict的key为特征，value为特征的值，为str类型tensor。tensor为bool型。各行均map后字典应该是自动根据value做合并
    if shuffle:
        dataset2=dataset2.shuffle(buffer_size=30000)
    dataset2=dataset2.repeat(epochs)
    dataset2=dataset2.batch(batchsize)

    iter=dataset2.make_one_shot_iterator()
    feature,label=iter.get_next()
    return feature,label

def sessiontry():
    with tf.Session() as sess:
        feature1, label1 = inputfile(traindata,epochs=1)
        for i in range(10):
            try:
                output1 = sess.run(label1)
                print(output1)
            except tf.errors.OutOfRangeError:
                break
uservec=[]
def tftrain():
    for i in range(3,103):
        uservec.append(tf.feature_column.numeric_column(_CSV_COLUMNS[i]))
    paperid=tf.feature_column.categorical_column_with_hash_bucket('paperid',hash_bucket_size=100)
    fe1=tf.feature_column.numeric_column('fe1')#总引文数量
    fe2=tf.feature_column.numeric_column('fe2')#外语引文数量
    fe8=tf.feature_column.numeric_column('fe8')#页数
    fe9=tf.feature_column.numeric_column('fe9')#下载频次
    fe5=tf.feature_column.categorical_column_with_hash_bucket('fe5',hash_bucket_size=50)#机构代码
    fe6 = tf.feature_column.categorical_column_with_hash_bucket('fe6', hash_bucket_size=50)#出版物代码
    fe9_buckets = tf.feature_column.bucketized_column(fe9, boundaries=[5,10,20,40,70,100,150,200,300,450,650,900,1500,3000])
    deepcolumn=[fe1,fe2,fe8,tf.feature_column.indicator_column(fe9_buckets),tf.feature_column.indicator_column(fe5),tf.feature_column.indicator_column(fe6),tf.feature_column.embedding_column(paperid, dimension=20)]+uservec
    basecolumn=[paperid,fe1,fe9_buckets]+uservec
    model = tf.estimator.DNNLinearCombinedClassifier(linear_feature_columns=basecolumn,
                                                     dnn_feature_columns=deepcolumn, dnn_hidden_units=[200, 300, 100])
    for i in range(3):
        print("------cycle %d trainging start:-----------"%i)
        tstart=time.time()
        model.train(input_fn=lambda: inputfile(filepath=traindata, shuffle=True, batchsize=50, epochs=2))
        print("------cycle %d trainging end:------using time: %.2f-----"%(i,time.time()-tstart))
        tstart=time.time()
        results = model.evaluate(input_fn=lambda: inputfile(filepath=cvdata, epochs=1))
        print("------cycle %d evaluate end:------using time: %.2f-----" % (i, time.time() - tstart))
        for key in sorted(results):
            print("{0:20}: {1:.4f}".format(key, results[key]))
        print("----cycle %d end-----"%i)

if __name__ == '__main__':
#    generatedata()
#    ceshi()
#    sessiontry()
    tftrain()
#    print(len(_CSV_COLUMN_DEFAULTS))