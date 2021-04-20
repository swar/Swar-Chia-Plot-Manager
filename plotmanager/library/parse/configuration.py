import pathlib
import os
import yaml


from plotmanager.library.utilities.exceptions import InvalidYAMLConfigException


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


def _get_progress_settings(config):
    progress_setting = config['progress']
    check_keys = ['phase1_end', 'phase2_end', 'phase3_end', 'phase4_end', 'phase1_weight', 'phase2_weight',
                  'phase3_weight', 'phase4_weight', ]
    missing_keys = []
    for key in check_keys:
        if key in progress_setting:
            continue
        missing_keys.append(key)

    if missing_keys:
        raise InvalidYAMLConfigException(f'Missing parameters inside progress: {", ".join(missing_keys)}')
    return progress_setting


def _get_log_settings(config):
    if 'log' not in config:
        raise InvalidYAMLConfigException('Failed to find the log parameter in the YAML.')
    log = config['log']
    failed_checks = []
    checks = ['folder_path', 'check_seconds']
    for check in checks:
        if check in log:
            continue
        failed_checks.append(check)

    if failed_checks:
        raise InvalidYAMLConfigException(f'Failed to find the following parameters in log: '
                                         f'{", ".join(failed_checks)}')

    return log['folder_path'], log['check_seconds']


def _get_jobs(config):
    if 'jobs' not in config:
        raise InvalidYAMLConfigException('Failed to find the jobs parameter in the YAML.')
    return config['jobs']


def _get_global_max_concurrent_config(config):
    if 'global' not in config:
        raise InvalidYAMLConfigException('Failed to find global parameter in the YAML.')
    if 'max_concurrent' not in config['global']:
        raise InvalidYAMLConfigException('Failed to find max_concurrent in the global parameter in the YAML.')
    max_concurrent = config['global']['max_concurrent']
    if not isinstance(max_concurrent, int):
        raise Exception('global -> max_concurrent should be a integer value.')
    return max_concurrent


def _check_parameters(parameter, expected_parameters):
    failed_checks = []
    checks = expected_parameters
    for check in checks:
        if check in parameter:
            continue
        failed_checks.append(check)

    if failed_checks:
        raise InvalidYAMLConfigException(f'Failed to find the following parameters: {", ".join(failed_checks)}')


def get_notifications_settings():
    config = _get_config()
    if 'notifications' not in config:
        raise InvalidYAMLConfigException('Failed to find notifications parameter in the YAML.')
    notifications = config['notifications']
    _check_parameters(notifications, ['notify_discord', 'discord_webhook_url', 'notify_sound', 'song',
                                      'notify_pushover', 'pushover_user_key', 'pushover_api_key'])
    return notifications


def get_config_info():
    config = _get_config()
    chia_location = _get_chia_location(config=config)
    log_directory, log_check_seconds = _get_log_settings(config=config)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    jobs = _get_jobs(config=config)
    max_concurrent = _get_global_max_concurrent_config(config=config)
    progress_settings = _get_progress_settings(config=config)
    return chia_location, log_directory, jobs, log_check_seconds, max_concurrent, progress_settings
