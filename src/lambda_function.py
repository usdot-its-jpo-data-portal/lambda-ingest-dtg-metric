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


def lambda_handler(event, context):
    # CloudWatch triggered lambda
    edate = datetime.strptime(event.get('time'), '%Y-%m-%dT%H:%M:%SZ')
    sdate = edate - timedelta(hours=24)
    ingest(sdate, edate)

def ingest(sdate: datetime, edate: datetime, write_to_es: bool = True):
    try:
        asset_ids = get_data_asset_ids()
        all_metrics = get_metrics(sdate, edate)
        filtered_metrics = [i for i in all_metrics if i['asset_uid'] in asset_ids]

        formatter = FormatterFactory().get_formatter('socrata')
        metric_objs = formatter.get_data_objects(filtered_metrics)
        if write_to_es:
            ElasticsearchDAO(ELASTICSEARCH_API_BASE_URL).write_to_elasticsearch(metric_objs)
        return metric_objs
    except Exception as e:
        msg = f"Error ingesting SCGC metrics for {sdate.isoformat()[:10]} ==> {str(e)}"
        print(msg)
        raise

def get_data_asset_ids():
    r = requests.get('http://api.us.socrata.com/api/catalog/v1', params={'for_user': USER_ID})
    catalog = r.json()['results']
    asset_ids = [i['resource']['id'] for i in catalog]
    return asset_ids

def get_metrics(sdate: datetime, edate: datetime):
    where_clause = f"timestamp >= '{sdate.strftime('%Y-%m-%d')}T00:00:00.000' AND timestamp < '{edate.strftime('%Y-%m-%d')}T00:00:00.000'"
    all_metrics = requests.get(
        'https://datahub.transportation.gov/resource/fa6d-d2xr.json',
        params={'$where': where_clause, '$limit': 50000}
    ).json()
    return all_metrics


if (__name__ == '__main__'):
    edate = datetime.today()
    sdate = edate - timedelta(hours=24)
    metric_objs = ingest(sdate, edate, write_to_es=False)
    write_metrics_to_csv(f"dtg_metrics_{sdate.strftime('%Y-%m-%d')}.csv", metric_objs)