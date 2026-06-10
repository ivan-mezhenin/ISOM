import operator
from collections import defaultdict
from itertools import *

##mapping_a_list0去重
##input  - mapping_a_list0 =  [['x1', 'x18'], ['x1', 'x18']]
##output - mapping_a_list0 =  [['x1', 'x18']]
def get_dedupl(mapping_a_list0):
    for j in range( len( mapping_a_list0 )-1, -1, -1 ) :
##        print('j = ', j)
        if j-1>=0 and operator.eq(mapping_a_list0[j],mapping_a_list0[j-1]):
##            print('Y')
            del mapping_a_list0[j]
##            print('mapping_a_list0 = ', mapping_a_list0)
    return mapping_a_list0

##字典值相同，找键
##把值相同的键添加到一个列表中
##input  -   mapping_a ={'x1': ['a08', 'a12'], 'x18': ['a12', 'a08']}
##output - mapping_a_k =  {'a08': ['x1', 'x18'], 'a12': ['x1', 'x18']}
def samevalue_getkey(mapping_a):
    mapping_a_kv = defaultdict(list)  # automatically initialize every value to a list()
    for k, v in mapping_a.items():
        for x in v:
            mapping_a_kv[x].append(k)
##    for k, v in mapping_a_kv.items():
##        if len(v) > 1:
####            print([v, k])
####    print('mapping_a_kv = ', dict(mapping_a_kv))
    return dict(mapping_a_kv)

##如果字典中值 - 列表中的元素顺序不一致，调整到一致。
##['a08', 'a12']和['a12', 'a08'] 顺序不一致，调整后：['a08', 'a12']，['a08', 'a12']
##input - mapping_a =  {'x1': ['a08', 'a12'], 'x18': ['a12', 'a08']}
##output  -  v_mapping_a =  [['a08', 'a12'], ['a08', 'a12']]
def change_order(mapping_a):
    vs_mapping_a = list(mapping_a.values())
    for k, v in mapping_a.items():
##        print('k = ', k)  
        for j in range( len(vs_mapping_a) - 1,  -1,  -1 ) :
##            print('j = ', j)
##            print('vs_mapping_a[j].sort(),vs_mapping_a[j-1].sort() = ', sorted(vs_mapping_a[j]), sorted(vs_mapping_a[j-1]))
            if j-1>=0 and operator.eq(sorted(vs_mapping_a[j]), sorted(vs_mapping_a[j-1])):
##                print('Y')
                vs_mapping_a[j] = vs_mapping_a[j-1]                
##                print('mapping_a_list0 = ', vs_mapping_a)
##    print('!!!vs_mapping_a = ', vs_mapping_a)           
    return vs_mapping_a

def many_to_many_dict(mapping_a):
    ##如果字典中值 - 列表中的元素顺序不一致，调整到一致。
    v_mapping_a = change_order(mapping_a)
    ##print('v_mapping_a = ',v_mapping_a)

    ##字典值去重
    v_mapping_a = get_dedupl(v_mapping_a)
##    print('v_mapping_a = ',v_mapping_a)

    ##把值相同的键添加到一个列表中
    mapping_a_k = samevalue_getkey(mapping_a)
##    print('\nmapping_a_k = ', dict(mapping_a_k))

    ##字典键去重
    k_mapping_a = get_dedupl(list(mapping_a_k.values()))
##    print('k_mapping_a = ',k_mapping_a)

    ##把键列表和值列表组成字典
    kvls = []
    for i in range(len(v_mapping_a)):
    ##    print(k_mapping_a[i])
        kvl = []
        vtl = list(permutations(v_mapping_a[i]))
        for j in range(len(vtl)):
    ##        print(list(vtl[j]))
    ##        print( dict(zip(k_mapping_a[i],list(vtl[j]))))
            kvl.append(dict(zip(k_mapping_a[i],list(vtl[j]))))
    ##        print('kvl = ', kvl)
        kvls.append(kvl)
    if len(kvls)==1:
        kvls = kvls[0]
##    print(kvls)
    return kvls
        

mapping_a ={'x1': ['a08', 'a12'], 'x18': ['a12', 'a08'] }#, 'x2' : ['a01', 'a02', 'a03'], 'x3' : ['a01', 'a02', 'a03'], 'x4' : ['a01', 'a02', 'a03']}
##print('\nmapping_a = ', mapping_a)

kvls =  many_to_many_dict(mapping_a)
##print('kvls = ', kvls)


   
                

            
            


        
    




 
