#!/usr/bin/env python



def g1(res, resAtt):
    resAtt[0] = res
    print res
    
def g(cbs, cb, x, resAtt):
    if len(cbs) == 0:
        cb(x, resAtt)
    else:
        bV = cbs.pop()
        bVf = bV['func']
        bVV = bV['val']
        bVf(cbs, cb, x * bVV, resAtt)

def f(cbs, cb, x, resAtt):
    if x == 0:
        bV = cbs.pop()
        bVf = bV['func']
        bVV = bV['val']
        bVf(cbs, cb, bVV, resAtt)
    else:
        cbs.append({
            'func':g,
            'val':x
        })
        f(cbs, cb, x-1, resAtt)

resAtt = [0]
f([], g1, 6, resAtt)
print resAtt[0]



#def bfunc(n, *args):
#    print args

#bfunc(142,236,637,25)
#a = (236,637,25)
#bfunc(142, *a)





