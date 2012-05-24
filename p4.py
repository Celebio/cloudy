#!/usr/bin/env python
import sys
import copy

from p4lib import *
from celery.task import chord
from celery.task.sets import TaskSet

gBoard = None


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
    sys.stdout.write(" 1234567 \n")
    sys.stdout.write("/-------\\\n")
    for i in range(0,7):
        sys.stdout.write("|")
        for j in range(0,7):
            bElem = getBoardElem(board, i, j)
            if bElem == 0:
                sys.stdout.write(" ")
            elif bElem == 1:
                sys.stdout.write("O")
            elif bElem == 2:
                sys.stdout.write("X")
        sys.stdout.write("|\n")
    sys.stdout.write("\\-------/\n")
    displayBoardState(board)


def displayBoardState(board):
    for i in range(0,7):
        for j in range(0,7):
            bElem = getBoardElem(board, i, j)
            if bElem == 0:
                sys.stdout.write("0")
            elif bElem == 1:
                sys.stdout.write("1")
            elif bElem == 2:
                sys.stdout.write("2")
    sys.stdout.write("\n")
    
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
    
    
    if level == 5:
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
                return (1000, j)
            elif winner == 3 - curPlayer:
                setBoardElem(board, fallLine, j, 0)
                return (-1000, j)
            
            bValue, bestAction = think(board, level+1, 3 - curPlayer)
            bValue = -bValue
            setBoardElem(board, fallLine, j, 0)
            if bValue > maxValue:
                maxValue = bValue
                localBestAction = j

    return (maxValue, localBestAction)



def distributedThink(board, level, curPlayer):
    callback = getBest.subtask()
    header = []
    for j in range(0, 7):
        
        fallLine = playToBoard(board, j, curPlayer)
        if fallLine != -1:
            winner = isGameFinished(board)
            if winner == curPlayer:
                setBoardElem(board, fallLine, j, 0)
                return (1000, j)
            elif winner == 3 - curPlayer:
                setBoardElem(board, fallLine, j, 0)
                return (-1000, j)
            
            localBoard = copy.copy(board)
            setBoardElem(board, fallLine, j, 0)
            header.append(thinkAsync.subtask((localBoard, level+1, 3 - curPlayer)))
    
    #job = TaskSet(tasks=header)
    #result = job.apply_async()
    
    result = chord(header)(callback)
    return result.get()


def interactivePlay():
    global gBoard
    
    curPlayer = 1
    whoWon = 0
    cse = 0
    
    while (whoWon == 0):
        print "Its your turn %d" % curPlayer
        drawBoard(gBoard)
        
        if curPlayer == 1:
            cse = inputAction()
        else:
            maxValue, cse = distributedThink(gBoard, 0, curPlayer)
            
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



