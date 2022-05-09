import os
import pprint
import time
import argparse
from google.oauth2 import service_account
from google.cloud import monitoring_v3

parser = argparse.ArgumentParser()

parser.add_argument("--team", action="store", dest="dep_team", help="The name of the team the deployed service belongs to", type=str)
parser.add_argument("--service", action="store", dest="dep_service", help="The name of the service or application being deployed", type=str)
parser.add_argument("--environment", action="store", dest="dep_environment", help="The environment into which the service/application is being deployed", type=str)
parser.add_argument("--status", action="store", dest="dep_status", help="Either 'started' or 'finished'", type=str)
parser.add_argument("--result", action="store", dest="dep_result", help="One of 'queued' 'pending' 'error' 'in_progress' 'failure' 'inactive' or 'success'", type=str)
parser.add_argument("--version", action="store", dest="dep_version", help="The version or commit being deployed", type=str)
parser.add_argument("--metric-value", action="store", dest="metric_value", help="The count to give for this deployment status - usually 1", type=int)
parser.add_argument("--auth-type", action="store", dest="auth_type", help="One of either sa-key or oidc to determine the type of authentication file provided", type=str)
args = parser.parse_args()

project_id = os.environ["GOOGLE_CLOUD_PROJECT"]

if args.auth_type == "sa-key":
    credentials = service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
elif args.auth_type == "oidc":
    credentials = service_account.IDTokenCredentials.from_service_account_file(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
else:
    print("Please provide either 'sa-key' or 'oidc' for the auth_type argument")
    exit(1)

print(f"Using service account {credentials.service_account_email} for {project_id}")

def write_time_series(project_id, metric_value):
    client = monitoring_v3.MetricServiceClient()
    project_name = client.common_project_path(project_id)

    series = monitoring_v3.types.TimeSeries()
    series.metric.type = 'custom.googleapis.com/deployment/status'
    # Using global as seemingly no better options... perhaps generic_task but that leads to
    # numerous resource labels that wouldn't serve much purpose or be very artificial
    # https://cloud.google.com/monitoring/custom-metrics/creating-metrics#custom-metric-resources
    series.resource.type = 'global'
    series.metric.labels['team'] = args.dep_team
    series.metric.labels['service'] = args.dep_service
    series.metric.labels['environment'] = args.dep_environment
    series.metric.labels['status'] = args.dep_status
    series.metric.labels['result'] = args.dep_result
    series.metric.labels['version'] = args.dep_version
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10 ** 9)
    interval = monitoring_v3.TimeInterval(
        {"end_time": {"seconds": seconds, "nanos": nanos}}
    )
    point = monitoring_v3.Point({"interval": interval, "value": {"int64_value": metric_value}})
    series.points = [point]
    pprint.pprint(series)
    client.create_time_series(name=project_name, time_series=[series])

class MissingProjectIdError(Exception):
    pass

# Google rate limit is 1 metric per series every 10 seconds
try:
  write_time_series(project_id, args.metric_value)
except:
  print(f"Probably hit the rate limit so forcing a sleep for 10 seconds...")
  time.sleep(11)
  write_time_series(project_id, args.metric_value)
