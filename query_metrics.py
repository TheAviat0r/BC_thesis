import requests
import sys, os, time
import csv, json, argparse
import config

from datetime import datetime, timedelta
from config import STORAGE_PROMETHEUS, QUERY_PARAMS, METRICS_TO_QUERY

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
    endpoint = '{0}/api/v1/query_range'.format(STORAGE_PROMETHEUS)

    ts_start = int(datetime_to_unix(start))
    ts_end = int(datetime_to_unix(end))

    query = metric['query']

    response = requests.get(endpoint,
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
        print('%s: %s - %s - unable to extract data' % (metric['name'], start, end))
        failed_metrics.append(metric['name'])
        return None

    return results

def datetime_to_unix(dt):
    return time.mktime(dt.timetuple())

def query_one_hour_metric(metric, start, dc_name, step):
    end = start + timedelta(seconds=1*60*59) 
    ts_json = get_timeseries(metric, start, end, dc_name, step=step)
    if ts_json == None:
        return None 

    return ts_json

def query_metrics(metrics_to_query, start, end, csv_dir, step='1m'):
    dc_name = csv_dir[-3:]
    for metric in metrics_to_query:
        dt_start = datetime.strptime(start, "%d/%m/%Y %H:%M")
        dt_end = datetime.strptime(end, "%d/%m/%Y %H:%M")

        print('[query_metrics] query: %s - %s' % (metric['name'], dc_name))
        while dt_start < dt_end:
            ts_json = query_one_hour_metric(metric, dt_start, dc_name, step)
            dt_start = dt_start + timedelta(seconds=60*60)

            if ts_json == None:
                continue
            else:
                query_to_csv(ts_json, metric['name'], csv_dir)

def query_to_csv(results, name, csv_dir):
    file_name = '%s/%s.csv' % (csv_dir, name)
    open_mode = 'w'

    if os.path.exists(file_name):
        open_mode = 'a'

    csv_file = open(file_name, open_mode)

    field_names = ['time', name, 'instance']
    writer = csv.DictWriter(csv_file, fieldnames=field_names) 
    if open_mode == 'w':
        writer.writeheader()

    for ts_json in results:
        instance = ts_json['metric']['instance']
        for gauge in ts_json['values']:
            time = datetime.fromtimestamp(gauge[0]).strftime('%d_%m_%H:%M')
            writer.writerow({
                            'time': time,
                            name: gauge[1],
                            'instance': instance
                            })

    csv_file.close()

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

if __name__ == '__main__':
    train_dirs, test_dirs = prepare_directories()

    print('train dir: %s' % (str(train_dirs)))
    print('test dir: %s' % (str(test_dirs)))

    print('-------------------')
    for train_dir in train_dirs:
        query_metrics(config.METRICS_TO_QUERY, config.TRAIN_START_TIME,
                      config.TRAIN_END_TIME, train_dir, step=config.QUERY_STEP)
    print('-------------------')
    """
    for test_dir in test_dirs:
        query_metrics(config.METRICS_TO_QUERY, config.TEST_START_TIME,
                      config.TEST_END_TIME, test_dir, step=config.QUERY_STEP)
    """

    for metric in failed_metrics:
        print('Failed: ' + metric)

