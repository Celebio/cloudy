#!/usr/bin/env python
from celery.task import chord
from p4lib import add, tsum

import time


result = chord(add.subtask((i, i)) for i in xrange(100))(tsum.subtask()).get()

#result = add.delay(4,4)

print result

#result.ready()
#print result.result
#time.sleep(10)
#print result.ready()
#print result.result


