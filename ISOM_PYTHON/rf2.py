import re
from collections import Counter
import dict_sort as ds  # 字典排序，自己写的
from collections import defaultdict # defaultdict(list)用
import Isomorphic_literal as isl
import itertools
import operator  ## operator.eq用
import other_fun as of




##把R2分成两部分，一部分是pair_literal_RQ（包含v的所有元素），另一部分是R2 = 原R2 - pair_literal_RQ
##input : R2 =  ['P1(x1,x2,x3)', 'P1(x2,x3,x1)', 'P1(a8,x1,x2)']
##output:  pair_literal_RQ =  [['P1(a8,x1,x2)']]  (v = 'a8'), R2 = ['P1(x1,x2,x3)', 'P1(x2,x3,x1)']
def split_withv_withoutv(R2 , v,  pair_literal_RQ):
    print('\nIn fun split_withv_withoutv')
    pair_literal_RQ_sub = []
    R2_p = []
    reg1 = '^((?!(' + v + '\d+)).)*$'
    ##  .* 代表匹配除换行符之外的所有字符。
    reg2 = '.*' + v + '.*'
    reg3 = '(?='+reg2+')(?='+reg1+')' # 包含x1但是不包含 x1\d+，例如不包含x10
    
    
    for i in range(len(R2)):                        
##        print('i = ', i)
        ret = re.search(reg3, R2[i])
##        print('ret = ', ret)
##        print('type(ret) =', type(ret))
        if isinstance(ret,re.Match):            
            pair_literal_RQ_sub.append(R2[i])
            print('pair_literal_RQ_sub = ', pair_literal_RQ_sub)    
        else:
            R2_p.append(R2[i])
    pair_literal_RQ.append(pair_literal_RQ_sub)
    print('pair_literal_RQ = ', pair_literal_RQ)                 
##    R2 = list(filter(lambda x:x.find(v)==-1, R2))                        
    print('without v:', R2_p)
    print('Out of fun split_withv_withoutv\n')
    return pair_literal_RQ, R2_p


##在R2中包含有a的元素挑出来，放到一个新的列表中，把不含a的元素放另一个列表中
##input: R2 =  ['P4(x1,a2,x3,x4)', 'P4(x3,x1,a4,x4)', 'P4(x4,x1,x8,x3)', 'P4(a8,a2,a4,x4)', 'P4(a4,a2,x8,x3)']
##Q2 =  ['P4(a7,a2,a5,a6)', 'P4(a5,a7,a4,a6)', 'P4(a6,a7,a3,a5)', 'P4(a8,a2,a4,a6)', 'P4(a4,a2,a3,a5)']
##mapping_n =  {'x5': 'a1', 'x2': 'a2', 'x6': 'a8', 'x7': 'a4'}
##output: R2 =  [['P4(x1,a2,x3,x4)', 'P4(x3,x1,a4,x4)', 'P4(a8,a2,a4,x4)', 'P4(a4,a2,x8,x3)'], ['P4(x4,x1,x8,x3)']]
## Q2 =  [['P4(a7,a2,a5,a6)', 'P4(a5,a7,a4,a6)', 'P4(a8,a2,a4,a6)', 'P4(a4,a2,a3,a5)'], ['P4(a6,a7,a3,a5)']]
def divide_by_unif(R2,Q2,mapping_n):
##    分R2
    R2_vr = []      ## v - 字典的值 ，    
    for ir2 in range(len(R2)):
        if 'a' in R2[ir2]:
            R2_vr.append(R2[ir2])
    print('R2_vr = ', R2_vr)
    R2_without_vr = list(set(R2) - set(R2_vr))
    print('R2_without_vr = ', R2_without_vr)
##    分Q2 
    Q2_vr = []
    Q2_vl = list(mapping_n.values())
##            print('Q2_vl = ', Q2_vl)
    for iq2 in range(len(Q2)):
##                print (Q2[iq2])
        for iq2_vl in Q2_vl:
            if  (iq2_vl in Q2[iq2] and Q2[iq2] not in Q2_vr):                        
                Q2_vr.append(Q2[iq2])
    print('Q2_vr = ', Q2_vr)
    Q2_without_vr = list(set(Q2) - set(Q2_vr))
    print('Q2_without_vr = ', Q2_without_vr)
    return [R2_vr, R2_without_vr], [Q2_vr, Q2_without_vr]


##更新合一子，check_result_pair是检查冲突后的结果，True或False
##c_temp_u 是字典，mapping_n是字典

def update_mapping(check_result_pair, c_temp_u, mapping_n):
    print('\nIn fun update_mapping')
##    print('c_temp_u = ', c_temp_u)
##            如果冲突，该函数结束
    if (check_result_pair  == False):
        print('Result : no.')
        print('Out of fun update_mapping\n')
        return {},{}
##            13、否则，不冲突，得合一子
    else:
        if (isinstance(c_temp_u,list)):
            c_temp_u = c_temp_u[0]
        print('c_temp_u = ', c_temp_u)
##              查字典遍历的时候删除键=值的键值对                
        for ktu in list(c_temp_u):      
            if ktu == c_temp_u[ktu]:
##                        print('ktu, vtu  = ', ktu, vtu  )                      
                del c_temp_u[ktu]     
        mapping_n.update(c_temp_u)
        print('mapping_n = ', mapping_n)
##        print('c_temp_u = ', c_temp_u)
        print('Out of fun update_mapping\n')
        return mapping_n, c_temp_u

##先检查c_temp_u中和mapping的内容是否有冲突，如果有冲突，从c_temp_u中删除有冲突的字典
##    下面的例子中c_temp_u[1]与mapping有冲突，返回时删除， 只返回c_temp_u[0]
##    input: mapping =  {'x6': 'a5', 'x5': 'a3', 'x2': 'a4', 'x4': 'a6',
##            'x1': ['a1', 'a7'], 'x7': ['a1', 'a7'], 'x3': ['a2', 'a8'], 'x8': ['a2', 'a8']}
##c_temp_u =  [{'x2': 'a4', 'a5': 'a5', 'x1': 'a1', 'x4': 'a6', 'x8': 'a8', 'x7': 'a7', 'x3': 'a2'}, \
##             {'x2': 'a6', 'a5': 'a5', 'x1': 'a8', 'x4': 'a4', 'x8': 'a1', 'x7': 'a2', 'x3': 'a7'}]
##    output -  c_temp_u =  [{'x2': 'a4', 'a5': 'a5', 'x1': 'a1', 'x4': 'a6', 'x8': 'a8', 'x7': 'a7', 'x3': 'a2'}]
    
##两个字典间根据相同的键筛选其对应的值
##  input:  mapping =  {'x6': 'a5', 'x5': 'a3', 'x2': 'a4', 'x4': 'a6',
##            'x1': ['a1', 'a7'], 'x7': ['a1', 'a7'], 'x3': ['a2', 'a8'], 'x8': ['a2', 'a8']}
##             c_temp_u =  [{'x2': 'a4', 'a5': 'a5', 'x1': 'a1', 'x4': 'a6', 'x8': 'a8', 'x7': 'a7', 'x3': 'a2'}, \
##             {'x2': 'a6', 'a5': 'a5', 'x1': 'a8', 'x4': 'a4', 'x8': 'a1', 'x7': 'a2', 'x3': 'a7'}]
##  output : c_temp_u =  [{'x2': 'a4', 'a5': 'a5', 'x1': 'a1', 'x4': 'a6', 'x8': 'a8', 'x7': 'a7', 'x3': 'a2'}]
def cheak_conflicts_mapping_ctu(mapping, c_temp_u):
##    print('c_temp_u = ', c_temp_u)
    comp_r = []
    for ict in range(len(c_temp_u)):
        comp_r_t = []
##        print('\nict = ', ict)
        comp_r_t_mc = list(map(lambda k: (mapping[k], c_temp_u[ict][k]), {*mapping} & {*c_temp_u[ict]}))        
##        print('comp_r_t_mc = ', comp_r_t_mc)
        for jcr in range(len(comp_r_t_mc)):
##            print('jcr = ', jcr)
##            print('comp_r_t_mc[jcr] = ', comp_r_t_mc[jcr])
            if isinstance(comp_r_t_mc[jcr][0], list) and comp_r_t_mc[jcr][1] in comp_r_t_mc[jcr][0]:
                comp_r_t.append(True)
            elif isinstance(comp_r_t_mc[jcr][0], str) and comp_r_t_mc[jcr][1] == comp_r_t_mc[jcr][0]:
                comp_r_t.append(True)      
            else:
                comp_r_t.append(False)
##        print('comp_r_t = ', comp_r_t)
        if False in comp_r_t:
            comp_r.append(False)
        else:
            comp_r.append(True)
##    print(comp_r)

    for icp in range(len(comp_r)-1,-1,-1):
##        print('icp = ', icp)
        if comp_r[icp] == False:
##            print('in if')
            del c_temp_u[icp]
    return c_temp_u

##         12、 否则，两个列表不相等，查找两个列表R2、Q2之间的公共元素，并删除，
##以减少列表的长度，进而缩短比较时间
## input - R2 =  ['P1(a1,a4,a2)', 'P1(a2,a1,a6)', 'P1(a2,a6,x5)', 'P1(a2,a1,x5)', 'P1(a4,a6,a1)',
##'P1(a4,a7,a6)', 'P1(a4,a7,a1)', 'P1(a6,a2,a4)', 'P1(a6,a4,a8)', 'P1(a6,a8,a2)',
##'P1(x5,a2,a8)', 'P1(a7,a8,a4)', 'P1(a8,a6,a7)', 'P1(a8,x5,a6)', 'P1(a8,x5,a7) '] 
## Q2 =  ['P1(a1,a4,a2)', 'P1(a2,a1,a6)', 'P1(a2,a6,a3)', 'P1(a2,a1,a3)', 'P1(a3,a2,a8)',
##'P1(a4,a6,a1)', 'P1(a4,a7,a6)', 'P1(a4,a7,a1)', 'P1(a6,a2,a4)', 'P1(a6,a4,a8)',
##'P1(a6,a8,a2)', 'P1(a7,a8,a4)', 'P1(a8,a3,a6)', 'P1(a8,a6,a7)', 'P1(a8,a3,a7)']
## output - common_elements =  ['P1(a7,a8,a4)', 'P1(a2,a1,a6)', 'P1(a6,a4,a8)', 'P1(a6,a2,a4)',
##'P1(a4,a7,a1)', 'P1(a4,a6,a1)', 'P1(a1,a4,a2)', 'P1(a6,a8,a2)', 'P1(a4,a7,a6)', 'P1(a8,a6,a7)']
##In fun find_com_del R2 =  ['P1(a2,a6,x5)', 'P1(a2,a1,x5)', 'P1(x5,a2,a8)', 'P1(a8,x5,a6)', 'P1(a8,x5,a7) '] 
## Q2 =  ['P1(a2,a6,a3)', 'P1(a2,a1,a3)', 'P1(a3,a2,a8)', 'P1(a8,a3,a6)', 'P1(a8,a3,a7)']
 
def find_com_del(R2,Q2):
    common_elements = list(set(R2).intersection(Q2))
##    print('common_elements = ', common_elements)
    if len(common_elements)>0:
        for ice in range(len(common_elements)):
        ##    print('i = ', i)    
            R2 = list(filter(lambda x: x != common_elements[ice], R2))    
##            print('R2 = ', R2)
            Q2 = list(filter(lambda x: x != common_elements[ice], Q2))    
##            print('Q2 = ', Q2)
        print('In fun find_com_del R2 = ', R2, '\n', 'Q2 = ', Q2)
    else:
        print('\nNo common elements')
    
    return R2, Q2, common_elements

def get_first_mapping(R, Q):
##    print('R = ', R,'\n', 'Q= ',Q)
    ch1, ch2 = of.get_chrc(R,Q)
##    print('ch1, ch2 = ',ch1, ch2)
    oc1, oc2 = of.get_occurr(ch1,ch2)
    print('\noc1, oc2 = ', oc1, oc2)
    oc1 = ds.sort_val(oc1)
##    print('oc1 = ', oc1)

##3、 交换字典的键值对+根据字典的值 - 列表的长度对字典升序
    char_f1_after_kvswap = of.kvswap(ch1)
##    print('\nchar_f1_after_kvswap = ', dict(char_f1_after_kvswap))
##    {11: ['x4'], 9: ['x2'], 8: ['x3', 'x10'], 6: ['x1', 'x7'], 5: ['x5'], 4: ['x6']}
##    print('len(dict(char_f1_after_kvswap)) = ', len(dict(char_f1_after_kvswap)))
    char_f1_after_kvswap = dict(sorted(char_f1_after_kvswap.items(), key=lambda x: -len(x[1]), reverse=True))
    print('after sort char_f1_after_kvswap = ', char_f1_after_kvswap)
    char_f2_after_kvswap = of.kvswap(ch2)
##    print('char_f2_after_kvswap = ', dict(char_f2_after_kvswap))
    char_f2_after_kvswap = dict(sorted(char_f2_after_kvswap.items(), key=lambda x: -len(x[1]), reverse=True))
    print('after sort char_f2_after_kvswap = ', char_f2_after_kvswap)
       
    
##4、 把两个有相同键的字典合并为一个新列表
    mapping = of.conn_dict(char_f1_after_kvswap,char_f2_after_kvswap)
    
##    mapping_list = []
##    mapping_list = conn_list(char_f1_after_kvswap,char_f2_after_kvswap)
    print('\nafter_conn_list_mapping = ', mapping)
    return mapping


####字典遍历时，根据要求（键值相等）删除键值对
##input - 字典列表，eg:c_temp_u =  [{'x17': 'a11', 'a03': 'a03', 'x7': 'a18'}, {'x17': 'a18', 'a03': 'a03', 'x7': 'a11'}]
##output - 字典列表，eg: c_temp_u =  [{'x17': 'a11', 'x7': 'a18'}, {'x17': 'a18', 'x7': 'a11'}]
def del_kv_dict(c_temp_u):    
    for i in range(len(c_temp_u)):
        for key in list(c_temp_u[i]):
            if key == c_temp_u[i][key]:
                del c_temp_u[i][key]
##        print(c_temp_u[i])
    return c_temp_u


####字典遍历时，根据要求（键（常量，eg:a1）值（常量，eg: a2）不相等）删除字典
##input - 字典列表，eg:c_temp_u =[{'a26': 'a26', 'x7': 'a18', 'x17': 'a11', 'x12': 'a06'}, \
##           {'a26': 'a11', 'x7': 'a06', 'x17': 'a26', 'x12': 'a18'}]
##output - 字典列表，eg: [{'a26': 'a26', 'x7': 'a18', 'x17': 'a11', 'x12': 'a06'}]
def del_dict(c_temp_u):    
    for i in range(len(c_temp_u)):
        for key in list(c_temp_u[i]):
    ##        print('key = ', key)
            if 'a' in key and 'a' in c_temp_u[i][key] and key!= c_temp_u[i][key]:
    ##            print(key, c_temp_u[i][key])
                del c_temp_u[i]
##    print(c_temp_u)
    return c_temp_u


##如果列表ks的元素出现在R2中，则返回R2中相应的文字(列表)
##input - ks = ['x17', 'x7'], R2 =  ['P10(x3,x4)', 'P10(a26,x7)', 'P10(x8,x9)', 'P10(x9,x10)', 'P10(x11,x12)', \
##       'P10(x10,x14)', 'P10(x15,x16)', 'P10(x18,a10)', 'P10(a28,x16)', 'P10(x19,x4)',\
##       'P10(x21,x15)', 'P10(x16,x22)', 'P10(x17,x12)']
##output -['P10(a26,x7)', 'P10(x17,x12)']
def get_lits(ks, R2):
    x_R2 = []
    for ir2 in range(len(R2)):
        for jx in range(len(ks)):
            ve = ks[jx]
            reg1 = '^((?!(' + ve + '\d+)).)*$'
            ##  .* 代表匹配除换行符之外的所有字符。
            reg2 = '.*' + ve + '.*'
            reg3 = '(?='+reg2+')(?='+reg1+')' # 包含x1但是不包含 x1\d+，例如不包含x10
            ret = re.search(reg3, R2[ir2])
##            print('ret = ',  ret)
            if isinstance(ret,re.Match):             
##            if ks[jx] in R2[ir2]:
##                print(R2[ir2])
                x_R2.append(R2[ir2])
##    print(x_R2)
    return x_R2

##把检查冲突后得到的若干个字典转临时mapping
##eg: 检查冲突后得到的若干个字典 check_temp_mt =  [{'x3': 'a08', 'x19': 'a12'}, {'x3': 'a12', 'x19': 'a08'}]
##转后得： check_temp_mt_mdict =  {'x3': ['a08', 'a12'], 'x19': ['a12', 'a08']}
##input: check_temp_mt -  检查冲突后得到的若干个字典，  kst - 若干字典的键，
##output: 临时mapping， eg: check_temp_mt_mdict =  {'x3': ['a08', 'a12'], 'x19': ['a12', 'a08']}
def ctm_to_tm(kst, check_temp_mt):
     # 字典构造器
    check_temp_mt_mdict = dict([(k, []) for k in kst])
    ##print('check_temp_mt_mdict = ', check_temp_mt_mdict)
    for k,v in check_temp_mt_mdict.items():    
        for i in range(len(check_temp_mt)):
            check_temp_mt_mdict[k].append( check_temp_mt[i][k])
    ##        print(check_temp_mt_mdict[k])
##    print('check_temp_mt_mdict = ', check_temp_mt_mdict)
    return check_temp_mt_mdict

##判断mapping的值是否有列表，如果有，返回True
def vislist(mapping):    
    for v in mapping.values():
        if isinstance(v, list):
            return True


##更新mapping
def upd_map(mapping, mapping_n):    
##    print('qian mapping = ' , mapping)
    mapping.update(mapping_n[0])
##    print('hou mapping = ' , mapping)

    ##找到已经合一后的常量，从没有合一后的常量列表中删除
    v_list = []
    for v in mapping.values():
    ##    print(v)
        if isinstance(v, str):
            v_list.append(v)
##    print('v_list = ', v_list)

    ##更新值
##    print('\n')
    for k, v in mapping.items():
    ##    print('q v = ', v)
        if isinstance(v, list):
            v = [x for x in v if x not in v_list]
    ##        print('h k =', k,   'v = ',  v)
            mapping.update({k:v})        
##    print('shan hou mapping = ' , mapping)

    ##按照值的长度排序 ，得元组    
##    print('\n')
    mapping =  sorted(mapping.items(), key= lambda x: len(x[1]) if isinstance(x[1], list) else 1, reverse=False) 
##    print( 'mapping = ' , mapping)
    ##print( 'type(mapping) = ' , type(mapping))

    ##元组转字典
    mapping = dict(mapping)
##    print( 'mapping = ' , mapping)

##从mapping中删除mapping_n中已有的键值对
    for key in list(mapping.keys()):
        if key in list(mapping_n[0].keys()):
    ##            print(key)
            del mapping[key]
            
    return mapping



##用 mapping_n 更新mapping,
##input:   
## mapping =  {'x4': 'a24', 'x9': ['a01', 'a23'], 'x10': ['a01', 'a23'], 'x3': ['a08', 'a15', 'a25', 'a09', 'a13', 'a12', 'a17'], \
##'x8': ['a08', 'a15', 'a25', 'a09', 'a13', 'a12', 'a17'], 'x11': ['a08', 'a15', 'a25', 'a09', 'a13', 'a12', 'a17'],\
##      'x14': ['a08', 'a15', 'a25', 'a09', 'a13', 'a12', 'a17'], 'x18': ['a08', 'a15', 'a25', 'a09', 'a13', 'a12', 'a17'],
##'x19': ['a08', 'a15', 'a25', 'a09', 'a13', 'a12', 'a17'], 'x21': ['a08', 'a15', 'a25', 'a09', 'a13', 'a12', 'a17']}
## mapping_n  =  [{'x3': ['a08', 'a12'], 'x19': ['a12', 'a08']}]
##把mapping中的与mapping_n键相同的值更新成mapping_n的值，
##在mapping中的与mapping_n键不同的值中删除mapping_n的值
##output
##mapping =  {'x4': 'a24', 'x9': ['a01', 'a23'], 'x10': ['a01', 'a23'], 'x3': ['a08', 'a12'], 'x19': ['a12', 'a08'], \
##            'x8': ['a15', 'a25', 'a09', 'a13', 'a17'], 'x11': ['a15', 'a25', 'a09', 'a13', 'a17'], \
##            'x14': ['a15', 'a25', 'a09', 'a13', 'a17'], 'x18': ['a15', 'a25', 'a09', 'a13', 'a17'], 'x21': ['a15', 'a25', 'a09', 'a13', 'a17']}
def upd_map_list(mapping, mapping_n):    
##    print('qian mapping = ' , mapping)
    mapping.update(mapping_n[0])
##    print('hou mapping = ' , mapping)

    ##找到已经合一后的常量，存列表v_list，从没有合一后的常量列表中删除
    v_list = []
    values_map = list(mapping_n[0].values())
    for subitem in values_map:
       v_list.extend(subitem)
    v_list = of.list_deduplication(v_list)
##    print('v_list = ', v_list)

    ##更新值
##    print('\n')
    keys_map = list(mapping_n[0].keys())
##    print('keys_map = ',keys_map)
    for k, v in mapping.items():
##        print('\nq k, v = ', k, v)
        if k not in keys_map and isinstance(v, list):
            v = [x for x in v if x not in v_list]
##            print('h k =', k,   'v = ',  v)
##        else:
##            print('mei bian k =', k,   'v = ',  v)            
##        print('k, v = ', k, v)
        mapping.update({k:v})        
##    print('shan hou mapping = ' , mapping)

    ##按照值的长度排序 ，得元组    
##    print('\n')
    mapping =  sorted(mapping.items(), key= lambda x: len(x[1]) if isinstance(x[1], list) else 1, reverse=False) 
##    print( 'mapping = ' , mapping)
    ##print( 'type(mapping) = ' , type(mapping))

    ##元组转字典
    mapping = dict(mapping)
##    print( 'mapping = ' , mapping)

##把mapping中 与mapping_n[0]相同的键值对移到字典末尾，先删，再加
    mapping_a = {}
    for k in list(mapping.keys()):
        if k in list(mapping_n[0].keys()):
##            print('mapping_n[0][k] = ', mapping_n[0][k])
            mapping_a[k] = mapping_n[0][k]
            del mapping[k]
##    print('mapping_a = ', mapping_a)
    for k in list(mapping_n[0].keys()):
        mapping[k] = mapping_n[0][k]
        
    return mapping
