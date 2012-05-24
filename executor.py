#!/usr/bin/env python
from celery.task import chord
from p4lib import *

import time
import pika



#result = f.delay([], g1, 10)

result = fibo.delay([], None, 10)


credentials = pika.PlainCredentials('celmquser', 'celmq4rox')

connection = pika.BlockingConnection(pika.ConnectionParameters(
    credentials=credentials,
    host='94.23.52.124',
    virtual_host='celmqvhost'
))
channel = connection.channel()

channel.queue_declare(queue='hello')

print ' [*] Waiting for messages. To exit press CTRL+C'

def callback(ch, method, properties, body):
    channel.stop_consuming()
    print " [x] Received %r" % (body,)
    foo = raw_input("am i right?")

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

channel.start_consuming()




#resAtt = [0]
#add3 = bAdd.subtask(args=(3, ))


#result = bAdd.delay(1, 2, callback=add3).get()

#while not isinstance(result, int):
#    result = result.get()

#add3 = cAdd.subtask(args=(3, ))
#result = cAdd.delay(3,5, callback=add3).get()
#print "result:", result


#result = chord(add.subtask((i, i)) for i in xrange(100))(tsum.subtask()).get()

#result = add.delay(4,4)

#print result

#result.ready()
#print result.result
#print resAtt[0]
#time.sleep(10)
#print result.ready()
#print result.result
#print resAtt[0]


#bAdd.delay(2, 2, callback=bAdd.subtask((8, )))
