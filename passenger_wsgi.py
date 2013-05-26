import sys, os

# Switch to the virtualenv if we're not already there
#INTERP = os.path.expanduser("~/venv/infrapixenv/bin/python")
#if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)
#sys.path.append(os.getcwd())

from app import app as application

