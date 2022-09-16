import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
bind = '0.0.0.0:5001'
timeout = 0
accesslog = 'logs/access.log'
errorlog = 'logs/err.log'
capture_output = True
loglevel = "debug"
access_log_format = '%({X-Real-IP}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" '