#!/usr/bin/env python
import pika

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
    print " [x] Received %r" % (body,)

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

channel.start_consuming()

