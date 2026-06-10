##https://www.bilibili.com/video/BV1xR4y1X7jX/?spm_id_from=333.337.search-card.all.click&vd_source=a638ea4173aa3153c4a6e83b84d44fbe
##Leetcode 205 Isomorphic Strings 同构字符串

def get_code(c,d):
    code = -1
    if c in d:
        code = d[c]
    else:
        code = len(d)
        d[c] = code
    return code

##s, t 格式 ['x10', 'x2', 'x10', 'x3', 'x4']， ['a1', 'a2', 'a1', 'a3', 'x3']   
def isIsomorphic(s, t):
    s_dict = {}
    t_dict = {}
    
    for a, b in zip(s, t):
        a_code = get_code(a,s_dict)
        b_code = get_code(b,t_dict)
        
        if a_code != b_code:
            return False
##    print('s_dict = ', s_dict, '\n', 't_dict = ', t_dict)

    return  s_dict, t_dict

def get_arg(f):
    return f.split('(')[1].split(')')[0].split(',')
    
def main():
    s = 'P1(x10,x2,x10,x3,x4)'
    t = 'P1(a1,a2,a1,a3,x3)'
##    s = 'P1(x1,x2,x2)'
##    t = 'P1(a1,a2,a3)'
    s = get_arg(s)
    t = get_arg(t)
    print(s)
    print(t)
    
##    s = 'paper'
##    t = 'title'    
##    s = 'egg'
##    t = 'add'
##    s = 'foo'
##    t  = 'bar'
    print('isIsomorphic(s, t) = ', isIsomorphic(s, t))
##    print(type(isIsomorphic(s, t)))

    
if __name__ == '__main__':
    main()
