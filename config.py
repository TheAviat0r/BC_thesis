STORAGE_PROMETHEUS = 'http://dashboard.stg.corp.acronis.com:9090'
QUERY_PARAMS = "{dc='eu6'}"
DATA_CENTERS = [
    'us3',
]
DATASETS_DIR = 'final'

# Latest period with anomalies 
TRAIN_START_TIME = '25/05/2018 14:00'
TRAIN_END_TIME = '10/06/2018 15:00'
#TRAIN_START_TIME = '17/04/2018 00:00'
#TRAIN_END_TIME = '22/05/2018 00:00'

TEST_START_TIME = '27/05/2018 00:00'
TEST_END_TIME = '03/06/2018 12:00'

QUERY_STEP='5m'

METRICS_TO_QUERY = [
    {
        'name' : 'abgw_file_lookup_errs_rate',
        'query': "sum(irate(abgw_file_lookup_errs_total{dc='us3', err!='OK'}[5m])) by (instance)",
    },
    #{
    #   'name' : "abgw_account_pull_errs_total",
    #    'query' : "sum(abgw_account_pull_errs_total{dc='us3', err!='OK'}) by (instance)",
    #}
    #{
    #    'name' : "abgw_account_pull_errs_total",
    #    'query' : "sum(abgw_account_pull_errs_total{dc='us3', err!='OK'}",
    #}
    #{
    #    'name' : 'abgw_io_limiting_failures_rate',
    #    'query' : "sum(irate(abgw_io_limiting_failures_total{dc='us3'}[5m])) by (instance)",
    #},
    #{
    #    'name' : 'abgw_write_rollback_bytes_rate',
    #    'query' : "irate(abgw_write_rollback_bytes_total{dc='us3'}[5m])",
    #},
    #{
    #    'name' : 'abgw_pull_progress_bytes_total',
    #    'query' : "abgw_pull_progress_bytes_total{dc='us3'}",
    #},
    #{
    #    'name' : 'abgw_req_errs_total',
    #    'query' : "sum(abgw_req_errs_total{dc='us3', err!='OK'}) by (instance)"
    #},
]

# metrics that somehow are not collected in Prometheus
BAD_METRICS = [
    'abgw_account_lookup_fail_total',
    'abgw_iop_latency_ms_bucket',
    'abgw_req_latency_ms_bucket',
]

# local file with a list of available metrics
LOCAL_LABELS = 'local_labels.txt'
