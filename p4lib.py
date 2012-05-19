#!/usr/bin/env python
from celery.task import task
from celery.task.sets import subtask



@task
def add(x, y):
    return x + y



@task
def tsum(numbers):
    return sum(numbers)



