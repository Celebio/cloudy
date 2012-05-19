#!/usr/bin/env python
from test import add
import time


result = add.delay(4,4)


print result.ready()
print result.result
time.sleep(3)
print result.ready()
print result.result


