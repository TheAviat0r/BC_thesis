STORAGE_PROMETHEUS = 'http://dashboard.stg.corp.acronis.com:9090'
QUERY_PARAMS = "{dc='eu6'}"
DATA_CENTERS = [
    'us3',
]
DATASETS_DIR = 'final'

TRAIN_START_TIME = '17/04/2018 00:00'
TRAIN_END_TIME = '22/05/2018 00:00'

TEST_START_TIME = '27/05/2018 00:00'
TEST_END_TIME = '03/06/2018 12:00'

QUERY_STEP='5m'

METRICS_TO_QUERY = [
    {
        'name' : 'abgw_write_reqs_total',
        'query' : "abgw_write_reqs_total{dc='us3', job='abgw'}"
    },
    {
        'name' : 'abgw_read_reqs_total',
        'query' : "abgw_read_reqs_total{dc='us3', job='abgw'}"
    },
]

# metrics that somehow are not collected in Prometheus
BAD_METRICS = [
    'abgw_account_lookup_fail_total',
    'abgw_iop_latency_ms_bucket',
    'abgw_req_latency_ms_bucket',
]

# local file with a list of available metrics
LOCAL_LABELS = 'local_labels.txt'
