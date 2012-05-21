#!/usr/bin/env python
from celery.task import task
from celery.task.sets import subtask



@task
def add(x, y):
    return x + y



@task
def bAdd(x, y, callback=None):
    result = x + y
    if callback is not None:
        subtask(callback).delay(result)
    return result


@task(ignore_result=True)
def fact(n, callback=None):
    pass
    
@task()
def g1(res, resAtt):
    #resAtt[0] = res
    print res
    return res

@task()
def g(cbs, cb, x, resAtt):
    if len(cbs) == 0:
        cb(x, resAtt)
    else:
        bV = cbs.pop()
        bVf = bV['func']
        bVV = bV['val']
        return subtask(bVf).delay(cbs, cb, x * bVV, resAtt)


@task()
def f(cbs, cb, x, resAtt):
    if x == 0:
        bV = cbs.pop()
        bVf = bV['func']
        bVV = bV['val']
        return subtask(bVf).delay(cbs, cb, bVV, resAtt)
    else:
        cbs.append({
            'func':g,
            'val':x
        })
        return subtask(f).delay(cbs, cb, x-1, resAtt)







