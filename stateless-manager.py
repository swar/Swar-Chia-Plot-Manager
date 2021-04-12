import time

from datetime import datetime, timedelta

from plotmanager.library.parse.configuration import get_config_info
from plotmanager.library.utilities.jobs import has_active_jobs_and_work, load_jobs, monitor_jobs_to_start
from plotmanager.library.utilities.log import check_log_progress
from plotmanager.library.utilities.processes import get_running_plots

print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Getting config.yaml info...')
chia_location, log_directory, config_jobs, log_check_seconds, max_concurrent = get_config_info()

print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Loading jobs...')
jobs = load_jobs(config_jobs)

next_log_check = datetime.now()
next_job_work = {}
running_work = {}

print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Getting running plots...')
jobs, running_work = get_running_plots(jobs, running_work)

while has_active_jobs_and_work(jobs):
    # CHECK LOGS FOR DELETED WORK
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Updating log process...')
    check_log_progress(jobs=jobs, running_work=running_work)
    next_log_check = datetime.now() + timedelta(seconds=log_check_seconds)

    # DETERMINE IF JOB NEEDS TO START
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Checking if work needs to start...')
    jobs, running_work, next_job_work, next_log_check = monitor_jobs_to_start(
        jobs=jobs,
        running_work=running_work,
        max_concurrent=max_concurrent,
        next_job_work=next_job_work,
        chia_location=chia_location,
        log_directory=log_directory,
        next_log_check=next_log_check,
    )

    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Sleeping for {log_check_seconds} seconds...')
    time.sleep(log_check_seconds)
