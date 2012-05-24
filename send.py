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

channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
print " [x] Sent 'Hello World!'"
connection.close()

