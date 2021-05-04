import socket
import logging
from prometheus_client import Counter, Gauge, start_http_server
from plotmanager.library.parse.configuration import get_instrumentation_settings

hostname = socket.gethostname()
settings = get_instrumentation_settings()


def _get_metrics():
    if settings.prometheus_enabled:
        gauge_plots_running = Gauge('chia_running_plots', 'Number of running plots', ['hostname', 'job'])
        counter_plots_completed = Counter('chia_completed_plots', 'Total completed plots', ['hostname', 'job'])
        start_http_server(settings.prometheus_port)
        return gauge_plots_running, counter_plots_completed
    else:
        gauge_plots_running = None
        counter_plots_completed = None
        return gauge_plots_running, counter_plots_completed


gauge_plots_running, counter_plots_completed = _get_metrics()


def set_plots_running(num_plots, job):
    if settings.prometheus_enabled:
        gauge_plots_running.labels(hostname=hostname, job=job).set(num_plots)
    else:
        logging.debug('Prometheus instrumentation not enabled')


def increment_plots_completed(amount, job):
    if settings.prometheus_enabled:
        counter_plots_completed.labels(hostname=hostname, job=job).inc(amount)
    else:
        logging.debug('Prometheus instrumentation not enabled')
