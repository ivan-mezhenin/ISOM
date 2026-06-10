import re
import operator  ## operator用


# 将可以转化为数字的转化为数字
# 不可以转化的保留原始类型
def tryint(s):
    try:
        return int(s)
    except ValueError:
        return s
    # 也可以使用
    # return int(s) if s.isdigit() else s

# 将字母和数字分开
def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    # 使用alphanum_key作为key进行排序
    l.sort(key=alphanum_key)

##按照字典的键升序
def ascending_key(a_dict):
    a_sort_list = sorted(a_dict.items(),key=lambda x :  alphanum_key(x[0]))
    a_sort_dict = {}
    for n, s in a_sort_list:
        a_sort_dict[n] = s 
    return a_sort_dict

##按照字典的值升序
def ascending_value(a_dict):
    a_sort_list = sorted(a_dict.items(),key=lambda x :  alphanum_key(x[1]))
    a_sort_dict = {}
    for n, s in a_sort_list:
        a_sort_dict[n] = s 
    return a_sort_dict


##按照字典的值降序排序
## in : a_dict = {'a1': 2, 'a2': 3, 'a3': 2, 'a4': 3, 'a5': 2, 'a6': 1, 'a7': 2}
## out: char_f1 =  {'a2': 3, 'a4': 3, 'a1': 2, 'a3': 2, 'a5': 2, 'a7': 2, 'a6': 1}
##def sort_dict_desc_order(a_dict):
def desceding_value(a_dict):    
    a_sort_list = sorted(a_dict.items(),key=lambda x : (x[1]), reverse=True)
    a_sort_dict = {}
    for n, s in a_sort_list:
        a_sort_dict[n] = s 
    return a_sort_dict


##按照字典的键降序排序
## in : a_dict = {'a1': 2, 'a2': 3, 'a3': 2, 'a4': 3, 'a5': 2, 'a6': 1, 'a7': 2}
## out: char_f1 =  {'a2': 3, 'a4': 3, 'a1': 2, 'a3': 2, 'a5': 2, 'a7': 2, 'a6': 1}
def desceding_key(a_dict):    
    a_sort_list = sorted(a_dict.items(),key=lambda x : alphanum_key(x[0]), reverse=True)
    a_sort_dict = {}
    for n, s in a_sort_list:
        a_sort_dict[n] = s 
    return a_sort_dict

##函数sort_key，sort_val不涉及键或值中既包含字母，又包含数字的情况
##按照字典的键升序排序
def sort_key(d):
    return dict(sorted(d.items(), key=operator.itemgetter(0)))

##按照字典的值升序排序
def sort_val(d):
    return dict(sorted(d.items(), key=operator.itemgetter(1)))


##d =  {'x1': 3, 'x2': 3, 'x3': 2, 'x4': 1}
##print(sort_val(d))


##lam =  {'x10': 'a8', 'x4': 'a7', 'x3': 'a6', 'x9': 'a5', 'x2': 'a4', 'x8': 'a2', 'x11': 'a13', 'x7': 'a12', 'x6': 'a11', 'x5': 'a10', 'x1': 'a1'}
##print(lam)
##print(ascending_key(lam))




##dict_f1 =  {'a1': 1, 'a4': 1, 'a6': 2, 'a7': 1, 'a10': 1, 'a11': 2, 'a12': 2, 'a2': 1, 'a5': 1, 'a8': 1, 'a13': 1}
##dict_f2 = {'a1': 1, 'a4': 1, 'a17': 2, 'a7': 1, 'a10': 1, 'a11': 2, 'a12': 2, 'a2': 1, 'a5': 1, 'a8': 1, 'a13': 1}
####print('dict_f1 = ',dict_f1)
####print('dict_f2 = ', dict_f2)
##char_f1 = desceding_value(dict_f1)

##print('char_F1 :  ', char_f1)
##print_charact(char_f1)
##char_f2 = desceding_value(dict_f2)
##print('\nchar_F2 :  ', char_f2)
##print_charact(char_f2)

##unifier =  {'x1': 'a1', 'x2': 'a4', 'x3': 'a6', 'x4': 'a7', 'x5': 'a10', 'x6': 'a11', 'x7': 'a12', 'x8': 'a2', 'x9': 'a5', 'x10': 'a8', 'x11': 'a13'}
##print(unifier)
##print(desceding_key(unifier))
