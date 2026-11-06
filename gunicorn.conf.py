import os

bind = f"0.0.0.0:{int(os.getenv('PORT', '8000'))}"
workers = 1
threads = 2
worker_class = 'gthread'
timeout = 30
accesslog = None
errorlog = '-'
forwarded_allow_ips = ''
