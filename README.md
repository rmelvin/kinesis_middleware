# Kinesis Django Middleware

A Python 3.6 / Django 2.x middleware that intercepts requests, generates records, and writes 
records to an AWS Kinesis stream. Requests are intercepted based on the request method being called 
and the model associated with the Django view function being accessed.

