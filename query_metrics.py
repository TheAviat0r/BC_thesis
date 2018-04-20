import requests
import sys, os, time
import csv, json, argparse
import config

from datetime import datetime
from config import STORAGE_PROMETHEUS, QUERY_PARAMS, METRICS_TO_QUERY

import pandas as pd
import numpy as np

failed_metrics = []

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

    print len(results_json['data'][1:])
    return results_json['data'][1:-3]

def get_timeseries(metric, start, end, step='1m'):
    total_query = '{0}/api/v1/query_range'.format(STORAGE_PROMETHEUS)
    if config.TOTAL_SUM == True:
        query = 'sum(' + metric + QUERY_PARAMS + ')'
    else:
        query = metric + QUERY_PARAMS

#    print '[get_time_series] total query: ' + total_query
#    print '[get_time_series] metric query: ' + query

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
        print metric + ' - unable to extract data'
        failed_metrics.append(metric)
        return None

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

def dump_timeseries(results, start, end):
    for ts_json in results:
#        print '[dump_time_series] dumping json part'

        for response in ts_json:
            instance = response['metric']['instance']
            name = response['metric']['__name__']

            for gauge in response['values']:
                print '{1} {0} at [{2}] value - {3}'.format(instance,
                                                            name,
                                                            gauge[0],
                                                            gauge[1])

            print '-----------'

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', help='start datetime of timeseries')
    parser.add_argument('-e', '--end', help='end datetime of timeseries')

    args = parser.parse_args()
    verify_args(args)

    return args

def get_csv_name(name, date):
    dt = datetime.strptime(date, "%d/%m/%Y %H:%M")
    csv_path = '{:s}/{:02d}_{:02d}'.format(config.DATASETS_DIR, dt.day,
                                           dt.month)
    if not os.path.exists(csv_path):
        os.mkdir(csv_path)

    name = '{:s}/{:s}.csv'.format(csv_path, name)

    return name

def query_metrics(metrics_to_query, start, end, step='1m'):
    results = []

    ts_start = int(datetime_to_unix(start))
    ts_end = int(datetime_to_unix(end))
    
    for metric in metrics_to_query:
        print '[query_metrics] query: ' + metric
        ts_json = get_timeseries(metric, ts_start, ts_end, step)
        if ts_json == None:
            continue

        query_to_csv(ts_json, metric, start)

        results.append(ts_json)

    print 'metrics_amount: ' + str(len(results))

    return results

def query_to_csv(results, name, start_time):
#    print '[query_to_csv] writing from json to csv: '
#    print 'name: ' + name

    file_name = get_csv_name(name, start_time)
    csv_file = open(file_name, 'w')


    field_names = ['time', name]
    if config.TOTAL_SUM == False:
        field_names.append('instance')

    writer = csv.DictWriter(csv_file, fieldnames=field_names) 
    writer.writeheader()

    for ts_json in results:
#        print json.dumps(ts_json['metric'], indent=4)
#        print json.dumps(ts_json['values'], indent=4)

        instance = 'DC_SUM'
        if len(ts_json['metric']) > 0:
            ''' if metric attibute is not empty,
                it means that user didn't specified an
                expr for that query.
            '''
            instance = ts_json['metric']['instance']
#        print 'instance: ' + instance

        for gauge in ts_json['values']:
            time = datetime.fromtimestamp(gauge[0]).strftime('%d_%m_%H:%M')
            if config.TOTAL_SUM == True:
                writer.writerow({
                                    'time': time,
                                    name: gauge[1]
                                })
            else:   
                writer.writerow({
                                    'instance': instance,
                                    'dc': config.DATA_CENTER,
                                    'time': time,
                                    name: gauge[1]
                                })

    csv_file.close()

def prepare_directories(start_time):
    if not os.path.exists(config.DATASETS_DIR):
        os.mkdir(config.DATASETS_DIR)

    dt = datetime.strptime(start_time, "%d/%m/%Y %H:%M")
    date_path = '{:s}/{:02d}_{:02d}'.format(config.DATASETS_DIR, dt.day, dt.month)

    if not os.path.exists(date_path):
        os.mkdir(date_path)

def count_metrics(all_metrics):
    stats_file = open('stat.txt', 'w')

    http_metrics_amount = len([m for m in metrics if m.startswith('http') and
                                                     m not in config.BAD_METRICS])

    abgw_metrics_amount = len([m for m in metrics if m.startswith('abgw') and
                                                     m not in config.BAD_METRICS])
    job_metrics_amount = len([m for m in metrics if m.startswith('job:abgw') and
                                                     m not in config.BAD_METRICS])

    abgw_metrics_amount = abgw_metrics_amount + job_metrics_amount

    node_metrics_amount = len([m for m in metrics if m.startswith('node') and
                                                     m not in config.BAD_METRICS])
    process_metrics_amount = len([m for m in metrics if m.startswith('process') and
                                                        m not in config.BAD_METRICS])
    pcs_metrics_amount = len([m for m in metrics if m.startswith('pcs') and
                                                    m not in config.BAD_METRICS])

    smart_metrics_amount = len([m for m in metrics if m.startswith('smart') and
                                                    m not in config.BAD_METRICS])

    total_node_metrics = node_metrics_amount + smart_metrics_amount
    total_process_metrics = pcs_metrics_amount + process_metrics_amount

    stats_file.write('http metrics - total {0}\n'.format(http_metrics_amount))
    stats_file.write('abgw metrics - total {0}\n'.format(abgw_metrics_amount))
    stats_file.write('node metrics - total {0}\n'.format(total_node_metrics))
    stats_file.write('process metrics - total {0}\n'.format(total_process_metrics))

    stats_file.close()

def compare_with_server(server_metrics):
    if not os.path.exists(config.LOCAL_LABELS):
        metrics_output = open(config.LOCAL_LABELS, 'w')
        for metric in metrics:
            metrics_output.write(metric + "\n")
        metrics_output.close()
    else:
        local_metrics_file = open(config.LOCAL_LABELS, 'r')
        local_metrics = local_metrics_file.read().split()
        local_metrics_file.close()
        difference = list(set(local_metrics) - set(server_metrics))
        print difference
        if len(difference) > 0:
            'WARNING: metrics have changed on server'
            'NEW METRICS: ' + str(difference)
            return False

    return True

if __name__ == '__main__':
    args = parse_arguments()

    prepare_directories(args.start)

    metrics = get_metrics_labels()
    count_metrics(metrics)
    compare_result = compare_with_server(metrics)
    if compare_result == False:
        print 'false'
        sys.exit()

    necessary_metrics = [name for name in metrics
                         if name.startswith(config.METRICS_PREFIX) and
                         name not in config.BAD_METRICS]

    results = query_metrics(config.METRICS_TO_QUERY, args.start, args.end, '5m')

    for metric in failed_metrics:
        print 'Failed: ' + metric


