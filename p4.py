#!/usr/bin/env python
import sys
import copy

from p4lib import *
from celery.task import chord
from celery.task.sets import TaskSet
import celeryconfig

import string
from random import *



gBoard = None
channel = None

def createBoard():
    board = []
    for i in range(7*7):
        board.append(0)
    return board

def getBoardElem(board, i, j):
    if i >= 0 and i < 7 and j >= 0 and j <7:
        return board[i*7 + j]
    return 0

def setBoardElem(board, i, j, elem):
    if i >= 0 and i < 7 and j >= 0 and j <7:
        board[i*7 + j] = elem


def drawBoard(board):
    bStr = ""
    bStr += (" 1234567 \n")
    bStr += ("/-------\\\n")
    for i in range(0,7):
        bStr += ("|")
        for j in range(0,7):
            bElem = getBoardElem(board, i, j)
            if bElem == 0:
                bStr += (" ")
            elif bElem == 1:
                bStr += ("O")
            elif bElem == 2:
                bStr += ("X")
        bStr += ("|\n")
    bStr += ("\\-------/\n")
    print bStr
    displayBoardState(board)


def displayBoardState(board):
    bStr = ""
    for i in range(0,7):
        for j in range(0,7):
            bElem = getBoardElem(board, i, j)
            if bElem == 0:
                bStr += ("0")
            elif bElem == 1:
                bStr += ("1")
            elif bElem == 2:
                bStr += ("2")
    bStr += ("\n")
    print bStr
    
def createBoardFromString(bStr):
    board = []
    for i in range(0, len(bStr)):
        bChar = bStr[i]
        bVal = int(bChar)
        board.append(bVal)
    return board

def inputAction():
    cse = 0
    isOk = False
    while not isOk:
        isOk = True
        cseStr = raw_input("Your action?")
        try:
           cse = int(cseStr)
        except:
            isOk = False
    
    return cse-1


def playToBoard(board, cse, curPlayer):
    i = 0
    if getBoardElem(board, 0, cse):
        return -1
    
    found = False
    for i in range(0, 7):
        if getBoardElem(board, i, cse):
            found = True
            break
    if not found:
        i = 7
    setBoardElem(board, i-1, cse, curPlayer)
    return i-1

def isGameFinished(board):
    curPlayer = 1
    while curPlayer < 3:
        # horizontal
        for i in range(0, 7):
            ctr = 0
            j = 0
            while j<7:
                if getBoardElem(board, i, j) == curPlayer:
                    ctr += 1
                else:
                    ctr = 0
                if ctr == 4:
                    return curPlayer
                j += 1
                
        # vertical
        for j in range(0, 7):
            ctr = 0
            i = 0
            while i<7:
                if getBoardElem(board, i, j) == curPlayer:
                    ctr += 1
                else:
                    ctr = 0
                if ctr == 4:
                    return curPlayer
                i += 1
        
        # diagonal
        for i in range(0, 7):
            for j in range(0, 7):
                ctrB = 0
                ctrC = 0
                
                for k in range(0, 4):
                    if getBoardElem(board, i+k, j+k) == curPlayer:
                        ctrB += 1
                    else:
                        ctrB = 0
                    if ctrB == 4:
                        return curPlayer
                    if getBoardElem(board, i-k, j+k) == curPlayer:
                        ctrC += 1
                    else:
                        ctrC = 0
                    if ctrC == 4:
                        return curPlayer
        curPlayer += 1
    return 0


def think2(board, level, curPlayer, bestAction):
    bestAction = -1
    winner = isGameFinished(board)
    if winner == curPlayer:
        return (1000, bestAction)
    elif winner == 3 - curPlayer:
        return (-1000, bestAction)
    
    
    if level == 4:
        return (0, bestAction)
    
    maxValue = float("-inf")
    localBestAction = 0
    
    for j in range(0, 7):
        fallLine = playToBoard(board, j, curPlayer)
        #drawBoard(gBoard)
        
        if fallLine != -1:
            bValue, bestAction = think2(board, level+1, 3 - curPlayer, bestAction)
            bValue = -bValue
            
            setBoardElem(board, fallLine, j, 0)
            if bValue > maxValue:
                maxValue = bValue
                localBestAction = j
    
    bestAction = localBestAction    
    
    return (maxValue, bestAction)
    

def think(board, level, curPlayer):
    if level == 7:
        return (0, -1)
    
    #print "considering board;"
    #drawBoard(board)
    
    maxValue = float("-inf")
    localBestAction = 0
    
    if level == 0:
        print "think"
    
    for j in range(0, 7):
        fallLine = playToBoard(board, j, curPlayer)
        if fallLine != -1:
            winner = isGameFinished(board)
            if winner == curPlayer:
                bValue, bestAction = 10000, j
            elif winner == 3 - curPlayer:
                bValue, bestAction = -10000, j
            else:
                bValue, bestAction = think(copy.copy(board), level+1, 3 - curPlayer)
                bValue = -bValue

            if level == 0:
                print bValue, j
            setBoardElem(board, fallLine, j, 0)
            if bValue > maxValue:
                maxValue = bValue
                localBestAction = j

    return (maxValue, localBestAction)



def distributedThink(board, level, curPlayer):
    callback = getBest.subtask()
    header = []
    queueName = "hellp"
    nodeId = randomQueueName()
    collectingNode = CollectingNode(queueName, nodeId)

    #queueName = "hello"
    for j in range(0, 7):
        
        fallLine = playToBoard(board, j, curPlayer)
        if fallLine != -1:
            #winner = isGameFinished(board)
            #if winner == curPlayer:
            #    setBoardElem(board, fallLine, j, 0)
            #    print "this case"
            #    return (10000, j)
            #elif winner == 3 - curPlayer:
            #    setBoardElem(board, fallLine, j, 0)
            #    print "this case oh"
            #    return (-10000, j)
            
            thinkAsync.delay(copy.copy(board), level+1, 3 - curPlayer, j, queueName, nodeId)
            setBoardElem(board, fallLine, j, 0)
    
    #job = TaskSet(tasks=header)
    #result = job.apply_async()
    
    
    collectingNode.waitForMessages()
    print collectingNode.result
    
    return collectingNode.result
    
    #result = chord(header)(callback)
    #maxValue, bestAction = result.get()
    #print "distributedThink:"
    #print maxValue, bestAction
    #return maxValue, bestAction



class BrokerCallback: 
    
    def __init__(self, queueName, nodeId):
        self.queueName = queueName
        self.nodeId = nodeId
        self.result = [None, None, None, None, None, None, None]
        self.ctr = 0

    def _computeBest(self, ch):
        maxValue = float("-inf")
        localBestAction = 0
        print "getting best"
        print self.result
        #print "actions:"
        for j in range(0, len(self.result)):
            act = self.result[j]
            
            if not act:
                print "HEEEYYYYYYYYY"
            else:
                act[0] = -act[0]
                #bAct = (-act[0], act[1], act[2])
                if act[0] > maxValue:
                    maxValue = act[0]
                    localBestAction = j
        #print "getBest"
        #print maxValue, localBestAction
        self.bResult = (maxValue, localBestAction)
        ch.stop_consuming()
        
    def __call__(self, ch, method, properties, body): 
        print " [x] Received %r" % (body,)
        #self.result = body
        vals = cjson.decode(body)
        print vals
        maxValue, localBestAction, ichBin, recNodeId = vals
        #print "%d" % ichBin
        
        self.result[ichBin] = vals
        self.ctr += 1
        if self.ctr == 7:
            self._computeBest(ch)



class CollectingNode:
    def __init__(self, queueName, nodeId):
        
        self.nodeId = nodeId
        self.queueName = queueName  #"hello"    #self._randomQueueName()
        credentials = pika.PlainCredentials(celeryconfig.BROKER_USER, celeryconfig.BROKER_PASSWORD)
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            credentials=credentials,
            host=celeryconfig.BROKER_HOST,
            virtual_host=celeryconfig.BROKER_VHOST
        ))
        channel = connection.channel()
        try:
            channel.queue_delete(queue=self.queueName)
        except:
            pass
        
        self.channel = channel
        self.connection = connection
        print 1
        
    def waitForMessages(self):
        channel = self.channel
        connection = self.connection
        queueName = self.queueName
        channel.queue_declare(queue=self.queueName)
        print ' [*] Waiting for messages. To exit press CTRL+C queueName = %s' % queueName
        brokerCallback = BrokerCallback(self.queueName, self.nodeId)
        channel.basic_consume(brokerCallback,
                              queue=self.queueName,
                              no_ack=True)
        channel.start_consuming()
        connection.close()
        print "continuing.."
        self.result =  brokerCallback.bResult
        

def randomQueueName():
    chars = string.ascii_letters    # + string.digits
    return "".join(choice(chars) for x in range(randint(8, 10)))
        
        
    
    
#def brokerCallback(ch, method, properties, body):
#    global channel
#    print " [x] Received %r" % (body,)
#    channel.stop_consuming()

def interactivePlay():
    global gBoard
    global channel
    
    curPlayer = 1
    whoWon = 0
    cse = 0
    
    while (whoWon == 0):
        print "Its your turn %d" % curPlayer
        drawBoard(gBoard)
        
        if curPlayer == 1:
            cse = inputAction()
        else:
            #maxValue, cse = think(gBoard, 0, curPlayer)
            #print "think best:"
            #print maxValue, cse
            
            
            #collectingNode = CollectingNode()
            
            #print "go on..."
            #print collectingNode.result
            dMaxValue, dcse = distributedThink(gBoard, 0, curPlayer)
            print "distributed think best:"
            print dMaxValue, dcse
            maxValue, cse = dMaxValue, dcse
            
            
        while playToBoard(gBoard, cse, curPlayer) == -1:
            drawBoard(gBoard)
            cse = inputAction()            
        
        curPlayer = 3 - curPlayer
        whoWon = isGameFinished(gBoard)
    drawBoard(gBoard)
    print "%d won" % whoWon
    
    

def main():
    global gBoard
    if len(sys.argv) > 1:
        gBoard = createBoardFromString(sys.argv[1])
    else:
        gBoard = createBoard()
    drawBoard(gBoard)
    interactivePlay()




if __name__ == "__main__":
    main() 



