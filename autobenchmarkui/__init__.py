import datetime
import json
import os
import sys

import bson
from flask import Flask, jsonify, render_template, request
from flask.ext.cache import Cache

import config
import dbmath
import dbmodel
import floatliststatistics

CONNDATA = None

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
cache = Cache()
cache.init_app(app, config={'CACHE_TYPE': 'simple'})

DEPLOY_MACHINES = ['TESTLAB-TA-MIN', 'TESTLAB-TA-REC']

THUMBNAIL_DAYS = 30
DETAIL_DAYS = 120


def round_date(dt):
    rounded = datetime.datetime(dt.year, dt.month, dt.day, dt.hour)
    # Zero out hour/min/sec/etc and return isostr
    return rounded.isoformat()

@cache.cached(timeout=30)
@app.route('/thumbjson')
def thumbjson():
    # TODO: Add support for 'calc of calcs' instead of max
    all_json = get_graph_data_from_request(request, THUMBNAIL_DAYS)

    all_results = {}
    for benchname, entries in all_json['results'].items():
        dtToEntries = {}
        for entry in entries:
            roundedDt = round_date(entry['key'])
            dtToEntries.setdefault(roundedDt, []).append(entry['value'])
        dtToSingleEntry = {dt: dbmath.mean(items) for dt, items in dtToEntries.iteritems()}
        newresult = [{'key': k, 'value': v} for k, v in sorted(dtToSingleEntry.iteritems())]
        all_results[benchname] = newresult
    # Just mutate the original results since we're throwing them away.
    result = all_json
    result['results'] = all_results
    return jsonify(result)

@cache.cached(timeout=30)
@app.route('/scatterjson')
def scatterjson():
    return jsonify(get_graph_data_from_request(request, DETAIL_DAYS))


@app.route('/')
def index():
    return machinegallery('TESTLAB-TA-REC')


@app.route('/radiator/<int:days>')
def radiator(days):
    kwargs = get_base_kwargs()
    kwargs.update(get_kwargs_from_request(request, days))
    # kwargs['metric'] = kwa
    # kwargs['benchma'] = 'Autopilot'
    # kwargs['machinename'] = 'TESTLAB-TA-REC'
    return render_template('radiator.html', **kwargs)


@app.route('/machine/<machinename>')
def machinegallery(machinename):
    kwargs = get_base_kwargs()
    kwargs['gallerystatic'] = machinename
    kwargs['gallerystaticKey'] = 'machinename'
    kwargs['galleryvertical'] = kwargs['benchmarks']
    kwargs['galleryverticalKey'] = 'bench'
    return render_template('gallery.html', **kwargs)


@app.route('/bench/<bench>')
def benchgallery(bench):
    kwargs = get_base_kwargs()
    kwargs['gallerystatic'] = bench
    kwargs['gallerystaticKey'] = 'bench'
    kwargs['galleryvertical'] = kwargs['machines']
    kwargs['galleryverticalKey'] = 'machinename'
    return render_template('gallery.html', **kwargs)


@app.route('/detail')
def detail():
    kwargs = get_base_kwargs()
    kwargs.update(get_kwargs_from_request(request, DETAIL_DAYS))
    return render_template('detail.html', **kwargs)


@app.route('/executionjson/<id_>')
def executionjson(id_):
    coll = CONNDATA()[2]
    obj = coll.find_one({'_id': bson.ObjectId(id_)})
    if obj is None:
        raise NotImplementedError('404')
    resultlist = []
    metric = request.args['metric']
    for entrytime, value in obj['metrics'][metric]:
        resultlist.append(
            {'key': entrytime,
             'value': value,
             'id': -1})

    result_values = [i['value'] for i in resultlist]
    result = {
        'results': {'execution': resultlist},
        'empty': False,
        'metric': metric,
        'meta': {
            'max': "{0:.3f}".format(max(result_values)),
            'min': "{0:.3f}".format(min(result_values)),
            'average': "{0:.3f}".format(floatliststatistics.get_average(result_values)),
            'range': "{0:.3f}".format(floatliststatistics.get_range(result_values)),
            'mode': "{0:.3f}".format(floatliststatistics.get_mode(result_values)),
        }
    }
    return jsonify(result)


@app.route('/execution/<id_>')
def execution(id_):
    kwargs = {'id': id_,
              'metric': request.args['metric'],
              'title': request.args.get('title', 'NO TITLE'),
              'appconfig': app.config,
    }
    return render_template('execution.html', **kwargs)


def get_graph_data(baseSearch, metric, aggpoint, daysToReturn, format_results):
    coll = CONNDATA()[2]

    if int(daysToReturn) != 0:
        baseSearch = dbmodel.set_search_date_restriction(baseSearch, int(daysToReturn))

    cursor = coll.find(
        baseSearch,
        {aggpoint: 1, 'benchmarkname': 1, 'entrytime': 1, 'buildnumber': 1, 'branch': 1}
    )

    data = format_results(cursor, metric)
    return {'results': data,
            'empty': not bool(data),
            'metric': metric}


def get_kwargs_from_request(request_, default_days):
    kwargs = dict(request_.args.items())
    REQUIRED_KEYS = ['metric', 'machinename']
    for key in REQUIRED_KEYS:
        if key not in kwargs:
            raise KeyError(key)  # Return invalid request instead

    OPTIONAL_KEYS_AND_DEFAULTS = {
        'days': default_days,
        'calc': 'mean',
        'bench': None,
    }
    for key, default in OPTIONAL_KEYS_AND_DEFAULTS.items():
        kwargs.setdefault(key, default)
    return kwargs


def get_graph_data_from_request(request_, default_days):
    kwargs = get_kwargs_from_request(request_, default_days)
    metricAndCalc = "AggregateData.%s.%s" % (kwargs['metric'], kwargs['calc'])

    search = {
        'machinename': kwargs['machinename'],
        'benchmarkname': kwargs['bench'],
        metricAndCalc: {'$exists': True}}

    for k, v in search.items():
        if v is None:
            search.pop(k)

    def formatCursor(cursor, metric):
        return dbmodel.format_cursor_to_scatterjson(cursor, metric, kwargs['calc'])

    result = get_graph_data(
        search,
        kwargs['metric'],
        metricAndCalc,
        kwargs['days'],
        formatCursor)

    result['machinename'] = kwargs['machinename']
    result['bench'] = kwargs['bench']
    return result


@app.route('/storeResultEntry/', methods=['PUT'])
def store_result_entry():
    """
    This page only accepts PUT requests with json encoded content.

    The resultdata is then put into the mongodb.
    """
    # get the data
    if validate_entry(request.data):

        resultdata = dict(json.loads(request.data))
        resultdata = append_aggregated_data(resultdata)
        # send it to mongo
        dbmodel.insert_benchmark_result(resultdata, CONNDATA()[2])
        app.logger.debug('Data Sucesfully Stored into the DB')
        return jsonify(resultdata)
    else:
        bad = app.make_response(("The data sent is not valid", 400, {}))
        return bad


def append_aggregated_data(resultdata):
    """
    Appends an aggregated metrics key onto a result set.

    :param resultdata: The resultdata should be a dictionary consistent with
        the dbmodel
    :return: The result set with aggregated data appended.
    """
    resultdata['AggregateData'] = dict(resultdata['metrics'])
    for key, entryTimesAndValues in resultdata['AggregateData'].items():
        metricvals = [item[1] for item in entryTimesAndValues]
        resultdata['AggregateData'][key] = {
            'mean': dbmath.mean(metricvals),
            'median': dbmath.median(metricvals),
            'stddev': dbmath.standard_deviation(metricvals),
            'min': min(metricvals),
            'max': max(metricvals)
        }
    return resultdata


def validate_entry(json_attempt):
    """
    Accepts a string of JSON.
    :return: This returns True if the data is valid.
    """
    try:
        data = json.loads(json_attempt)
    except Exception:
        return False
    requiredfields = ['branch', 'buildnumber', 'machinename', 'benchmarkname']
    for key in requiredfields:
        if key not in data.keys():
            app.logger.info(
                'The required field %s was missing, rejected entry', key)
            return False
    app.logger.debug('Valid JSON Entered, Storing Result to DB')
    return True


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        if request.form.keys()[0] == 'dropbenchmark':
            dbmodel.drop_benchmark(request.form['dropbenchmark'], CONNDATA()[1].benchresults)
        else:
            raise RuntimeError('Unrecognized action: %s' % request.form.keys()[0])
    kwargs = get_base_kwargs()
    return render_template('admin.html', **kwargs)


def get_base_kwargs():
    return {
        'machines': dbmodel.get_unique_values_for_key('machinename', CONNDATA),
        'benchmarks': sorted(dbmodel.get_unique_values_for_key('benchmarkname', CONNDATA)),
        'metrics': ['fps', 'frametime', 'workingset', 'timedelta'],
        'appconfig': app.config
    }


def configure_app(configname=None):
    try:
        cfg = config.Configs[configname or os.getenv('BENCHUI_CONFIG')]
    except KeyError:
        sys.stderr.write(
            'BENCHUI_CONFIG env var must be defined to one of: %s' %
            config.Configs.keys())
        sys.exit(2)

    global CONNDATA
    CONNDATA = dbmodel.create_mongo_objs_getter_from_config(cfg)
    app.config.from_object(cfg)
    return cfg
