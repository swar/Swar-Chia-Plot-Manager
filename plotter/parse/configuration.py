import os
import yaml

from string import ascii_uppercase

from plotter.utilities.exceptions import InvalidYAMLConfigException

CONFIG_LOCATION = 'S:/Cloud Storage/Github/plotter/config.yaml'


def _get_config():
    if not os.path.exists(CONFIG_LOCATION):
        raise FileNotFoundError("Was unable to find the config.yaml file.")
    f = open(CONFIG_LOCATION, 'r')
    config = yaml.load(stream=f, Loader=yaml.Loader)
    f.close()
    return config


def _get_chia_location(config):
    return config.get('chia_location', 'chia')


def _get_log_location(config):
    log_location = config['log_location']
    return log_location['folder_path'], log_location['check_seconds']


def _get_jobs(config):
    return config['jobs']


def get_config_info():
    config = _get_config()
    chia_location = _get_chia_location(config=config)
    log_directory, log_check_seconds = _get_log_location(config=config)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    jobs = _get_jobs(config=config)
    return chia_location, log_directory, jobs, log_check_seconds
