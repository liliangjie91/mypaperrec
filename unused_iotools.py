# encoding=utf-8
import codecs
import os
import re

from pandas import ExcelWriter

from tc_conversion.langconv import *
from tc_conversion.full_half_conversion import *


def open_folder(path):
    """
    打开一个文件夹下所有的目录文件
    :param path: 文件夹路径
    :type path: string or sequence of string
    :return: 保存当前文件夹下文件路径
    :rtype: unicode string
    """
    file_list = list()
    rec_path = list()
    files = os.listdir(path)
    for f in files:
        if os.path.isfile(path + '/' + f):
            file_list.append(f)
    for i in range(len(file_list)):
        rec_path.append(path + '/' + file_list[i])
    return rec_path


def read_rec_data(path):
    """
    读取REC文本文件
    :param path: REC文件所在路径
    :type path: unicode string
    :returns:篇名，正文组成的列表以及中文摘要
    """
    doc = []
    # abstract = ''
    date = ''
    periodical_title = ''
    impact_factor = ''
    download_frequency = ''
    cite_frequency = ''
    filename = ''
    fulltext_count = 0

    with codecs.open(path, 'rU', 'gb18030', errors='replace') as f:  # REC文件为gb18030编码
        for line in f:
            line = line.strip()
            line = str_full2half(line)        # 检测全角字符，将全角字符转换成半角
            line = Converter('zh-hans').convert(line)         # 繁体字检测，将繁体字转换成简体字
            if line.find(u'<篇名>=') == 0:
                title = line[5:]
            # elif line.find(u'<中文摘要>=') == 0:
            #     abstract = line[7:]
            elif line.find(u'<出版日期>=') == 0:
                date = line[7:]
            elif line.find(u'<中英文刊名>=') == 0:
                periodical_title = line[8:]
            elif line.find(u'<影响因子>=') == 0:
                impact_factor = line[7:]
            elif line.find(u'<下载频次>=') == 0:
                download_frequency = line[7:]
            elif line.find(u'<被引频次>=') == 0:
                cite_frequency = line[7:]
            elif line.find(u'<文件名>=') == 0:
                filename = line[6:]
            elif line.find(u'<全文>=') == 0:
                title_index = line.find(title + '@')  # 去掉全文末尾的标题、作者、摘要、引文等
                if title_index != -1:
                    text = line[5:title_index]
                else:
                    text = line[5:]
                fulltext_count = len(text)
                doc.append((title, text))
    # return doc, abstract
    return doc, download_frequency, cite_frequency, date, periodical_title, impact_factor, filename, fulltext_count


def write_txt_data(df, file_path, sig):
    """
    将DataFrame输出保存到txt文件，以制表符分隔
    :param df: 数据DataFrame
    :type df: DataFrame
    :param file_path: 输出文件路径
    :type file_path: string or sequence of string
    :param sig: 篇名
    :type sig: unicode string
    """
    new_file_path = file_path + '/' + '%s.txt' % sig
    df.to_csv(new_file_path, sep='\t', header=False, index=False, mode='a', encoding='utf8')


def write_xls_data(list_dfs, file_path, sig, list_title=None):
    """
    将多个DataFrame输出保存到一个Excel文件中
    :param list_dfs: 多个DataFrame列表
    :type list_dfs: DataFrame
    :param file_path: 输出文件路径
    :type file_path: string or sequence of string
    :param sig: 篇名
    :type sig: unicode string
    :param list_title: 对应的篇名列表，默认为空
    :type list_title: list
    """
    new_file_path = file_path + '/' + '%s.xlsx' % sig
    with ExcelWriter(new_file_path) as writer:
        for i, df in enumerate(list_dfs):
            if list_title is None:
                df.to_excel(writer, 'sheet%s' % i, encoding='utf8', index=False)
            else:
                title = re.sub(r'[\\*?:/\[\]]', '', list_title[i])  # 去除标题中的不规范符号
                if len(title) > 31:  # 标题最长为31
                    title = title[0:31]
                df.to_excel(writer, sheet_name=title, encoding='utf8', index=False)


def read_data(path):
    # def readData(level,path):
    """
    加载multilingpilot2013数据集的中文文档
    # :param level: REC文件目录级别
    # :type level: string or sequence of string
    :param path: REC文件所在路径
    :type path: string or sequence of string
    :return:篇名，正文组成的列表
    """
    doc = []  # 返回数据集正文
    # dir_list = []    # 所有文件夹，第一个字段是次目录的级别
    file_list = []  # 返回列表，包含当前路径级下所有目录文件的名称集合

    files = os.listdir(path)
    # dir_list.append(str(level))   # 添加目录级别
    for f in files:
        # if os.path.isdir(path + '/' + f):    # 排除隐藏文件夹，添加非隐藏文件夹
        #     if(f[0] == '.'):pass
        #     else:
        #         dirList.append(f)
        if os.path.isfile(path + '/' + f):
            file_list.append(f)
    for fl in file_list:
        tmp_list = []
        with codecs.open(path + '/' + fl, 'rU', 'gb18030', errors='replace') as f:
            for line in f.readlines():
                line = line.strip()
                tmp_list.append(line)
        tmp_doc = ''.join(tmp_list)  # 格式转换
        doc.append(tmp_doc)
    return doc


def save_rec_files(rec_path, file_path, num=1):
    """
    文件批处理，将一个保存多个txt的rec文本，拆分成多个单篇rec文本，保存到相关路径下
    :param rec_path: 批量rec文本路径
    :type rec_path:  unicode string
    :param file_path: 保存分解之后单个rec文本的路径
    :type file_path: unicode string
    :param num: 甄别句子时使用的甄别长度（默认状态下，num=6）
    :type num: int
    特殊说明：
    文件写入时编码要和read_rec_data方法中的编码格式保持一致
    """
    with codecs.open(rec_path, 'rU', 'gb18030', errors='replace') as f:  # REC文件为gb18030编码
        count = 1
        str1_content = ''
        str2_content = None
        title = ''
        for line in f:
            line = line.strip()
            if line.find(u'<REC>') == 0:
                str2_content = str1_content
                str1_content = ''               # 字符串置空操作
                str1_content += '%s\n' % line[:]
            elif line.find(u'<篇名>=') == 0:
                title = line[5:]
                str1_content += '%s\n' % line[:]
            elif line.find(u'<中文摘要>=') == 0:
                str1_content += '%s\n' % line[:]
            elif line.find(u'<全文>=') == 0:
                title_index = line.find(title + '@')  # 去掉全文末尾的标题、作者、摘要、引文等
                new_line = line[5:title_index]
                cnt = 0
                delimiters = u'。'               # 可以修改成正则表达式匹配多符号
                pos = new_line.find(delimiters)
                if pos != -1:
                    cnt += 1
                while pos != -1:
                    new_line = new_line[pos+1:]
                    pos = new_line.find(delimiters)
                    if pos != -1:
                        cnt += 1
                if cnt >= num:
                    if title_index != -1:
                        str1_content += '%s\n' % line[:title_index]
                    else:
                        str1_content += '%s\n' % line[:]
                else:
                    str1_content = ''
            else:
                # if line.find(u'<') == 0:        # 待修改（暂时）
                str1_content += '%s\n' % line
            if str2_content and str2_content.find(u'<全文>=') != -1:
                fl = open("%s/%s.txt" % (file_path, count), 'w')
                fl.write(str2_content.encode('gb18030', 'replace'))  # 此处的编码格式与read_rec_data保持一致
                fl.close()
                str2_content = None
                count += 1
        if str1_content and str1_content.find(u'<全文>=') != -1:
                fl = open("%s/%s.txt" % (file_path, count), 'w')
                fl.write(str1_content.encode('gb18030', 'replace'))  # 此处的编码格式与read_rec_data保持一致
                fl.close()


def remove_files(path_list):
    """
    自动删除指定文件夹下的所有文件
    :param path_list: 待删除文件的对应文件夹列表
    :type path_list: list
    """
    for i in range(len(path_list)):
        root_dir = "%s\%s" % (os.getcwd(), path_list[i])
        fl = os.listdir(root_dir)
        for f in fl:
            file_path = os.path.join(root_dir, f)
            if os.path.isfile(file_path):
                os.remove(file_path)


def add_abstract_into_rec(rec_path, file_path):
    """
    将批量的REC语料添加机器摘要字段信息并保存相关路径下
    :param rec_path: 批量rec文本路径
    :type rec_path:  unicode string
    :param file_path: 保存分解之后单个rec文本的路径
    :type file_path: unicode string

    特殊说明：
    文件写入时编码要和read_rec_data方法中的编码格式保持一致
    调用示例：
    ->>>IOTools.add_abstract_into_rec(Path.files_path, Path.input_data_path)
    结果将导入的REC文本语料添加机器摘要字段信息
    """
    from abstract import Abstract
    mod = Abstract()
    filename = 'add_abstract'
    with codecs.open(rec_path, 'rU', 'gb18030', errors='replace') as f:  # REC文件为gb18030编码
        str1_content = ''
        str2_content = None
        title = ''
        fulltext = ''
        for line in f:
            line = line.strip()
            if line.find(u'<REC>') == 0:
                str2_content = str1_content
                str1_content = ''               # 字符串置空操作
                str1_content += '%s\n' % line[:]
            elif line.find(u'<篇名>=') == 0:
                title = line[5:]
                str1_content += '%s\n' % line[:]
            elif line.find(u'<全文>=') == 0:
                title_index = line.find(title + '@')  # 去掉全文末尾的标题、作者、摘要、引文等
                str1_content += '%s\n' % line[:title_index]
                fulltext = line[5:title_index]
            else:
                str1_content += '%s\n' % line
            if title and fulltext:
                machine_abstract = mod.get_machine_abstract(title, fulltext)
                field = u'<机器摘要>='
                str1_content += '%s%s\n\n' % (field, machine_abstract)
                title = ''         # 当一篇语料提取摘要结束之后，将title和fulltext字段置空，防止机器摘要重复抽取
                fulltext = ''
            if str2_content:
                if str2_content.find(u'<机器摘要>') == -1:    # 自动甄别掉主要字段缺失的文本不写入REC文档中
                    pass
                else:
                    fl = open("%s/%s.txt" % (file_path, filename), 'a')  # 文件以追加的方式写入
                    fl.write(str2_content.encode('gb18030', 'replace'))  # 此处的编码格式与read_rec_data保持一致
                    fl.close()
                    str2_content = None
        if str1_content:
            fl = open("%s/%s.txt" % (file_path, filename), 'a')
            fl.write(str1_content.encode('gb18030', 'replace'))
            fl.close()
