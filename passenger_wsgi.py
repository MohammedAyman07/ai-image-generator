import sys, os

# Add the project directory to the sys.path
# This ensures that python can find your app.py file
INTERP = os.path.expanduser("/var/www/html/cgi-bin/python_bin")
if os.path.exists(INTERP):
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

from app import app as application
