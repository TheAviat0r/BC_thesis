STORAGE_PROMETHEUS = 'http://dashboard.stg.corp.acronis.com:9090'
QUERY_PARAMS = "{dc='eu6'}"
DATA_CENTER = 'eu6'
DATASETS_DIR = 'datasets'

TOTAL_SUM = True

METRICS_PREFIX = 'abgw'

# Metrics which have to be exported from Prometheus
metrics_to_query = [
    'abgw_conns',
    'abgw_accounts',
]

# metrics that somehow are not collected in Prometheus
BAD_METRICS = [
    'abgw_account_lookup_fail_total'
]

# local file with a list of available metrics
LOCAL_LABELS = 'local_labels.txt'
