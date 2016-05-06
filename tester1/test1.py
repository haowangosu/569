import sut
import random
import sys
import time

def expandPool():
    global belowMean,lastAddCoverage
    if len(sut.newStatements()) != 0:
        print "NEW STATEMENTS DISCOVERED",sut.newStatements()
        oldTest = list(sut.test())
        storeTest = sut.reduce(oldTest,sut.coversStatements(sut.newStatements()))
        print "OLD LENGTH = ",len(oldTest),"NEW LENGTH = ",len(storeTest)
        sut.replay(oldTest)
        fullPool.append((storeTest, set(sut.currStatements())))
        lastAddCoverage = set(sut.currStatements())
        return
    for s in belowMean:
        if s in sut.currStatements() and s not in lastAddCoverage:
            print "NEW PATH TO LOW COVERAGE STATEMENT",s
            fullPool.append((list(sut.test()), set(sut.currStatements())))
            lastAddCoverage = set(sut.currStatements())
            return



def randomAction():
    global actCount, bugs, failPool, coverageCount

    act = sut.randomEnabled(random.Random())
    actCount += 1
    ok = sut.safely(act)
    if not ok:
        bugs += 1
        print "FOUND A FAILURE"
        print sut.failure()
        print "REDUCING"
        failPool.append(sut.test())
        for s in sut.currStatements():
            if s not in coverageCount:
             coverageCount[s] = 0
            coverageCount[s] += 1

        R = sut.reduce(sut.test(),sut.fails, True, True)
        sut.prettyPrintTest(R)
        print sut.failure()
        sut.restart()
    else:
        expandPool()
    return ok

depth = 100

explore = 0.7
actCount = 0

sut = sut.sut()

bugs = 0

coverageCount = {}
activePool = []
fullPool = []
failPool = []

belowMean = set([])

print "STARTING PHASE 1"

start = time.time()
ntests = 0
while time.time()-start < int(sys.argv[1]):
    sut.restart()
    ntests += 1
    for s in xrange(0,depth):
        if not randomAction():
            break
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0
        coverageCount[s] += 1

#printCoverage()
print "STARTING PHASE 2"
def buildActivePool():
    global activePool

    activePool = []
    for (t,c) in fullPool:
        for s in c:
            if s in belowMean:
                activePool.append((t,c))
                break
    print len(activePool),"TESTS IN THE ACTIVE POOL,",len(fullPool),"IN FULL POOL"

start = time.time()
while time.time()-start < int(sys.argv[2]):
    buildActivePool()
    lastAddCoverage = set([])
    sut.restart()
    if random.Random().random() > explore:
        sut.replay(random.Random().choice(activePool)[0])
        lastAddCoverage = set(sut.currStatements())
    ntests += 1
    for s in xrange(0,depth):
        if not randomAction():
            break


#sut.internalReport()
#printCoverage()

print ntests,"TESTS"


for (t,s) in fullPool:
    print len(t),len(s)


print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start

