import pathlib
import os
import yaml


from plotmanager.library.utilities.exceptions import InvalidYAMLConfigException


def _get_config():                              # Can we find the actual config - checker
    directory = pathlib.Path().resolve()
    file_name = 'config.yaml'
    file_path = os.path.join(directory, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Unable to find the config.yaml file. Expected location: {file_path}")
    f = open(file_path, 'r')
    config = yaml.load(stream=f, Loader=yaml.Loader)
    f.close()
    return config


def _get_chia_location(config):                  # must know where it is
    return config.get('chia_location', 'chia')


def _get_progress_settings(config):              # generics given; can be replaced by machine specifics
    progress_setting = config['progress']
    expected_parameters = ['phase1_line_end', 'phase2_line_end', 'phase3_line_end', 'phase4_line_end', 'phase1_weight',
                           'phase2_weight', 'phase3_weight', 'phase4_weight', ]
    _check_parameters(parameter=progress_setting, expected_parameters=expected_parameters, parameter_type='progress')
    return progress_setting


def _get_manager_settings(config):              # must have log manager settings 
    if 'manager' not in config:
        raise InvalidYAMLConfigException('Failed to find the log parameter in the YAML.')
    manager = config['manager']
    expected_parameters = ['check_interval', 'log_level']
    _check_parameters(parameter=manager, expected_parameters=expected_parameters, parameter_type='manager')
    return manager['check_interval'], manager['log_level']


def _get_log_settings(config):               # must have actual place to read /parse logs
    if 'log' not in config:
        raise InvalidYAMLConfigException('Failed to find the log parameter in the YAML.')
    log = config['log']
    expected_parameters = ['folder_path']
    _check_parameters(parameter=log, expected_parameters=expected_parameters, parameter_type='log')
    return log['folder_path']


def _get_jobs(config):                      # jobs are a horrible name collision; these are drone defaults
    if 'jobs' not in config:
        raise InvalidYAMLConfigException('Failed to find the jobs parameter in the YAML.')
    return config['jobs']


def _get_chiax_location(config):                    # ADDED to accomodate our work folder
    if 'chiax' not in config:
        raise InvalidYAMLConfigException('Failed to find the log parameter in the YAML.')
    chiax = config['chiax']
    expected_parameters = ['folder_path']
    _check_parameters(parameter=chiax, expected_parameters=expected_parameters, parameter_type='chiax')
    return chiax['folder_path']


def _get_global_config(config):             # odd that this follows, but OK.  
    if 'global' not in config:
        raise InvalidYAMLConfigException('Failed to find global parameter in the YAML.')
    global_config = config['global']
    expected_parameters = ['max_concurrent', 'max_for_phase_1', 'minimum_minutes_between_jobs']
    _check_parameters(parameter=global_config, expected_parameters=expected_parameters, parameter_type='global')
    drive_string = global_config['drive_mounts']
    drive_mounts = eval(drive_string)
    max_concurrent = global_config['max_concurrent']
    max_for_phase_1 = global_config['max_for_phase_1']
    minimum_minutes_between_jobs = global_config['minimum_minutes_between_jobs']
    if not isinstance(max_concurrent, int):
        raise Exception('global -> max_concurrent should be a integer value.')
    if not isinstance(max_for_phase_1, int):
        raise Exception('global -> max_for_phase_1 should be a integer value.')
    if not isinstance(minimum_minutes_between_jobs, int):
        raise Exception('global -> max_concurrent should be a integer value.')
    if not isinstance(drive_mounts, Dict):
        raise Exception('global -> need tuple of actual drive mounts')
    return max_concurrent, max_for_phase_1, minimum_minutes_between_jobs, drive_mounts


def _get_notifications_settings(config):
    notifications = config.get('notifications', None)
    if not notifications:
        notifications = {}

    if 'notify_discord' in notifications and notifications['notify_discord']:
        _check_parameters(parameter=notifications, expected_parameters=['discord_webhook_url'],
                          parameter_type='notification')

    if 'notify_ifttt' in notifications and notifications['notify_ifttt']:
        _check_parameters(parameter=notifications, expected_parameters=['ifttt_webhook_url'],
                          parameter_type='notification')

    if 'notify_sound' in notifications and notifications['notify_sound']:
        _check_parameters(parameter=notifications, expected_parameters=['song'],
                          parameter_type='notification')

    if 'notify_pushover' in notifications and notifications['notify_pushover']:
        _check_parameters(parameter=notifications, expected_parameters=['pushover_user_key', 'pushover_api_key'],
                          parameter_type='notification')

    if 'notify_telegram' in notifications and notifications['notify_telegram']:
        _check_parameters(parameter=notifications, expected_parameters=['telegram_token'],
                          parameter_type='notification')

    if 'notify_twilio' in notifications and notifications['notify_twilio']:
        _check_parameters(parameter=notifications, expected_parameters=['discord_webhook_url'],
                          parameter_type='notification')

    return notifications


def _get_view_settings(config):
    if 'view' not in config:
        raise InvalidYAMLConfigException('Failed to find view parameter in the YAML.')
    view = config['view']
    expected_parameters = ['datetime_format', 'include_seconds_for_phase', 'include_drive_info', 'include_cpu', 'include_ram',
                           'include_plot_stats', 'check_interval']
    _check_parameters(parameter=view, expected_parameters=expected_parameters, parameter_type='view')
    return view


def _get_instrumentation_settings(config):
    if 'instrumentation' not in config:
        raise InvalidYAMLConfigException('Failed to find instrumentation parameter in the YAML.')
    instrumentation = config.get('instrumentation', {})
    return instrumentation


def _check_parameters(parameter, expected_parameters, parameter_type):
    failed_checks = []
    checks = expected_parameters
    for check in checks:
        if check in parameter:
            continue
        failed_checks.append(check)

    if failed_checks:
        raise InvalidYAMLConfigException(f'Failed to find the following {parameter_type} parameters: '
                                         f'{", ".join(failed_checks)}')


def get_config_info():
    config = _get_config()
    chia_location = _get_chia_location(config=config)
    manager_check_interval, log_level = _get_manager_settings(config=config)
    log_directory = _get_log_settings(config=config)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    chiax_directory = _get_chiax_location(config=config)    #ADDED to mesh with above; need to add bid stuff
    if not os.path.exists(chiax.folder_path):
        os.makedirs(chiax_path)
    jobs = _get_jobs(config=config)
    drive_mounts = _get_global_config(config=config)
    max_concurrent, max_for_phase_1, minimum_minutes_between_jobs = _get_global_config(config=config)
    progress_settings = _get_progress_settings(config=config)
    notification_settings = _get_notifications_settings(config=config)
    view_settings = _get_view_settings(config=config)
    instrumentation_settings = _get_instrumentation_settings(config=config)

    return chia_location, log_directory, jobs, manager_check_interval, max_concurrent, max_for_phase_1, \
        minimum_minutes_between_jobs, progress_settings, notification_settings, log_level, view_settings, \
        instrumentation_settings, drive_mounts
