# Fix Render worker timeouts and socket failures

worker_class = "eventlet"
workers = 1
timeout = 300
graceful_timeout = 300
keepalive = 5

# Disable worker auto-reload behavior that causes "Bad file descriptor"
reload = False
loglevel = "info"
