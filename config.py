STORAGE_PROMETHEUS = 'http://dashboard.stg.corp.acronis.com:9090'
QUERY_PARAMS = "{dc='eu6'}"
DATA_CENTERS = [
    'eu6',
    'eu7',
]
DATASETS_DIR = 'datasets'

TRAIN_START_TIME = '01/05/2018 00:00'
TRAIN_END_TIME = '01/05/2018 03:00'

TEST_START_TIME = '01/05/2018 03:00'
TEST_END_TIME = '01/05/2018 05:00'

QUERY_STEP='5m'

METRICS_TO_QUERY = [
    ('abgw_req_latency_ms_sum', 'sum', None),
    ('abgw_iop_latency_ms_count', 'sum', None),
    ('abgw_iop_latency_ms_sum', 'sum', None),
    ('abgw_write_reqs_total', 'sum', None),
    ('abgw_read_reqs_total', 'sum', None),
    ('abgw_stat_reqs_total', 'sum', None),
    ('abgw_write_bytes_total', 'sum', None),
    ('abgw_read_bytes_total', 'sum', None),
]

RATE_METRICS = [
    'abgw_conns_total',
    'http_requests_total',
]

# metrics that somehow are not collected in Prometheus
BAD_METRICS = [
    'abgw_account_lookup_fail_total',
    'abgw_iop_latency_ms_bucket',
    'abgw_req_latency_ms_bucket',
]

# local file with a list of available metrics
LOCAL_LABELS = 'local_labels.txt'
