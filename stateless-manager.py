import time

from datetime import datetime, timedelta

from plotmanager.library.parse.configuration import get_config_info
from plotmanager.library.utilities.jobs import has_active_jobs_and_work, load_jobs, monitor_jobs_to_start
from plotmanager.library.utilities.log import check_log_progress
from plotmanager.library.utilities.processes import get_running_plots

chia_location, log_directory, config_jobs, log_check_seconds, max_concurrent, progress_settings = get_config_info()
jobs = load_jobs(config_jobs)

next_log_check = datetime.now()
next_job_work = {}
running_work = {}

jobs, running_work = get_running_plots(jobs, running_work)
for job in jobs:
    max_date = None
    for work in running_work.values():
        start = work.datetime_start
        if not max_date or start > max_date:
            max_date = start
    if not max_date:
        continue
    next_job_work[job.name] = max_date + timedelta(minutes=job.stagger_minutes)

while has_active_jobs_and_work(jobs):
    # CHECK LOGS FOR DELETED WORK
    check_log_progress(jobs=jobs, running_work=running_work, progress_settings=progress_settings)
    next_log_check = datetime.now() + timedelta(seconds=log_check_seconds)

    # DETERMINE IF JOB NEEDS TO START
    jobs, running_work, next_job_work, next_log_check = monitor_jobs_to_start(
        jobs=jobs,
        running_work=running_work,
        max_concurrent=max_concurrent,
        next_job_work=next_job_work,
        chia_location=chia_location,
        log_directory=log_directory,
        next_log_check=next_log_check,
    )

    time.sleep(log_check_seconds)
