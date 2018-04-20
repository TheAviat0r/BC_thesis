STORAGE_PROMETHEUS = 'http://dashboard.stg.corp.acronis.com:9090'
QUERY_PARAMS = "{dc='eu6'}"
DATA_CENTER = 'eu6'
DATASETS_DIR = 'datasets'

TOTAL_SUM = True

METRICS_PREFIX = 'abgw'

# Metrics which have to be exported from Prometheus
METRICS_TO_QUERY = [
#    'abgw_conns',
#    'abgw_conns_total',
#    'abgw_read_reqs_total',
#    'abgw_read_bytes_total',
#    'abgw_write_reqs_total',
#    'abgw_write_bytes_total',
    'http_requests_total',
#    'abgw_iop_latency_ms_count',
]

# metrics that somehow are not collected in Prometheus
BAD_METRICS = [
    'abgw_account_lookup_fail_total',
    'abgw_iop_latency_ms_bucket',
    'abgw_req_latency_ms_bucket',
]

# local file with a list of available metrics
LOCAL_LABELS = 'local_labels.txt'
