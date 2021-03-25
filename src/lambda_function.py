import argparse
from datetime import datetime, timedelta
import json
import os
import requests

from datahub_metrics_ingest.DHMetric import DHMetric
from datahub_metrics_ingest.FormatterFactory import FormatterFactory
from datahub_metrics_ingest.ElasticsearchDAO import ElasticsearchDAO
from datahub_metrics_ingest.util import write_metrics_to_csv


USER_ID = '9k5r-tgy7'
ELASTICSEARCH_API_BASE_URL = os.environ.get('ELASTICSEARCH_API_BASE_URL')\
    if os.environ.get('ELASTICSEARCH_API_BASE_URL') is not None else 'http://localhost'
LIMIT_N = 50000
SOCRATA_AUTH = tuple(os.environ.get('SOCRATA_COMMA_DELIM_AUTH', ',').split(','))


def lambda_handler(event, context):
    # CloudWatch triggered lambda
    edate = datetime.strptime(event.get('time'), '%Y-%m-%dT%H:%M:%SZ')
    sdate = edate - timedelta(hours=24)
    ingest(sdate, edate, source_name='dtg')
    ingest(sdate, edate, source_name='scgc')
    
def ingest(sdate: datetime, edate: datetime, source_name: str = 'scgc', write_to_es: bool = True, elasticsearch_host: str = ELASTICSEARCH_API_BASE_URL, socrata_auth=SOCRATA_AUTH):
    if write_to_es:
        print(f'Ingesting {source_name} data from {sdate.isoformat()[:10]} - {edate.isoformat()[:10]} into metrics index at {elasticsearch_host}')
    else:
        print(f'Ingesting {source_name} data from {sdate.isoformat()[:10]} - {edate.isoformat()[:10]} to CSV file')
    try:
        asset_ids = get_data_asset_ids()
        done = False
        offset = 0
        all_metric_objs = []
        while not done:
            all_metrics = get_metrics(sdate, edate, offset, source_name, socrata_auth)
            offset += LIMIT_N
            if len(all_metrics) < LIMIT_N:
                done = True
            filtered_metrics = [i for i in all_metrics if i['asset_uid'] in asset_ids]
            formatter = FormatterFactory().get_formatter('socrata')
            metric_objs = formatter.get_data_objects(filtered_metrics, source_name)
            if write_to_es:
                ElasticsearchDAO(elasticsearch_host).write_to_elasticsearch(metric_objs)
            else:
                all_metric_objs += metric_objs
        return all_metric_objs
    except Exception as e:
        msg = f"Error ingesting {source_name} metrics for {sdate.isoformat()[:10]} ==> {str(e)}"
        print(msg)
        raise

def get_data_asset_ids():
    r = requests.get('http://api.us.socrata.com/api/catalog/v1', params={'for_user': USER_ID})
    catalog = r.json()['results']
    asset_ids = [i['resource']['id'] for i in catalog]
    return asset_ids

def get_metrics(sdate: datetime, edate: datetime, offset: int = 0, source_name: str = "scgc", socrata_auth=SOCRATA_AUTH):
    where_clause = f"timestamp >= '{sdate.strftime('%Y-%m-%d')}T00:00:00.000' AND timestamp < '{edate.strftime('%Y-%m-%d')}T00:00:00.000'"
    source_name_dict = {
        "scgc": "https://datahub.transportation.gov/resource/fa6d-d2xr.json",
        "dtg": "https://data.transportation.gov/resource/5uf5-scxk.json"
    }
    metrics = requests.get(
        source_name_dict[source_name],
        params={'$where': where_clause, '$limit': LIMIT_N, '$offset': offset},
        auth=socrata_auth
    ).json()
    return metrics


if (__name__ == '__main__'):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingest_historical", dest='ingest_historical', action='store_true', default=False,
        help="Ingest all daily DTG metrics from 2017-11-01 until yesterday. Otherwise, will ingest only metrics for yesterday.")
    parser.add_argument("--write_to_es", dest='write_to_es', action='store_true', default=False,
        help="Write metrics Elasticsearch. Otherwise, will write metrics to CSV.")
    parser.add_argument("--es_host", dest='es_host', default="http://localhost",
        help="Elasticsearch host to write the metrics to. Default: http://localhost.")
    parser.add_argument("--socrata_auth", dest='socrata_auth', default=None,
        help="Socrata auth to use, comma delimited with username followed by password. Will use `SOCRATA_COMMA_DELIM_AUTH` environment variable if not supplied.")
    
    args = parser.parse_args()
    
    if args.ingest_historical:
        edate = datetime.today() - timedelta(hours=24)
        sdate = datetime(2017,11,1)
    else:
        edate = datetime.today()
        sdate = edate - timedelta(hours=24)
    
    socrata_auth = SOCRATA_AUTH if not args.socrata_auth else tuple(args.socrata_auth.split(','))
    metric_objs_dtg = ingest(sdate, edate, source_name='dtg', write_to_es=args.write_to_es, elasticsearch_host=args.es_host, socrata_auth=socrata_auth)
    metric_objs_scgc = ingest(sdate, edate, source_name='scgc', write_to_es=args.write_to_es, elasticsearch_host=args.es_host, socrata_auth=socrata_auth)
    if not args.write_to_es:
        fp = f"socrata_metrics_{sdate.strftime('%Y-%m-%d')}.csv"
        write_metrics_to_csv(fp, metric_objs_dtg+metric_objs_scgc)
        print(f'Wrote {len(metric_objs_dtg)} dtg and {len(metric_objs_scgc)} scgc records to {fp}')