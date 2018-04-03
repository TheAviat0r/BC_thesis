STORAGE_PROMETHEUS = 'http://dashboard.stg.corp.acronis.com:9090'
QUERY_PARAMS = "{dc='eu6'}"
DATA_CENTER = 'eu6'

DATASETS_DIR = 'datasets'

METRICS_PREFIX = 'abgw'

metrics_to_query = [
    'abgw_conns',
    'abgw_accounts',
#    'abgw_fds'
]

BAD_METRICS = [
    'abgw_account_lookup_fail_total'
]
