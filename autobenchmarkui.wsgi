# This file is here for reference, this is not what we're using in production
# but its very similar. There's no promise that it will work as it is now.

activate_this = r"autobenchmarkui\virtualenv\Scripts\activate_this.py"
execfile(activate_this, dict(__file__=activate_this))

import sys
import os
curdir = os.path.dirname(__file__)
sys.path.append(r'%s\autobenchmarkui' % curdir)


os.environ['BENCHUI_CONFIG'] = 'prod'

from runserver import app as application