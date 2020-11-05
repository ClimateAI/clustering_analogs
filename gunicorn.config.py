import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
loglevel = "DEBUG"
errorlogfile = "./logs/gunicorn_error.log" 
accesslogfile =  "./logs/gunicorn_access.log"
capture_output = True
reload = True
