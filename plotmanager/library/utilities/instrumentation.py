import socket
import logging

PROCESSED = False
GAUGE_PLOTS_RUNNING = None
COUNTER_PLOTS_COMPLETED = None


def _get_metrics(instrumentation_settings):
    global PROCESSED
    if instrumentation_settings.get('prometheus_enabled', False) and not PROCESSED:
        from prometheus_client import Counter, Gauge, start_http_server
        global GAUGE_PLOTS_RUNNING
        global COUNTER_PLOTS_COMPLETED
        GAUGE_PLOTS_RUNNING = Gauge('chia_running_plots', 'Number of running plots', ['hostname', 'queue'])
        COUNTER_PLOTS_COMPLETED = Counter('chia_completed_plots', 'Total completed plots', ['hostname', 'queue'])
        port = instrumentation_settings.get('prometheus_port', 9090)
        logging.info(f'Prometheus port: {port}')
        start_http_server(port)
        PROCESSED = True


def set_plots_running(total_running_plots, job_name, instrumentation_settings):
    _get_metrics(instrumentation_settings=instrumentation_settings)
    if instrumentation_settings.get('prometheus_enabled', False) and GAUGE_PLOTS_RUNNING:
        logging.info(f'Prometheus: Setting running plots {job_name}')
        hostname = socket.gethostname()
        GAUGE_PLOTS_RUNNING.labels(hostname=hostname, queue=job_name).set(total_running_plots)
    else:
        logging.debug('Prometheus instrumentation not enabled')


def increment_plots_completed(increment, job_name, instrumentation_settings):
    _get_metrics(instrumentation_settings=instrumentation_settings)
    if instrumentation_settings.get('prometheus_enabled') and COUNTER_PLOTS_COMPLETED:
        logging.info(f'Prometheus: Incrementing plots {job_name}')
        hostname = socket.gethostname()
        COUNTER_PLOTS_COMPLETED.labels(hostname=hostname, queue=job_name).inc(increment)
    else:
        logging.debug('Prometheus instrumentation not enabled')
