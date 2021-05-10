import socket
import logging


def _get_metrics(instrumentation_settings):
    from prometheus_client import Counter, Gauge, start_http_server
    gauge_plots_running = None
    counter_plots_completed = None
    if instrumentation_settings.get('prometheus_enabled', False):
        gauge_plots_running = Gauge('chia_running_plots', 'Number of running plots', ['hostname', 'queue'])
        counter_plots_completed = Counter('chia_completed_plots', 'Total completed plots', ['hostname', 'queue'])
        port = instrumentation_settings.get('prometheus_port', 9090)
        logging.info(f'Prometheus port: {port}')
        start_http_server(port)
    return gauge_plots_running, counter_plots_completed


def set_plots_running(total_running_plots, job_name, instrumentation_settings):
    gauge_plots_running, counter_plots_completed = _get_metrics(instrumentation_settings)
    if instrumentation_settings.get('prometheus_enabled', False):
        logging.info(f'Prometheus: Setting running plots {job_name}')
        hostname = socket.gethostname()
        gauge_plots_running.labels(hostname=hostname, queue=job_name).set(total_running_plots)
    else:
        logging.debug('Prometheus instrumentation not enabled')


def increment_plots_completed(increment, job_name, instrumentation_settings):
    gauge_plots_running, counter_plots_completed = _get_metrics(instrumentation_settings)
    if instrumentation_settings.get('prometheus_enabled'):
        logging.info(f'Prometheus: Incrementing plots {job_name}')
        hostname = socket.gethostname()
        counter_plots_completed.labels(hostname=hostname, queue=job_name).inc(increment)
    else:
        logging.debug('Prometheus instrumentation not enabled')
