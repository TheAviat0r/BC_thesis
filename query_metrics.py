import requests
import sys
import csv, json
import time
import argparse
import config

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
        print 'Exiting right now'
        sys.exit()

    results = results_json['data']['result']

    if len(results) == 0:
        print 'Unable to extract data, json is empty.'
        print 'Exiting right now.'
        sys.exit()

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

def get_csv_name(name, date):
    dt = datetime.strptime(date, "%d/%m/%Y %H:%M")
    name = '{:s}/{:s}_{:02d}_{:02d}_{:04d}.csv'.format(config.DATASETS_DIR, 
                                                       name, dt.day,
                                                       dt.month, dt.year)
    return name

def query_metrics(metrics_to_query, start, end):
    results = []

    for metric in metrics_to_query:
        print '[query_metrics] query: ' + metric
        ts_json = get_timeseries(metric, start, end)

        results.append(ts_json)

    return results

def dump_timeseries(results, start, end):
    for ts_json in results:
        print '[dump_time_series] dumping json part'

        for response in ts_json:
            instance = response['metric']['instance']
            name = response['metric']['__name__']

            for gauge in response['values']:
                print '{1} {0} at [{2}] value - {3}'.format(instance,
                                                            name,
                                                            gauge[0],
                                                            gauge[1])

            print '-----------'

def query_to_csv(results, start_time):
    for ts_json in results:
        print '[query_to_csv] writing from json to csv: '

        for node_response in ts_json:
            instance = node_response['metric']['instance']
            name = node_response['metric']['__name__']

            file_name = get_csv_name(name, start_time)
            csv_file = open(file_name, 'wb')

            field_names = ['name', 'dc', 'instance', 'time', 'value']
            writer = csv.DictWriter(csv_file, fieldnames=field_names) 

            writer.writeheader()

            for gauge in node_response['values']:
                writer.writerow({
                                    'name': name,
                                    'instance': instance,
                                    'dc': config.DATA_CENTER,
                                    'time': gauge[0],
                                    'value': gauge[1]
                                })

            csv_file.close()

if __name__ == '__main__':
    args = parse_arguments()

    start = int(datetime_to_unix(args.start))
    end = int(datetime_to_unix(args.end))

    results = query_metrics(metrics_to_query, start, end)

#    dump_timeseries(results, start, end)
    query_to_csv(results, args.start)


