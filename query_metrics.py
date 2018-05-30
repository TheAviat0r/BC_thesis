import requests
import sys, os, time
import csv, json, argparse
import config

from datetime import datetime, timedelta
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

    print('Total amount of metrics: %d' % (len(results_json['data'][1:])))

    return results_json['data'][1:-3]

def get_timeseries(metric, start, end, dc_name, step='1m'):
    assert metric[1] == 'sum' or metric[1] == 'none'

    total_query = '{0}/api/v1/query_range'.format(STORAGE_PROMETHEUS)


    ts_start = int(datetime_to_unix(start))
    ts_end = int(datetime_to_unix(end))

    if metric[2] != None:
        query = "%s{dc='%s',%s}" % (metric[0], dc_name, metric[2])
    else:
        query = "%s{dc='%s'}" % (metric[0], dc_name)

    if metric[1] == 'sum':
        query = 'sum(%s)' % query

#    print('[get_time_series] metric query: ' + query)

    response = requests.get(total_query,
                            params={
                                    'query': query,
                                    'start': ts_start,
                                    'end': ts_end,
                                    'step': step
                                    })
    results_json = response.json()

    status = query_status(results_json)
    if status == False:
        print('[get_time_series] Query had failed: ' + query)
        print('Exiting right now')
        sys.exit()

    results = results_json['data']['result']

    if len(results) == 0:
        print(metric[0] + ' - unable to extract data')
        failed_metrics.append(metric[0])
        return None

    return results

def datetime_to_unix(dt):
    return time.mktime(dt.timetuple())

def dump_timeseries(results, start, end):
    for ts_json in results:
        for response in ts_json:
            instance = response['metric']['instance']
            name = response['metric']['__name__']

            for gauge in response['values']:
                print('{1} {0} at [{2}] value - {3}'.format(instance,
                                                            name,
                                                            gauge[0],
                                                            gauge[1]))

            print('-----------')

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', help='start datetime of timeseries')
    parser.add_argument('-e', '--end', help='end datetime of timeseries')

    args = parser.parse_args()
    verify_args(args)

    return args

def query_one_hour_metric(metric, start, dc_name, step, counter):
    end = start + timedelta(seconds=60*59) 
    ts_json = get_timeseries(metric, start, end, dc_name, step)
    if ts_json == None:
        return None 

    return ts_json

def query_metrics(metrics_to_query, start, end, csv_dir, step='1m'):
    for metric in metrics_to_query:
        dt_start = datetime.strptime(start, "%d/%m/%Y %H:%M")
        dt_end = datetime.strptime(end, "%d/%m/%Y %H:%M")

        print('[query_metrics] query: ' + metric[0])
        dc_name = csv_dir[-3:]
        counter=0
        while dt_start < dt_end:
            ts_json = query_one_hour_metric(metric, dt_start, dc_name, step, counter)
            if ts_json == None:
                continue

            query_to_csv(ts_json, metric[0], csv_dir, counter)
            counter = counter + 1
            dt_start = dt_start + timedelta(seconds=60*60)

def query_to_csv(results, name, csv_dir, write_counter):
    file_name = '%s/%s.csv' % (csv_dir, name)
    csv_file = None
    if write_counter == 0:
        csv_file = open(file_name, 'w')
    else:
        csv_file = open(file_name, 'a')

    field_names = ['time', name]

    writer = csv.DictWriter(csv_file, fieldnames=field_names) 
    if write_counter == 0:
        writer.writeheader()

    for ts_json in results:
        for gauge in ts_json['values']:
            time = datetime.fromtimestamp(gauge[0]).strftime('%d_%m_%H:%M')
            writer.writerow({
                            'time': time,
                            name: gauge[1]
                            })

    csv_file.close()

"""
def query_metrics(metrics_to_query, start, end, csv_dir, step='1m'):
    results = []

    for metric in metrics_to_query:
        print('[query_metrics] query: ' + metric[0])
        dc_name = csv_dir[-3:]
        ts_json = get_timeseries(metric, start, end, dc_name, step)
        if ts_json == None:
            continue

        query_to_csv(ts_json, metric[0], csv_dir)

        results.append(ts_json)

    return results

def query_to_csv(results, name, csv_dir):
    file_name = '%s/%s.csv' % (csv_dir, name)
    csv_file = open(file_name, 'w')

    field_names = ['time', name]

    writer = csv.DictWriter(csv_file, fieldnames=field_names) 
    writer.writeheader()

    for ts_json in results:
        for gauge in ts_json['values']:
            time = datetime.fromtimestamp(gauge[0]).strftime('%d_%m_%H:%M')
            writer.writerow({
                            'time': time,
                            name: gauge[1]
                            })

    csv_file.close()
"""
def prepare_directories():
    if not os.path.exists(config.DATASETS_DIR):
        os.mkdir(config.DATASETS_DIR)

    train_dirs = []
    test_dirs = []

    for dc_name in config.DATA_CENTERS:
        train_dir = '%s/%s' % (config.DATASETS_DIR, 'train_%s' % (dc_name))
        test_dir = '%s/%s' % (config.DATASETS_DIR, 'test_%s' % (dc_name))

        if not os.path.exists(train_dir):
            os.mkdir(train_dir)
        if not os.path.exists(test_dir):
            os.mkdir(test_dir)

        train_dirs.append(train_dir)
        test_dirs.append(test_dir)

    return train_dirs, test_dirs

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
        if len(difference) > 0:
            'WARNING: metrics have changed on server'
            'NEW METRICS: ' + str(difference)
            return False

    return True

if __name__ == '__main__':
    train_dirs, test_dirs = prepare_directories()
    print('train dir: %s' % (str(train_dirs)))
    print('test dir: %s' % (str(test_dirs)))

    metrics = get_metrics_labels()
    count_metrics(metrics)

    compare_result = compare_with_server(metrics)
    if compare_result == False:
        print('Server metrics have been updated, exiting right now')
        sys.exit()

    print('-------------------')
    for train_dir in train_dirs:
        query_metrics(config.METRICS_TO_QUERY, config.TRAIN_START_TIME,
                      config.TRAIN_END_TIME, train_dir, step=config.QUERY_STEP)
    print('-------------------')
    for test_dir in test_dirs:
        query_metrics(config.METRICS_TO_QUERY, config.TEST_START_TIME,
                      config.TEST_END_TIME, test_dir, step=config.QUERY_STEP)

    for metric in failed_metrics:
        print('Failed: ' + metric)

