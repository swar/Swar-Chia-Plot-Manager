import pathlib
import os
import yaml


from library.utilities.exceptions import InvalidYAMLConfigException


def _get_config():
    directory = pathlib.Path().resolve()
    file_name = 'config.yaml'
    file_path = os.path.join(directory, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Unable to find the config.yaml file. Expected location: {file_path}")
    f = open(file_path, 'r')
    config = yaml.load(stream=f, Loader=yaml.Loader)
    f.close()
    return config


def _get_chia_location(config):
    return config.get('chia_location', 'chia')


def _get_log_location(config):
    if 'log_location' not in config:
        raise InvalidYAMLConfigException('Failed to find the log_location parameter in the YAML.')
    log_location = config['log_location']
    failed_checks = []
    checks = ['folder_path', 'check_seconds']
    for check in checks:
        if check in log_location:
            continue
        failed_checks.append(check)

    if failed_checks:
        raise InvalidYAMLConfigException(f'Failed to find the following parameters in log_location: '
                                         f'{", ".join(failed_checks)}')

    return log_location['folder_path'], log_location['check_seconds']


def _get_jobs(config):
    if 'jobs' not in config:
        raise InvalidYAMLConfigException('Failed to find the jobs parameter in the YAML.')
    return config['jobs']


def get_config_info():
    config = _get_config()
    chia_location = _get_chia_location(config=config)
    log_directory, log_check_seconds = _get_log_location(config=config)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    jobs = _get_jobs(config=config)
    return chia_location, log_directory, jobs, log_check_seconds
