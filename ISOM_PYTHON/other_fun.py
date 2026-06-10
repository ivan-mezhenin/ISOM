import re
from collections import Counter
import dict_sort as ds  # 字典排序，自己写的
from collections import defaultdict # defaultdict(list)用
import Isomorphic_literal as isl
import itertools
import operator  ## operator.eq用



##获取R中变量名（以x开头的，如x5）
def names_of_variable(F):
    argument = []
    pa = re.compile(r"[x]\d+")
    for argu in pa.findall(F):
        argument.append(argu)
    return argument



##提取谓词对应的常量或变量
##得  ['(a1,a3,a2)', '(a2,a1,a5)', ……, '(a4,a3,a5)', '(a7,a5,a10)']
def names_of_argument(F):
    argument = []
    pa = re.compile(r"[a|x]\d+")
    for argu in pa.findall(F):
        argument.append(argu)
    return argument


##提取两个公式（每个公式包含一个出现若干次的相同的谓词）中每个常量（或变量？）及其对应的次数，存字典
##思路：1、提取每个argument， 2、及其相对应的次数，3、最后提取次数对应的次数，
##            4、 判断第3步得到的结果的真假。如果为真，返回True，否则，返回False
def get_chrc(f1,f2):
    ##1、提取每个argument
    arg_f1 = names_of_argument(f1)
    arg_f2 = names_of_argument(f2)
    ##2、提取公式中每个常量（或变量？）及其对应的次数，存字典

    dict_f1 = dict(Counter(arg_f1))
##    print('dict_f1 = ',dict_f1)    
    dict_f1 = ds.sort_val(dict_f1) 
##    print('升序后  dict_f1 = ',dict_f1)
##    print('F1 :  ', end =' ')
##    print_charact(dict_f1)
    dict_f2 = dict(Counter(arg_f2))
    dict_f2 = ds.sort_val(dict_f2) 
##    ds.ascending_value(dict_f2)
##    print('升序后  dict_f2 =', dict_f2)
##    print('\nF2 :  ', end =' ')
##    print_charact(dict_f2)
    
##    char_f1 = ds.descending_value(dict_f1)
##    char_f2 = ds.ascending_value(dict_f2)
##    print('\nchar_F2 :  ', end =' ')
##    print_charact(char_f2)
    return dict_f1,dict_f2


##求 λRP和R
def get_lamb_F1_R(f,x):
    R = f
    ##1、获取argument
    ag_f = names_of_argument(f)
##    print('ag_f = ',ag_f)
    ##去掉重复的argument    
    af_f_deduplication = list_deduplication(ag_f)
##    print('af_f_deduplication = ',af_f_deduplication)
    ##2、创建用于替换字符串中常量的字典
    unifier = {}
    for i in range(len(af_f_deduplication)):
        unifier[ str(x)  + str(i+1)] = af_f_deduplication[i]
##    print('unifier = ',unifier)

##3、替换
    unifier = ds.desceding_value(unifier)    
    R = multipleReplace(R,unifier)
    print('R = ', R)    
    return unifier,R

def is_equ_charc(f1,f2):
    n1, n2 = get_chrc(f1,f2)    
    c1, c2 = get_occurr(n1,n2)    
##    print('c1,c2 = ',  c1,c2)    
##4 、判断两个公式中每个argument出现次数对应的次数是否相等，
##    如果相等，返回True，否则，返回False
##    if(c1 == c2):
##        return True
##    else:
##        return False
    return True if (c1 == c2) else False





def get_occurr(c1,c2):
##    print('get_occurr - input c1,c2 = ', c1,c2)
##    c1, c2 = get_chrc(f1,f2)
##3 、提取每个常量（或变量？）出现次数的次数
    number_of_occ_arg_f1 = dict(Counter(list(c1.values())))
##    print('\nnumber_of_occ_arg_f1 = ', number_of_occ_arg_f1)
    number_of_occ_arg_f2 = dict(Counter(list(c2.values())))
##    print('number_of_occ_arg_f2 = ', number_of_occ_arg_f2)
##    print('number_of_occ_arg_f1, number_of_occ_arg_f2' , number_of_occ_arg_f1,number_of_occ_arg_f2)
    return number_of_occ_arg_f1,number_of_occ_arg_f2


##打印Характеристика
def print_charact(d):
##    print(d)
    for k,v in d.items():
##        print( k ,v) # 文字数*变量数，结果很大的时候，用这行语句，稍微快些
        print(chr(967) , '(', k ,') =',v, ',' , end='')

##列表去重
def list_deduplication(ldf):
##    af_f1_deduplication = list(set(ag_f1))
    return list({}.fromkeys(ldf).keys())


##交换字典的键值对
def kvswap(d):    
    new_d = defaultdict(list)    
    for key, val in d.items():
        new_d[val].append(key)
    return new_d

##求每个文字中包含的变量的个数
##备注：由于谓词名称相同，所以取了第一个文字中变量的个数，
##如果谓词名称不同，可能需要改！！！！
def count_arg(F):
    return len(F.split('&')[0].split(','))

##        把两个有相同键的字典合并为一个新字典list_dict_rf，删除原两个字典的键，
##        并将一个字典的值作为键，另一个字典的值作为值    
def conn_dict(dict_r,dict_f2):
    dict_rf = {}    
    for kr,vr in dict_r.items():
##        print('kr,vr = ', kr,vr)        
        for mf,nf in dict_f2.items():
##            print('mf,nf =', mf,nf)
            if kr == mf:
##                print(type(vr))
                if len(vr) ==1:
                    dict_rf[vr[0]] = nf[0]
                else:
                    for i in range(len(vr)):  
                        dict_rf[vr[i]] = nf            
##    print('dict_rf = ', dict_rf)
    return dict_rf


##        把两个有相同值的字典合并为一个新字典list_dict_rf，删除原两个字典的键，
##        并将一个字典的值作为键，另一个字典的值作为值    
def conn_dict_samevalue(dict_r,dict_f2):
##    print('dict_r,dict_f2 = ', dict_r,dict_f2)
    dict_rf = {}    
    for kr,vr in dict_r.items():
##        print('kr,vr = ', kr,vr)        
        for mf,nf in dict_f2.items():
##            print('mf,nf =', mf,nf)
            if vr == nf:                
                dict_rf[kr] = mf            
##    print('dict_rf = ', dict_rf)
    return dict_rf

## other_elements类型是字典 = {}， first_element 也是字典
def assert_dict(other_elements,first_element):
    ##    flag_first_element用于判断基准元素是否改变，默认没变
    flag_first_element = False
    ##        如果键包含于其他对文字的合一子中
    for key in other_elements:
        ##            如果该键也包含于第一对文字的合一子中
        if (key in first_element):
            if (first_element[key]==other_elements[key]):
                pass
            else:
                return {}, False
##                print('The value of the base element is not equal to the value of the corresponding key of other elements', first_element[key]!=other_elements[key])             
        else:
##                该键不包含于第一对文字的合一子中
##                给第一对文字的合一子添加其他文字合一子的键值
            
##                如果其他文字合一子的值不出现在第一对文字的合一子中        
            if other_elements[key] not in first_element.values():
                first_element[key] = other_elements[key]
                flag_first_element = True
##                如果其他文字合一子的值出现在第一对文字的合一子中，但是这两个值对应的键不一样
            else:
                return {}, False                
##    print('result = ', result)
    return first_element, flag_first_element

##  求k,v 在原公式中的相同位置出现的次数
##input : 公式F, 要查找的变量或常量ve ，
##output: ve在公式F中的characteristic
##eg:  F = 'P1(a3,a0,a2)&P1(a1,a2,a0)&P1(a2,a1,a3)&P1(a2,a1,a3)'
##number_of_occurrences(Q2, 'a2')
##[[0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 0, 0]]
def number_of_occurrences(F, ve):
##    print('F, ve = ', F, ve)
##    匹配包含ve
    reg1 = '^((?!(' + ve + '\d+)).)*$'
    ##  .* 代表匹配除换行符之外的所有字符。
    reg2 = '.*' + ve + '.*'
    reg3 = '(?='+reg2+')(?='+reg1+')' # 包含x1但是不包含 x1\d+，例如不包含x10
    Fl = F.split('&')
    counts = []
##    counts_sum = []
    for i in range(len(Fl)):
        Fls = Fl[i].split(',')
##        print('\n', ' Fls = ', Fls)
        count = [0]*count_arg(F)
##        print('count = ' , count )
        for j in range(len(Fls)):            
##            print('\nFls[j]= ', Fls[j])
            ret = re.search(reg3, Fls[j])
##            print('ret = ', ret)
##            print('type(ret) =', type(ret))
            if isinstance(ret,re.Match):
##                print('ret.start() = ', ret.start())
                count[j] = 1                
##                count_sum[j] = count_sum[j]+1
##        print('count = ', count)
        counts.append(count)
##        counts_sum.append(count_sum)        
##    print(counts)
    return counts#,counts_sum


##嵌套列表排序
def nested_list_sorting(lis, number_of_argument):
    for i in range(number_of_argument):
##        print(i)
        lis.sort(key = lambda x: x[i], reverse=False)
##        lis.sort(key = lambda x: (x[0],x[1],x[2]), reverse=False)
    return lis


def conn_list(dict_r,dict_f2):
##    print('dict_r,dict_f2 = ', dict(dict_r),dict(dict_f2))
    list_rf = []    
    for kr,vr in dict_r.items():
##        print('\nkr,vr = ', kr,vr)        
        for mf,nf in dict_f2.items():
##            print('mf,nf =', mf,nf)
            if kr == mf:
##                print('type(vr) = ', type(vr))
                if len(vr) ==1:
                    list_rf.append([vr[0],nf[0]])
##                    print('if - list _rf = ', list_rf)
                    del dict_f2[mf]
                    break
                else:
##                    for i in range(len(vr)):  
                    list_rf.append([vr,nf])
##                    print('else - list_rf = ', list_rf)
##    print('list_rf = ', list_rf)
    return list_rf

##获得列表中元素的层数
##lst3 = [[['x2', 'x3', 'x4'], ['a3', 'a0', 'a1']], ['x1', 'a2']]
##get_depth(lst3) = 3
##get_depth(lst3[0]) = 2
##get_depth(lst3[1]) = 1
def get_depth(lst):
    return 1 + max(get_depth(itm) for itm in lst) if type(lst) == list else 0

##检查冲突
##input : arr1 = [], arr2 = []
##output: True - 无冲突 + 合一子 , False  - 有冲突 + 空列表
def check_inconsistency(arr1,arr2):
    print('\nIn fun check_inconsistency')
    print('arr1 = ', arr1)
    print('arr2 = ', arr2)

    if (len(arr1) == 1):
        print('len(arr1) = ',len(arr1))
                    
##        print('arr1 == arr2')
##    if( len(arr1) == 1):
##        print('isl.get_arg(arr1) = ', isl.get_arg(arr1[0]))
        tup = isl.isIsomorphic(isl.get_arg(arr1[0]), isl.get_arg(arr2[0]))

##        print('tup = ', tup)
##        print('type(tup[0]) = ', type(tup[0]))
##        print(conn_dict_samevalue(tup[0],tup[1]))
        print('Out of fun check_inconsistency\n')
        return True, conn_dict_samevalue(tup[0],tup[1])
        

    ltr_pair_with_unif = {}              ##字典，存放同构的文字对（值）
##    list_ltr_pair_with_unif = []      ##列表，元素为上面字典 ltr_pair_with_unif 的所有值
##    ltr_pair_with_not_unif = {}             ##字典，存放不同构的文字对（值）
##    list_ltr_pair_with_not_unif  = []       ##列表，元素为上面字典ltr_pair_with_not_unif 的所有值     
    list_result = []            ##存每次若干个文字对比较后的结果，要么false，要么合一子
    
#permutations(a, b) 连续返回由a元素生成的长度为b的全排列组合
    a2  = list(itertools.permutations(arr2))
    print('a2 = ',  a2)
    n = len(a2)
##    print('n = ',n)
    for i in range(n):
        pair_literal = list(zip(arr1,a2[i]))
##        print('\ni = {}, pair_literal =  {}'.format(i, pair_literal))
        list_unif = []
        
        for j in range(len(pair_literal)):
##            print('\tj = {}, pair_literal[{}] = {}'.format( j, j,pair_literal[j]))          
##            print(pair_literal[j][0])
##            print(type(pair_literal[j][0]))
##            print(pair_literal[j][1])
            dic_r,dic_f2 = isl.isIsomorphic(isl.get_arg(pair_literal[j][0]), isl.get_arg(pair_literal[j][1]))
##            print('\ndic_r,dic_f2 = ', dic_r,dic_f2)
            temp_unif = conn_dict_samevalue(dic_r,dic_f2)
##            print('temporary_unifier = ', temp_unif)
            list_unif.append(temp_unif)
##            print('list_unif = ', list_unif)
            
            if j!=0:
                t_u, flag_f_e = assert_dict(list_unif[1],list_unif[0])
##                print('f_element, flag_f_element = ', t_u, flag_f_e)
    ##                如果第一个字典变，合一子为第一个字典的值(由assert_dict(list_unif[1],list_unif[0])求出)

                if (flag_f_e == True):
                    list_unif = [t_u]
##                    print('list_unif = ', list_unif)
                    unif = list_unif[0]
##                    print('unif = ', unif)
##                    print('len(ltr_pair_with_unif) = ' ,len(ltr_pair_with_unif))
##                    print('pair_literal[0] = ', pair_literal[0])
##                    print('ltr_pair_with_unif = ', ltr_pair_with_unif)
                    if pair_literal[0] not in ltr_pair_with_unif.values():
                        ltr_pair_with_unif[len(ltr_pair_with_unif)] = pair_literal[0]                    
                    ltr_pair_with_unif[len(ltr_pair_with_unif)] = pair_literal[j]
##                    print('if - ltr_pair_with_unif = ' ,ltr_pair_with_unif)
                    if j == len(pair_literal) -1:                        
                        list_result.append(list_unif[0])
##                        print('list_result = ', list_result)
                        
                    ##                    否则第一个字典没变                    
    ##              t_u不空，表示此次文字和上次文字同构，有合一子，删除此次添加的字典                             
                elif (t_u !={}):
##                    print('in elif')
                    if pair_literal[0]  not in ltr_pair_with_unif.values():
                        ltr_pair_with_unif[len(ltr_pair_with_unif)] = pair_literal[0]  
                    ltr_pair_with_unif[len(ltr_pair_with_unif)] = pair_literal[j]
##                    print('else - if - ltr_pair_with_unif = ' ,ltr_pair_with_unif)
                    list_unif.pop()
##                    print('list_unif = ', list_unif)
                    if j == len(pair_literal) -1:                        
                        list_result.append(list_unif[0])
##                        print('list_result = ', list_result)                       
                        
    ##                    t_u空，无合一子
                else:
##                    print('in else')
##                    print('j = ', j)
##                    for k in range(j):
##                        print('k = ', k)                            
##                        ltr_pair_with_not_unif[len(ltr_pair_with_not_unif)] = [pair_literal[j],pair_literal[k]]
    ##                                    print('for - ltr_pair_with_not_unif = ', ltr_pair_with_not_unif)                        
                    list_result.append(False)
##                    print('list_result = ', list_result)
##                    print('ltr_pair_with_not_unif = ', ltr_pair_with_not_unif)
##                    list_ltr_pair_with_not_unif = list(ltr_pair_with_not_unif.values())
##                    print('list_ltr_pair_with_not_unif = ', list_ltr_pair_with_not_unif)
                    break
##    gc.collect()
                
##    with open("1.txt","w") as f: 
##        f.write(str(list_result))
    len_res = len(list_result)  
##    print('\nOut-for-list_result = ', list_result)
    if list_result.count(False) < n:
##        print('The formulas are isomorphic, and the unifier is {}'.format())
##        print('The formulas are isomorphic, and the unifier is ')
        print('Сheck for inconsistency - no ')
        for m in range(len_res):
##            print('m = ', m)
            if list_result[m] != False:
##                print('m = ', m)
                print(list_result[m])
##        gc.collect()
        print('Out of fun check_inconsistency\n')                
        return True , list(filter(lambda x: x != False, list_result))

    else:
        print('Сheck for inconsistency - yes')
##        print('The formulas are not isomorphic.')
        print('Out of fun check_inconsistency\n')
        return False , []



##统计一个列表中每个嵌套列表出现的次数
##input -  [[0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 0, 0]]
##output - {(1, 0, 0): 2, (0, 0, 1): 1, (0, 1, 0): 1}
def count_nested_list(arr):
##    print('arr = ', arr)
    for i in range(len(arr)):
##        print(tuple(t[i]))
        arr[i] = tuple(arr[i])    
    result = {}
##    print('set(arr) = ', set(arr))
    for i in set(arr):
##        print('\ni = ', i)
##        print('arr.count(i) = ',arr.count(i))
        result[i] = arr.count(i)
##        print('result[i] = ', result[i])
    return result

##把公式f通过split('&')变成列表，再按照找到arg的方式（没有包含arg的字符串排前面，包含arg的排后面）排序
##假设arg = a4  
##input - Q =  P5(a3,a7,a1,a6,a5)&P5(a7,a6,a5,a4,a2)&P5(a1,a6,a2,a7,a3)
##output - Q2 =  ['P5(a3,a7,a1,a6,a5)', 'P5(a1,a6,a2,a7,a3)', 'P5(a7,a6,a5,a4,a2)']
def split_sort(f , arg):
    f2 = f.split('&')
    f2.sort(key = lambda x: x.find(arg))
    return f2


##按照字典的键（元组）排序
##input:     {(1, 0, 0): 1, (0, 0, 1): 1, (0, 1, 0): 1}
##output:   [((1, 0, 0), 1), ((0, 1, 0), 1), ((0, 0, 1), 1)]
def sort_dict_keytuple(d):
    d = list(d.items())
    d.sort(key = lambda x:x[0],reverse=True)
    return d



##字符串替换，字符串中包含字典的 值，用字典的键替换字符串中字典的值
def multipleReplace(text, wordDict):
##    print('text, wordDict', text, '\n', wordDict)
    for key in wordDict:
        text = text.replace(wordDict[key], key)
##        print(text)
    return text

##字符串替换，字符串中包含字典的 键，用字典的键替换字符串中字典的值
def keymap_replace(string, mappings):
    replaced_string = string
    for character, replacement in mappings.items():
        replaced_string = replaced_string.replace(character, replacement)
    return replaced_string

##字符串列表替换，字符串中包含字典的键，用字典的键替换字符串中字典的值
def keymap_replace_list(list_of_strings,mappings):
    for k in range(len(list_of_strings)):   
        list_of_strings[k] = keymap_replace(list_of_strings[k],mappings)
    return list_of_strings


def print_lambd(lam):    
##    print('lam = ', lam)
    print('\t '.join(list(lam.keys())))
    print('\t '.join(list(lam.values())))



##字符串用字典替换 （完全匹配）
##input F - 公式，k - 键， v - 值
##output 替换后的F
def keymap_replace_key_value(F, k, v):
    
    reg1 = '^((?!(' + k + '\d+)).)*$'
    ##  .* 代表匹配除换行符之外的所有字符。
    reg2 = '.*' + k + '.*'
    reg3 = '(?='+reg2+')(?='+reg1+')' # 包含x1但是不包含 x1\d+，例如不包含x10

    Fs = F.split('&')       
##    print('Fs = ', Fs)
    
    Fr = []
    for i in range(len(Fs)):
        Fsp = Fs[i].split(',')
##            print('\ni = ', i, 'Fsp = ', Fsp)
        for j in range(len(Fsp)):
##                print('j = ', j, 'Fsp[j] = ', Fsp[j])            
            ret = re.search(reg3, Fsp[j])
##                print('ret = ', ret)
            if isinstance(ret,re.Match):
##                    print('if')
                Fsp[j] = keymap_replace(Fsp[j],{k:v})
##                    print('Fsp[j] = ', Fsp[j])
        Fsp = ','.join(Fsp)
##            print('Fsp = ', Fsp)
##        print('type(Fsp) = ', type(Fsp))
        Fr.append(Fsp)
##            print('Fr = ', Fr)
    Fr = '&'.join(Fr)
##    print('Fr = ', Fr)
    return Fr
    

##字符串用字典替换 （完全匹配）
##input F - 公式，m - 字典
##output 替换后的F
def keymap_replace_dict(F, m):
    for k,v in m.items() :
    ##    print('k, v = ', k,v)
        F = keymap_replace_key_value(F, k, v)
    return F    

