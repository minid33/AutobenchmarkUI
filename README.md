# AutobenchmarkUI

This web service takes performance benchmark data and graphs the results over time.

# Features

* Overview of all benchmarks in one page, grouped by machine name or the benchmark
* A Detailed view of a benchmark on a given machine
* Single exection metric views

# Entering results

When your benchmarking tool completes an execution it POSTs a JSON object via HTTP to http://<yourhostname>:<port>/storeResultEntry

This should be in the format of a posted result:

     structure = { 
        'branch': string,
        'buildnumber': int,
        'entrytime': datetime.datetime, (isoformatted in JSON)
        'machinename': string,
        'metrics': {
          keyname: list
        },
        'testcasename': string
    }


Metrics should have a key which represents what is being measured, like cputime or fps and then a list of lists in this format, this keyname will be displayed in the graph titles:

    'metrics': {
      fps:[[<isoformatted_datetime>, 40.0],[<isoformatted_datetime>, 45.2].....],
      cputime: [[<isoformatted_datetime>, 80.0],[<isoformatted_datetime>, 90.1].....]
    }


You can post results with different metric keys, this project was designed with video game benchmark results in mind but should be work with (or be easily adaptable for) different software if you want to measure something else.

# Viewing results

If I documented this correctly and you've followed the instructions you should be able to open your browser and punch in [http://localhost:5000](http://localhost:5000) (unless you changed the hostname)

and get a nice page like this, which probably doesnt have as many graphs or results in those graphs to start with:

![Benchmark results page](http://i.imgur.com/sniMIK4.png "Benchmark results")


## Requirements

There's no reason this wont work on a linux distro but I've only tested this on windows 7/8/Server 2008.

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
7. Create a collection in the autobenchmark database called configuration and add a key inside that called 'activebranch' with the value of the stringname of the branch you intend to start benchmarking with.
8. `python runserver.py`

## To run this using Apache HTTPD:


### Additional requirements

Install the following:
* mod_wsgi 3.5+ [Installation Instructions](https://code.google.com/p/modwsgi/wiki/InstallationInstructions)
* [Apache HTTPD 2.4+](http://httpd.apache.org/download.cgi)

Then follow these steps:
1. Follow the instructions above upto and including step 7.
2. Include the autobenchmarkui.conf in your httpd.conf
3. Check that the paths match your environment and point to the autobenchmarkui.wsgi
4. Check that the pathing matches your environment for autobenchmark.wsgi
5. Restart apache

## Using another production webserver
At its core the AutobenchmarkUI is simply a flask application. You can read alternative ways to deploy [here](http://flask.pocoo.org/docs/deploying/)


# Things that I'd like to do to this project:
* Remove dependancy on mongokit, it was initially introduced to enforce structure on our data but this really kills the power of a NoSQL to add new structures when we need to.
* Evaluate using an alternative graphing library that has a more open liscence.
* Clean up the pip_requirements.txt to remove requirements that are not used.
* Rename testcasename to benchmarkname
* 
# Running the unit tests

These tests are run using nose.

You will need to either fix the path to mongod.exe in the tests's __init__.py or add the binaries into /AutobenchmarkUI/bin/win_x64/2.4.8. I haven't tested it but you can probably point it to /usr/bin or where ever your distro put the mongod binary on linux.
