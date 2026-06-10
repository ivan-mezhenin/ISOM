import re
import sys
from collections import Counter
import dict_sort as ds  # 字典排序，自己写的
from collections import defaultdict # defaultdict(list)用
import Isomorphic_literal as isl  # 文字（字符串）同构，自己写的
import itertools
import operator  ## operator.eq用
import other_fun as of   ##除了rf2的其他函数，自己写的
import rf2  ##找R和F2和合一子需要的函数，自己写的
import mtmd         ##多对多 - 字典表示，自己写的



    
def get_lamb_R_F2(R,Q):    
##    print('R = ', R,'\n', 'Q= ',Q)
##    1、循环前准备
##    1.1 获取原始mapping
    mapping = rf2.get_first_mapping(R, Q)
##遍历mapping时，没有键对应的文字（这些文字可能在公式只出现了一次，
##    可能在之前遍历时已经把相应的文字做了冲突性检查）
##    由于没有足够的条件确定合一子，将这些键值对存放在 mapping_a中，最后在找合一子
    mapping_a = {} 
    mapping_n = []      ##mapping_n存键值 一对一 的合一子
    for_loop_execution_times = 0        ##循环次数


##    如果mapping_n不空（for_loop_execution_times==0 - 表示mapping_n空，>0- 表示不空）
##    函数vislist(mapping)  -  判断mapping的值是否有列表，如果有，返回True
    while(rf2.vislist(mapping)):
        print('\nIn while')
        for_loop_execution_times = for_loop_execution_times + 1    
        
##        更新mapping, 从mapping中删除mapping_n中已有的键值对
        if len(mapping_n)!=0:            
            mapping = rf2.upd_map(mapping, mapping_n)
            print('mapping = ', mapping)
        mapping_n_sub = {}


##取出键值对或值的第一个元素
##    for k,v in mapping.items():
        k = list(mapping.keys())[0]
##        print('k = ', k)
        v = mapping[list(mapping.keys())[0]]
        
##        如果值的长度为1，两个公式中只有一对arg的特性相等，那么直接将这对arg加到mapping中   
        if(isinstance(v,str) or (isinstance(v,list) and len(v)==1)):    
##            print('\nif isinstance(v,str)')
            print('k'':''v = ' , k,':',v)
##            print('mapping_n = ', mapping_n)
            if isinstance(v,list):
                v = v[0]
                
            if  len(mapping_n) == 1 and for_loop_execution_times != 1:       
                mapping_n[0].update({k:v})
            else:              
                mapping_n_sub[k] = v
                mapping_n.append(mapping_n_sub)  
            print('mapping_n = ',  mapping_n)


##          10、11、12分组前的预处理    
##          10、把R和Q用&分开，按照v排序
##          更新R, R2, Q2              
            R = of.keymap_replace_dict(R, mapping_n[0])
##            R = of.keymap_replace(R, mapping_n[0])
            print('R.replace = ', R)
            try:
                R2
            except NameError:
                R2 = of.split_sort(R , v)
            else:
                R2 = of.split_sort(R , v)
####                print('替换前 R2 = ', R2)
####                R2 = '&'.join(R2)
####                R = of.keymap_replace_dict(R2,c_temp_u)                        
##                R2 = R.split('&')
##                R2.sort(key = lambda x: x.find(v))
##                
####                print('替换后 R2 = ', R2, '\n', 'Q2 = ', Q2)
####                print('R = ', R)      
##                
####                R2 = of.keymap_replace_dict(R2, mapping_n[0])
            print('R2 = ', R2)
            try:
                Q2
            except NameError:
                Q2 = of.split_sort(Q , v)
            else:
                Q2.sort(key = lambda x: x.find(v))   
            print('Q2 = ', Q2)
##            R, R2, Q2 = getR_R2_Q2(R, R2, Q2)
##            res = try1(R2, Q2, mapping_n, v)


##          11、如果两个列表相等，程序结束    
            if operator.eq(R2, Q2):
                mapping_as = mtmd.many_to_many_dict(mapping_a)
##                print('mapping_as =' ,mapping_as)
##                print('mapping_n =' ,mapping_n)
##                print('len(mapping_as) = ', len(mapping_as))

                if  len(mapping_as) != 0:                
                    for i in range(1,len(mapping_as)):
    ##                    if i+1<=len(mapping_as):
    ##                    print('i = ', i)
                        mapping_n.append(mapping_n[i-1])
                    for i in range(len(mapping_as)):   
                        mapping_n[i].update(mapping_as[i])
                        mapping_n[i] = ds.ascending_key(mapping_n[i])                    
                    print('mapping_n =' ,mapping_n)
                else:
                    mapping_n[0] =  ds.ascending_key(mapping_n[0])                 
            

                return mapping_n

##         12、 否则，两个列表不相等，查找两个列表R2、Q2之间的公共元素，并删除，以减少列表的长度，进而缩短比较时间
            R2, Q2, common_elements= rf2.find_com_del(R2,Q2)   
                
##            13、把列表R2，Q2分成两部分，一部分pair_literal_RQ包含v，另一部分R2, Q2不包含v
            pair_literal_RQ = []
            pair_literal_RQ, R2 = rf2.split_withv_withoutv(R2, v, pair_literal_RQ)
            pair_literal_RQ, Q2 = rf2.split_withv_withoutv(Q2, v, pair_literal_RQ)   
            print('pair_literal_RQ[0] = ', pair_literal_RQ[0], 'pair_literal_RQ[1] = ', pair_literal_RQ[1])

##！！！需要测试
            if (len(pair_literal_RQ[0]) != len(pair_literal_RQ[1])):
                return {}
                
            
##            14、检查包含v的冲突性
            check_result_pair, c_temp_u = of.check_inconsistency(pair_literal_RQ[0], pair_literal_RQ[1])
            print('check_result_pair, c_temp_u = ', check_result_pair, c_temp_u)
            print('len(c_temp_u) = ', len(c_temp_u))
            print('type(c_temp_u) = ', type(c_temp_u))
        
            

##              如果冲突，程序结束
            if check_result_pair == False:
                return {}
            
##            15、如果不冲突，更新合一子
            
##            如果合一子的个数=1   isinstance(c_temp_u,dict)
##            rf2.cheak_conflicts_mapping_ctu(mapping, c_temp_u)先检查c_temp_u中和mapping的内容是否有冲突，
##            如果有冲突，从c_temp_u中删除有冲突的字典, 删除后len ==1
            
            elif isinstance(c_temp_u,dict) or len(rf2.cheak_conflicts_mapping_ctu(mapping, c_temp_u)) ==1:
                if isinstance(c_temp_u,dict):
                    pass
                else:
                    c_temp_u = rf2.cheak_conflicts_mapping_ctu(mapping, c_temp_u)[0]                    
                    
                print('\nIn elif')                
                print('c_temp_u = ', c_temp_u)
                print('mapping_n = ', mapping_n)
##                    for i in range(len(c_temp_u)):
##                    print('\ni = ', i, 'c_temp_u[i] = ', c_temp_u[i])                    
                mapping_n[0], c_temp_u = rf2.update_mapping(check_result_pair, c_temp_u, mapping_n[0])            
                print('mapping_n[0], c_temp_u = ', mapping_n[0], c_temp_u)
                print('mapping_n = ', mapping_n)
                if len(mapping_n[0])==0:
                    return {}
                else:
##                更新R, R2, Q2                      
                    print('替换前 R2 = ', R2)
                    R2 = '&'.join(R2)
                    R = of.keymap_replace_dict(R2,c_temp_u)                        
                    R2 = R.split('&')
                    print('替换后 R2 = ', R2, '\n', 'Q2 = ', Q2)
                    print('R = ', R)      
                    
##                    if operator.eq(R2, Q2):
##                        print('mapping_n = ', mapping_n)
##                        mapping_n[0] = ds.ascending_key(mapping_n[0]) 
##                        return mapping_n[0]
  
##合一子的组数>1（这段代码没有测试！！）             
            else:                
                print('\nIn else 合一子的组数>1 ')                
                print('c_temp_u = ', c_temp_u)
                print('mapping_n = ', mapping_n)

##                先检查c_temp_u中和mapping的内容是否有冲突，如果有冲突，从c_temp_u中删除有冲突的字典
                c_temp_u = rf2.cheak_conflicts_mapping_ctu(mapping, c_temp_u)
                print('检查冲突后的 c_temp_u = ', c_temp_u)
                
##更新mapping_n的内容，之前是只包含第一对键值对的列表，
##由于可能存在多个合一子，将mapping_n的个数扩充到与合一子相同的个数     
                for i in range(1,len(c_temp_u)):                   
                    mapping_n.append(mapping_n[i-1])
                print('mapping_n = ', mapping_n)
                
                for i in range(len(c_temp_u)):
                    print('\ni = ', i)                    
                    mapping_n[i], c_temp_u[i] = rf2.update_mapping(check_result_pair, c_temp_u[i], mapping_n[i])                    
                    print('\nmapping_n[{}] ={}, c_temp_u[{}] = {}'.format(i, mapping_n[i], i, c_temp_u[i]))
##                    如果出现冲突，没有合一子， 程序结束
                    if len(mapping_n[i])==0:
                        return {}
##                    print('c_temp_u = ', c_temp_u)
                    
##                    否则，有合一子，用c_temp_u字典替换R2中的字符为Q2
                    else:
                        print('替换前 R2 = ', R2)
                        R2 = of.keymap_replace_list(R2,c_temp_u[i])
                        print('替换后 R2 = ', R2, '\n', 'Q2 = ', Q2)
                       
##                        if operator.eq(R2, Q2) :
##                            print('mapping_n[i] = ', mapping_n[i] )
##                            mapping_n[0] = ds.ascending_key(mapping_n[0]) 
##                            return mapping_n[i]
##                        else:
##                            pass
                























##v的类型是列表
        else:
            v = mapping[list(mapping.keys())[0]][0]
##            print('v = ', v)
                            
            print('\nelse')
            print('mapping_n = ', mapping_n)
            print(k,':',v)

            mapping_nt = {k:v}      ##临时的合一子，如果正确，则更新到mapping_n中，否则mapping_n不变。
            print('mapping_nt = ', mapping_nt)
##            print('mapping_n[0] = ', mapping_n[0])
        


##          10、11、12分组前的预处理    
##          10、把R和Q用&分开，按照v排序
##                    R = of.keymap_replace(R, mapping_n[0])
            if len(mapping_n)>0:
                Rt = of.keymap_replace_dict(R, mapping_n[0])
##            else:
##                Rt = of.keymap_replace_dict(R, mapping_nt)
            try:
                mapping_nt
            except NameError:
                pass
            else:
                Rt = of.keymap_replace_dict(R, mapping_nt)                    
            print('Rt  = ', Rt)
            try:
                R2t
            except NameError:
                print('in except')
                R2t = of.split_sort(Rt , v)
            else:
                print('in try - else')
##                print('替换前 R2t = ', R2t)
                R2t = '&'.join(R2)
                R2t = of.keymap_replace_dict(R2t, mapping_n[0])
                R2t = of.keymap_replace_dict(R2t, mapping_nt)
                R2t = R2t.split('&')
            print('R2t = ', R2t)
            try:
                Q2t
            except NameError:
                try:
                    Q2
                except:
                    Q2 = of.split_sort(Q , v)
                else:
                    pass                
                Q2.sort(key = lambda x: x.find(v))
                Q2t = Q2
            else:
                Q2t = Q2          
            print('Q2t = ', Q2t)
    
  
##          11、如果两个列表相等，程序结束    
            if operator.eq(R2t, Q2t):
                print('mapping_n = ', mapping_n)
##                mapping_n[0] = ds.ascending_key(mapping_n[0]) 
                return mapping_n[0]

##         12、 否则，两个列表不相等，查找两个列表R2、Q2之间的公共元素，并删除，以减少列表的长度，进而缩短比较时间
            R2t, Q2t, common_elementst = rf2.find_com_del(R2t,Q2t)
            print('common_elementst = ', common_elementst)
                
##            13、把列表R2，Q2分成两部分，一部分pair_literal_RQ包含v，另一部分R2, Q2不包含v
            pair_literal_RQt = []
            pair_literal_RQt, R2t = rf2.split_withv_withoutv(R2t, v, pair_literal_RQt)
            pair_literal_RQt, Q2t = rf2.split_withv_withoutv(Q2t, v, pair_literal_RQt)   
            print('pair_literal_RQt[0] = ', pair_literal_RQt[0], 'pair_literal_RQt[1] = ', pair_literal_RQt[1])
##            print('type(pair_literal_RQt[0]) = ', type(pair_literal_RQt[0]), 'type(pair_literal_RQt[1]) = ', type(pair_literal_RQt[1]))
##            print('len(pair_literal_RQt[0]) ==0 ', len(pair_literal_RQt[0]) ==0)
##            print('len(pair_literal_RQt[0]) ==0 and len(pair_literal_RQt[1]==0)', len(pair_literal_RQt[0]) ==0 and len(pair_literal_RQt[1]==0))
            print('R2t, Q2t = ', R2t, Q2t)

            
##            14、检查包含v的冲突性(若干长度不相等，肯定有冲突，不用比)
##            下面的两行代码 需验证
            if len(pair_literal_RQt[0]) != len(pair_literal_RQt[1]):     
                continue
            
##             长度相等
            elif (len(pair_literal_RQt[0]) ==0 and len(pair_literal_RQt[1])==0):
                if len(common_elementst)>0:
                    check_result_pairt = True
                    print('!!!!!!!!!',k,v)
                    c_temp_ut = [{k:v}]
                    print('c_temp_ut = ', c_temp_ut)
##                更新R, R2, Q2                    
                    R2 = R2t
                    print('R2 = ', R2)
                    R= '&'.join(R2)
                    print('R = ', R)
                    Q2 = Q2t
                    print('Q2 = ', Q2 )     
                    

                else:                    
                    print('k = ', k)
##                更新R, R2, Q2                      
                    R2 = R2t
                    print('R2 = ', R2)
                    R= '&'.join(R2)
                    print('R = ', R)
                    Q2 = Q2t
                    print('Q2 = ', Q2 )                    
                    print('k,v = ',k,v)
                    
                    mapping_a[k] = mapping[k]
                    print('mapping_a = ', mapping_a)
                    del mapping[k]
                    print('mapping = ', mapping)                    
                    continue

            
            else:               
                check_result_pairt, c_temp_ut = of.check_inconsistency(pair_literal_RQt[0], pair_literal_RQt[1])                
                print('check_result_pairt, c_temp_ut = ', check_result_pairt, c_temp_ut)
                print('len(c_temp_ut) = ', len(c_temp_ut))
                print('type(c_temp_ut) = ', type(c_temp_ut))
                if isinstance(c_temp_ut, dict) and len(c_temp_ut)==2:
                    [c_temp_ut] = rf2.del_kv_dict([c_temp_ut])
                    print ('c_temp_ut = ', c_temp_ut)#{'a13': 'a13', 'x16': 'a10'}
                    print('len(c_temp_ut) = ', len(c_temp_ut))
                    print('type(c_temp_ut) = ', type(c_temp_ut))


            
    


##如果冲突，程序结束
            if check_result_pairt == False:
                return {}
            
##            15、如果不冲突，更新合一子
##            如果合一子的个数=1          

            elif (isinstance(c_temp_ut,dict) or len(rf2.cheak_conflicts_mapping_ctu(mapping, c_temp_ut)) ==1):
                if isinstance(c_temp_ut,dict) :
                    pass
                else:
##                    c_temp_ut = del_kv_dict(c_temp_ut)
##                    print('c_temp_ut = ',  c_temp_ut)
                    c_temp_ut = rf2.cheak_conflicts_mapping_ctu(mapping, c_temp_ut)[0]
##                    print('c_temp_ut = ',  c_temp_ut)
                
                
                print('In elif')
                print('c_temp_ut = ', c_temp_ut)
                print('mapping_n = ', mapping_n)
##                    for i in range(len(c_temp_u)):
##                    print('\ni = ', i, 'c_temp_u[i] = ', c_temp_u[i])

                if len(mapping_n)==0:
                    mapping_n.append(mapping_nt)
                else:                
                    mapping_n[0].update(mapping_nt)
                print('mapping_n[0] = ', mapping_n[0])
                mapping_n[0], c_temp_ut = rf2.update_mapping(check_result_pairt, c_temp_ut, mapping_n[0])
                
                
                print('mapping_n[0], c_temp_u = ', mapping_n[0], c_temp_ut)
                print('mapping_n = ', mapping_n)
                if len(mapping_n[0])==0:
                    return {}

                else:
                    try:
                        R2
                    except:
                        R2 = R2t
                    else:
                        pass

                    
                    print('替换前 R2 = ', R2)
##                    print('R2t = ', R2t)
                    R2 = '&'.join(R2t)
##                    print('R2 = ', R2)
##                    print('mapping_n[0] = ', mapping_n[0])
                    R = of.keymap_replace_dict(R2,mapping_n[0])     ## mapping_n[0] 之前是   c_temp_ut
##                    print('R = ', R)
                    if len(R) == 0:
                        R2 = []
                    else:
                        R2 = R.split('&')
                    Q2 = Q2t
                    print('替换后 R2 = ', R2, '\n', 'Q2 = ', Q2)                    
                    print('R = ', R)

##                    if operator.eq(R2, Q2):
##                        print('mapping_n = ', mapping_n)
##                        mapping_n[0] = ds.ascending_key(mapping_n[0]) 
##                        return mapping_n[0]


                ##合一子的组数>1                    
            else:                
                print('\nIn else')
                print('c_temp_ut = ', c_temp_ut)
                print('mapping_n = ', mapping_n)

##                先检查c_temp_ut中和mapping的内容是否有冲突，如果有冲突，从c_temp_u中删除有冲突的字典
                c_temp_ut = rf2.cheak_conflicts_mapping_ctu(mapping, c_temp_ut)
                print('检查冲突后的 c_temp_u = ', c_temp_ut)                

                print('len(c_temp_u)>1 合一子的组数>1')
                print('mapping_n[0] = ', mapping_n[0])
                print('k:v = ', k, v)
                mapping_n[0].update({k:v})   ##用k,v更新后的R2， Q2没有冲突，更新mapping_n
                print('mapping_n[0] = ', mapping_n[0])
                check_temp_mt = rf2.del_kv_dict(c_temp_ut)   ##check_temp_m列表，放check后的不唯一的合一子
                print('check_temp_mt = ', check_temp_mt)
                print('R2t = ', R2t)
                print('Q2t = ', Q2t)
                
                kst = list(check_temp_mt[0].keys())
                print('kst = ', kst)
                vst = list(check_temp_mt[0].values())
                print('vst = ', vst)
                
##如果列表kst的元素出现在R2中，则返回R2中相应的文字(列表)                            
                k_R2t = rf2.get_lits(kst, R2t)
                v_Q2t = rf2.get_lits(vst, Q2t)
                print('k_R2t = ', k_R2t)
                print('v_Q2t = ', v_Q2t)

##如果R2中 没有 包含列表kst的元素的文字(列表) ，用 mapping_n 更新mapping,  、
##                此时，变量得到了若干常量， 而不是唯一常量。                    
                if len(k_R2t) == 0 and len(v_Q2t) == 0:
##                    把检查冲突后得到的若干个字典转临时mapping
                    check_temp_mt_mdict = rf2.ctm_to_tm(kst, check_temp_mt)
                    print('check_temp_mt_mdict = ', check_temp_mt_mdict)
##                        print('!!!!mapping = ', mapping)
                    print('check_temp_mt_mdict = ', check_temp_mt_mdict)
##                    用 mapping_n 更新mapping  
                    mapping = rf2.upd_map_list(mapping, [check_temp_mt_mdict])                        
                    print('mapping = ', mapping)         

##如果R2中有包含列表kst的元素的文字(列表) ，那么把这些文字从R2t和Q2t中取出来，进行冲突性检测
                if len(k_R2t) != 0 and len(v_Q2t) != 0:                        
                    R2t = [i for i in R2t if i not in k_R2t]
                    Q2t = [i for i in Q2t if i not in v_Q2t]
                    print('R2t = ', R2t)
                    print('Q2t = ', Q2t)
                    
                    check_result_pairt, c_temp_ut = of.check_inconsistency(k_R2t, v_Q2t)
                    print('!!!!!!check_result_pairt, c_temp_u = ', check_result_pairt, c_temp_ut)
                    print('!!!!!len(c_temp_ut) = ', len(c_temp_ut))
                    print('!!!!type(c_temp_ut) = ', type(c_temp_ut))
                
##删除有冲突的字典，变量得到唯一常量。
                    c_temp_ut = rf2.del_dict(c_temp_ut)
                    c_temp_ut = rf2.del_kv_dict(c_temp_ut)
                    print('c_temp_ut = ', c_temp_ut)
                    if (len(c_temp_ut) == 1):
                        mapping_n[0].update(c_temp_ut[0])
                    print('mapping_n[0] = ', mapping_n[0])
                    
                R2 = R2t
                Q2 = Q2t
                R = '&'.join(R2t)
                print('R2 = ', R2)
                print('Q2 = ', Q2)
                print('R = ', R)
                    
        
    mapping_n[0] = ds.ascending_key(mapping_n[0])
##    print('mapping_n[0] = ', mapping_n[0])
##    mapping = ds.ascending_key(mapping) 
##    print('\nmapping = ', mapping)
    
    return mapping_n[0]




def get_map(F1,F2):
    if of.is_equ_charc(F1,F2) == True:        
        print('\nThe characteristics are equal, so possibly isomorphic.')
        lambF1, R = of.get_lamb_F1_R(F1,'x')
        print('\nUnifier λ of R and F1: ')        
        lambF1 = ds.ascending_key(lambF1)
        of.print_lambd(lambF1)
        
        lambF2 = get_lamb_R_F2(R, F2)
        print('lambF2 = ', lambF2)
        if len(lambF2) == 0:
            print('\nNot isomorphic')
            return False, {}
        elif isinstance(lambF2, dict):
            print('Unifier λ of R and F2: ')
            of.print_lambd(lambF2)
            lamb = of.conn_dict(lambF1,lambF2)
            return True, lamb
        else:
            print('Unifier λ of R and F2: ')
            for i in range(len(lambF2)):
                of.print_lambd(lambF2[i])
                lamb = of.conn_dict(lambF1,lambF2[i])
            return True, lamb
    else:
        print('\nNot isomorphic')
        return False, {}





def main():
    if len(sys.argv) == 3:
        F1 = sys.argv[1].replace('\\n', '')
        F2 = sys.argv[2].replace('\\n', '')
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()):
            is_iso, _ = get_map(F1, F2)
        print("ISOMORPHIC" if is_iso else "NOT ISOMORPHIC")
        return

    # Default test (19 literals, arity 3)
    F1 =  'P1(a1,a3,a2)&P1(a2,a1,a5)&P1(a2,a5,a8)&P1(a2,a1,a8)&P1(a3,a4,a1)&\
P1(a3,a5,a1)&P1(a3,a9,a4)&P1(a3,a9,a5)&P1(a3,a9,a1)&P1(a5,a2,a3)&\
P1(a5,a2,a4)&P1(a5,a3,a10)&P1(a5,a4,a10)&P1(a5,a10,a2)&P1(a8,a2,a10)&\
P1(a9,a10,a3)&P1(a10,a5,a9)&P1(a10,a8,a5)&P1(a10,a8,a9)'
    F2 =  'P1(a1,a4,a2)&P1(a2,a1,a6)&P1(a2,a6,a3)&P1(a2,a1,a3)&P1(a3,a2,a8)&\
P1(a4,a5,a1)&P1(a4,a6,a1)&P1(a4,a7,a5)&P1(a4,a7,a6)&P1(a4,a7,a1)&\
P1(a6,a2,a5)&P1(a6,a2,a4)&P1(a6,a5,a8)&P1(a6,a4,a8)&P1(a6,a8,a2)&\
P1(a7,a8,a4)&P1(a8,a3,a6)&P1(a8,a6,a7)&P1(a8,a3,a7)'

    if '\n' in F1:
        F1 = F1.replace('\n', '')
    if '\n' in F2:
        F2 = F2.replace('\n', '')

    print('Initial data:')    
    print('F1 = ', F1)
    print('F2 = ', F2)

    print('\nCharacteristic: ')
    t = of.get_chrc(F1,F2)
    for i in range(len(t)):
        of.print_charact(t[i])
    print('\n') 

    get_map(F1,F2)   



if __name__ == '__main__':
    main()
