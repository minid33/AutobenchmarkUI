# AutobenchmarkUI

This web service takes performance benchmark data and graphs the results over time.

## Requirements


* [Mongodb](http://www.mongodb.org/downloads) 2.4.8+
* [Lastest Python 2.7.x](http://python.org/download/) with [Virtualenv](http://www.virtualenv.org/en/latest/virtualenv.html#installation) and [Pip](http://www.pip-installer.org/en/latest/installing.html)

## Installing


To run this locally using the Flask development server:

1. rename autobenchmarkui/config_example.py to autobenchmarkui/config.py
2. [Create a new virtualenv](http://www.virtualenv.org/en/latest/virtualenv.html/)
3. Activate the virtualenv, the following instructions assume you have done this.
4. Use pip to install the python requirements `pip install -r pip_requirements.txt`
5. Stand up your monogdb instance or cluster
6. Ensure that the configuration in autobenchmarkui/config.py correctly points to your Mongo instance
7. `python runserver.py`

## To run this using Apache HTTPD:


### Additional requirements

Install the following:
* mod_wsgi 3.5+ [Installation Instructions](https://code.google.com/p/modwsgi/wiki/InstallationInstructions)
* [Apache HTTPD 2.4+](http://httpd.apache.org/download.cgi)

Then follow these steps:
1. Follow the instructions above upto and including step 6.
2. Include the autobenchmarkui.conf in your httpd.conf
3. Check that the paths match your environment and point to the autobenchmarkui.wsgi
4. Check that the pathing matches your environment for autobenchmark.wsgi
5. Restart apache

## Using another production webserver
At its core the AutobenchmarkUI is simply a flask application. You can read alternative ways to deploy [here](http://flask.pocoo.org/docs/deploying/)
