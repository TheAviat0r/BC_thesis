import requests
import sys
import csv, json
import time
import argparse

from datetime import datetime
from config import STORAGE_PROMETHEUS, QUERY_PARAMS, metrics_to_query

def query_status(response_json):
    status = response_json['status']
    if status != 'success':
        return False

    return True

def get_metrics_labels(name_regexp='__name__'):
    query_string = '{0}/api/v1/label/{1}/values'.format(STORAGE_PROMETHEUS,
                                                        name_regexp)
    response = requests.get(query_string)
    results_json = response.json()

    status = query_status(results_json)
    if status == False:
        return None

    return results_json['data'][1:]

def get_timeseries(metric, start=1522615224, end=1522617224, step='1m'):
    total_query = '{0}/api/v1/query_range'.format(STORAGE_PROMETHEUS)
    query = metric + QUERY_PARAMS

    print '[get_time_series] total query: ' + total_query
    print '[get_time_series] metric query: ' + query

    response = requests.get(total_query,
                            params={
                                    'query': query,
                                    'start': start,
                                    'end': end,
                                    'step': step
                                   })
    results_json = response.json()

    status = query_status(results_json)
    if status == False:
        print '[get_time_series] Query had failed: ' + query
        return None

    results = results_json['data']['result']

#    print json.dumps(results, indent=4)

    return results

def verify_args(args):
    if args.start == None:
        print 'Start datetime should be specified'
        sys.exit()
    if args.end == None:
        print 'End datetime should be specified'
        sys.exit()

def datetime_to_unix(date):
    dt = datetime.strptime(date, "%d/%m/%Y %H:%M")

    return time.mktime(dt.timetuple())

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', help='start datetime of timeseries')
    parser.add_argument('-e', '--end', help='end datetime of timeseries')

    args = parser.parse_args()
    verify_args(args)

    return args

if __name__ == '__main__':
    args = parse_arguments()

    metrics_labels = get_metrics_labels()

    start = int(datetime_to_unix(args.start))
    end = int(datetime_to_unix(args.end))

    for metric in metrics_to_query:
        print '[main] query from command line: ' + metric

        ts_json = get_timeseries(metric, start, end)
        if ts_json == None or len(ts_json) == 0:
            print 'Unable to extract timeseries, exiting right now'
            sys.exit()

        for response in ts_json:
            instance = response['metric']['instance']
            name = response['metric']['__name__']

            for gauge in response['values']:
                print '{1} {0} at [{2}] value - {3}'.format(instance,
                                                            name,
                                                            gauge[0],
                                                            gauge[1])

            print '-----------'

