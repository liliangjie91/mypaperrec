# encoding=utf-8
import ConfigParser

# 读取配置文件
cf = ConfigParser.ConfigParser()
cf.read("./config.ini")
# 输出文本的路径，为防止中文路径乱码，使用UNICODE编码
files_path = unicode(cf.get("file", "files_path"), 'utf8')
output_txt_path = unicode(cf.get("file", "output_txt_path"), 'utf8')
output_xls_path = unicode(cf.get("file", "output_xls_path"), 'utf8')
output_csv_path = unicode(cf.get("file", "output_csv_path"), 'utf8')
input_data_path = unicode(cf.get("file", "input_data_path"), 'utf8')
input_expert_path = unicode(cf.get("file", "input_expert_path"), 'utf8')
input_machine_path = unicode(cf.get("file", "input_machine_path"), 'utf8')
input_rouge_path = unicode(cf.get("file", "input_rouge_path"), 'utf8')
path = unicode(cf.get("file", "path"), 'utf8')
save_path = unicode(cf.get("file", "save_path"), 'utf8')
compute_idf_path = unicode(cf.get("file", "compute_idf_path"), 'utf8')
evaluated_path = unicode(cf.get("file", "evaluated_path"), 'utf8')


dict_path = unicode(cf.get("dict", "dict_path"), 'utf8')
otherdict_folder=unicode(cf.get("dict", "otherdict_folder"), 'utf8')
stop_words_path = unicode(cf.get("dict", "stop_words_path"), 'utf8')
kbase_dict_path = unicode(cf.get("dict", "kbase_dict_path"), 'utf8')
idf_dict_path = unicode(cf.get("dict", "idf_path"), 'utf8')
jieba_dict_path = unicode(cf.get("dict", "jieba_dict_path"), 'utf8')

path_list = [input_data_path, output_xls_path, input_expert_path, input_machine_path, output_csv_path, output_txt_path,
             evaluated_path]
