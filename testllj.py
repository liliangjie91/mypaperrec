# -*- coding: utf-8 -*-
__author__ = 'lljzhiwang'
import  time
import threading
# from Queue import Queue
import util_common as util

# kws = [u"石油" , u"计算机" , u"网络" , u"楼房" , u"鼠标" , u"咖啡"]
#
# for i in kws:
#     print i
# searchingword = u"石油"
# print searchingword
# # print a
# def worker():
#     print 'hello'
#     time.sleep(2)
#
# th = [threading.Thread(target=worker) for _ in xrange(5)]
# for thread in th:
#     thread.start()

def reverse(s):
    s=list(s)
    i,j=0,len(s)-1
    while j>i:
        s[i],s[j]=s[j],s[i]
        i+=1
        j-=1
    s=''.join(s)
    return s

def rev2(s,n):
    return reverse(reverse(s[:n])+reverse(s[n:]))

def printurllist():
    wl = util.load2list('./usearchl_181112_10w.log',get1column=1)
    wl = list(set(wl))
    wl=wl[:3000]
    with open('./tmpunionlocal.txt','w') as f:
        for w in wl:
            if len(w)>1:
                # f.write("http://recom.cnki.net/api/recommendations/words/union?w=%s\n" %w.encode('utf8'))
                f.write("http://127.0.0.1:8081/api/recommendations/papers/union?id=%s\n" % w.strip().encode('utf8'))
                # f.write("http://recom.cnki.net/api/recommendations/papers/itembased?id=%s\n" % w.strip().encode('utf8'))
                # f.write("http://recom.cnki.net/api/recommendations/papers/contentbased?id=%s\n" % w.strip().encode('utf8'))
                # f.write("http://my.cnki.net/RCDService/api/MyPapers/downloadHistory?id=%s\n" % w.encode('utf8'))

#
def qsort(l,start,end):
    if start>=end:
        return
    ll,lr=start,end
    tmpv=l[start]
    while ll<lr:
        while ll<lr and l[lr]>=tmpv:
            lr-=1
        if ll==lr:
            break
        else:
            l[ll],l[lr]=l[lr],l[ll]

        while ll<lr and l[ll]<=tmpv:
            ll+=1
        if ll==lr:
            break
        else:
            l[ll], l[lr] = l[lr], l[ll]
    qsort(l,start,ll-1)
    qsort(l,lr+1,end)

if __name__ == '__main__':
    # print rev2('abcdef',2)
    l=[5,4,3,6,8,2]
    qsort(l,0,len(l))
    print(l)

