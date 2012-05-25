#!/usr/bin/env python
from celery.task import task, Task
from celery.task.sets import subtask
from celery import registry

import pika


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



@task
def bAdd(x, y, callback=None):
    result = x + y
    if callback is not None:
        subtask(callback).delay(result)
    return result
    
        

class Adder(Task):
    def __init__(self):
        #self.users = {"george": "password"}
        pass
        
    def run(self, x, y, callback=None):
        result = x + y
        if callback is not None:
            subtask(callback).delay(result)
        return result

    def after_return(self, *args, **kwargs):
        print args
        print kwargs
        for k in self:
            print k, self[k]
        print("Task returned: %r" % (self.request, ))

cAdd = registry.tasks[Adder.name]


def sendResult(x):
    credentials = pika.PlainCredentials('celmquser', 'celmq4rox')

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        credentials=credentials,
        host='94.23.52.124',
        virtual_host='celmqvhost'
    ))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    channel.basic_publish(exchange='',
                          routing_key='hello',
                          body='%d' % x)
    #print " [x] Sent 'Hello World!'"
    connection.close()



@task()
def g1(res):
    print res
    return res

@task()
def g(cbs, cb, x):
    if len(cbs) == 0:
        print x
        sendResult(x)
        return x
    else:
        bV = cbs.pop()
        bVf = bV['func']
        bVV = bV['val']
        return subtask(bVf).delay(cbs, cb, x * bVV)


@task()
def f(cbs, cb, x):
    if x == 0:
        bV = cbs.pop()
        bVf = bV['func']
        bVV = bV['val']
        return subtask(bVf).delay(cbs, cb, bVV)
    else:
        cbs.append({
            'func':g,
            'val':x
        })
        return subtask(f).delay(cbs, cb, x-1)


@task()
def fibo(cbs, x):
    if x == 0 or x== 1:
        bV = cbs.pop()
        bVf = bV['func']
        bVV = bV['val']
        subtask(bVf).delay(cbs, bVV)
    else:
        cbs.append({
            'func':gibo,
            'val':x-1
        })
        subtask(fibo).delay(cbs, x-1)





from p4 import playToBoard, setBoardElem, think, isGameFinished, drawBoard



@task
def getBest(actions):
    maxValue = float("-inf")
    localBestAction = 0
    print "actions:"
    for j in range(0, len(actions)):
        act = actions[j]
        bAct = (-act[0], act[1], act[2])
        print bAct
        print j
        if bAct[0] > maxValue:
            print "maxvalue"
            maxValue = bAct[0]
            localBestAction = j
    print "getBest"
    print maxValue, localBestAction
    return (maxValue, localBestAction)
    

@task()
def thinkAsync(board, level, curPlayer, ichBin):
    print "received board;"
    drawBoard(board)
    if level == 5:
        return (0, -1)

    maxValue = float("-inf")
    localBestAction = 0
    winningBoard = None

    for j in range(0, 7):
        fallLine = playToBoard(board, j, curPlayer)
        if fallLine != -1:
            winner = isGameFinished(board)
            if winner == curPlayer:
                setBoardElem(board, fallLine, j, 0)
                return (10000, j, ichBin)
            elif winner == 3 - curPlayer:
                setBoardElem(board, fallLine, j, 0)
                return (-10000, j, ichBin)

            bValue, bestAction = think(board, level+1, 3 - curPlayer)
            bValue = -bValue
            setBoardElem(board, fallLine, j, 0)
            if bValue > maxValue:
                maxValue = bValue
                localBestAction = j

    return (maxValue, localBestAction, ichBin)










