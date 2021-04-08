import os
import time

from datetime import datetime, timedelta
from termcolor import cprint

from library.parse import get_config_info
from library.utilities import has_active_jobs_and_work, load_jobs, monitor_jobs_to_start
from library.utilities.log import check_stop_plotting_override, check_log_progress
from library.utilities import print_table


chia_location, log_directory, config_jobs, log_check_seconds = get_config_info()
jobs = load_jobs(config_jobs)

next_log_check = datetime.now()
next_job_work = {}
running_work = {}

override_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'STATELESS-OVERRIDE.json')
stop_plotting = False
while has_active_jobs_and_work(jobs):
    # CHECK TO SEE IF PLOTTING SHOULD BE OVERRIDDEN
    stop_plotting = check_stop_plotting_override(stop_plotting=stop_plotting, override_file_path=override_file_path)

    # CHECK LOGS FOR DELETED WORK
    check_log_progress(jobs=jobs, running_work=running_work)
    next_log_check = datetime.now() + timedelta(seconds=log_check_seconds)

    # DETERMINE IF JOB NEEDS TO START
    jobs, running_work, next_job_work, next_log_check = monitor_jobs_to_start(
        jobs=jobs,
        running_work=running_work,
        next_job_work=next_job_work,
        chia_location=chia_location,
        log_directory=log_directory,
        next_log_check=next_log_check,
        stop_plotting=stop_plotting,
    )

    if not running_work and stop_plotting:
        cprint(f"Plotting has stopped.", 'red')
        exit()

    # PRINT TABLE
    print_table(jobs, running_work, next_log_check, stop_plotting)

    time.sleep(log_check_seconds)
