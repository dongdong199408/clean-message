import multiprocessing


# import os
# import gevent.monkey
#
# gevent.monkey.patch_all()
#
# import multiprocessing
# debug = True
# loglevel = 'debug'
# bind = '0.0.0.0:5000' # 监听IP放宽，以便于Docker之间、Docker和宿主机之间的通信
# pidfile = 'log/gunicorn.pid'
# logfile = 'log/debug.log'
#
# ## 定义同时开启的处理请求的进程数量，根据网站流量适当调整
# workers =  1
# worker_class = 'gunicorn.workers.ggevent.GeventWorker'
#
# x_forwarded_for_header = 'X-FORWARDED-FOR'
workers = 2   # 定义同时开启的处理请求的进程数量，根据网站流量适当调整
#worker_class = "egg:meinheld#gunicorn_worker"   # 采用gevent库，支持异步处理请求，提高吞吐量
worker_class = "gevent"
bind = "0.0.0.0:5000"    # 监听IP放宽，以便于Docker之间、Docker和宿主机之间的通信
