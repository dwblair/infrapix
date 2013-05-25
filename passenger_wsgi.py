import sys, os

# Switch to the virtualenv if we're not already there
INTERP = os.path.expanduser("~/venv/infrapixenv/bin/python")
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

from app import app as application

#def application(environ, start_response):
#    start_response('200 OK', [('Content-type', 'text/plain')])
#    return ["Hello, world! from %s: %s\n" % (sys.version, sys.executable)]
