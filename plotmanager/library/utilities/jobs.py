import logging
import psutil

from copy import deepcopy
from datetime import datetime, timedelta

from plotmanager.library.commands import plots
from plotmanager.library.utilities.processes import is_windows, start_process
from plotmanager.library.utilities.objects import Job, Work
from plotmanager.library.utilities.log import get_log_file_name


def has_active_jobs_and_work(jobs):
    for job in jobs:
        if job.total_completed < job.max_plots:
            return True
    return False


def get_target_directories(job):
    job_offset = job.total_completed + job.total_running

    destination_directory = job.destination_directory
    temporary2_directory = job.temporary2_directory

    if isinstance(job.destination_directory, list):
        destination_directory = job.destination_directory[job_offset % len(job.destination_directory)]
    if isinstance(job.temporary2_directory, list):
        temporary2_directory = job.temporary2_directory[job_offset % len(job.temporary2_directory)]

    return destination_directory, temporary2_directory


def load_jobs(config_jobs):
    jobs = []
    for info in config_jobs:
        job = deepcopy(Job())
        job.total_running = 0

        job.name = info['name']
        job.max_plots = info['max_plots']

        job.farmer_public_key = info.get('farmer_public_key', None)
        job.pool_public_key = info.get('pool_public_key', None)
        job.max_concurrent = info['max_concurrent']
        job.max_concurrent_with_start_early = info['max_concurrent_with_start_early']
        job.max_for_phase_1 = info['max_for_phase_1']
        job.stagger_minutes = info.get('stagger_minutes', None)
        job.max_for_phase_1 = info.get('max_for_phase_1', None)
        job.concurrency_start_early_phase = info.get('concurrency_start_early_phase', None)
        job.concurrency_start_early_phase_delay = info.get('concurrency_start_early_phase_delay', None)
        job.temporary2_destination_sync = info.get('temporary2_destination_sync', False)

        job.temporary_directory = info['temporary_directory']
        job.destination_directory = info['destination_directory']

        temporary2_directory = info.get('temporary2_directory', None)
        if not temporary2_directory:
            temporary2_directory = None
        job.temporary2_directory = temporary2_directory

        job.size = info['size']
        job.bitfield = info['bitfield']
        job.threads = info['threads']
        job.buckets = info['buckets']
        job.memory_buffer = info['memory_buffer']
        jobs.append(job)

    return jobs


def monitor_jobs_to_start(jobs, running_work, max_concurrent, next_job_work, chia_location, log_directory, next_log_check):
    for i, job in enumerate(jobs):
        logging.info(f'Checking to queue work for job: {job.name}')
        if len(running_work.values()) >= max_concurrent:
            logging.info(f'Global concurrent limit met, skipping. Running plots: {len(running_work.values())}, '
                         f'Max global concurrent limit: {max_concurrent}')
            continue
        phase_1_count = 0
        for pid in job.running_work:
            if running_work[pid].current_phase > 1:
                continue
            phase_1_count += 1
        logging.info(f'Total jobs in phase 1: {phase_1_count}')
        if job.max_for_phase_1 and phase_1_count >= job.max_for_phase_1:
            logging.info(f'Max for phase 1 met, skipping. Max: {job.max_for_phase_1}')
            continue
        if job.total_completed >= job.max_plots:
            logging.info(f'Job\'s total completed greater than or equal to max plots, skipping. Total Completed: '
                         f'{job.total_completed}, Max Plots: {job.max_plots}')
            continue
        if job.name in next_job_work and next_job_work[job.name] > datetime.now():
            logging.info(f'Waiting for job stagger, skipping. Next allowable time: {next_job_work[job.name]}')
            continue
        discount_running = 0
        if job.concurrency_start_early_phase is not None:
            for pid in job.running_work:
                work = running_work[pid]
                try:
                    start_early_date = work.phase_dates[job.concurrency_start_early_phase - 1]
                except (KeyError, AttributeError):
                    start_early_date = work.datetime_start

                if work.current_phase < job.concurrency_start_early_phase:
                    continue
                if datetime.now() <= (start_early_date + timedelta(minutes=job.concurrency_start_early_phase_delay)):
                    continue
                discount_running += 1
        if (job.total_running - discount_running) >= job.max_concurrent:
            logging.info(f'Job\'s max concurrent limit has been met, skipping. Max concurrent minus start_early: '
                         f'{job.total_running - discount_running}, Max concurrent: {job.max_concurrent}')
            continue
        if job.total_running >= job.max_concurrent_with_start_early:
            logging.info(f'Job\'s max concurrnet limit with start early has been met, skipping. Max: {job.max_concurrent_with_start_early}')
            continue
        if job.stagger_minutes:
            next_job_work[job.name] = datetime.now() + timedelta(minutes=job.stagger_minutes)
            logging.info(f'Calculating new job stagger time. Next stagger kickoff: {next_job_work[job.name]}')
        job, work = start_work(job=job, chia_location=chia_location, log_directory=log_directory)
        jobs[i] = deepcopy(job)
        next_log_check = datetime.now()
        running_work[work.pid] = work

    return jobs, running_work, next_job_work, next_log_check


def start_work(job, chia_location, log_directory):
    logging.info(f'Starting new plot for job: {job.name}')
    nice_val = 10
    if is_windows():
        nice_val = psutil.NORMAL_PRIORITY_CLASS

    now = datetime.now()
    log_file_path = get_log_file_name(log_directory, job, now)
    logging.info(f'Job log file path: {log_file_path}')
    destination_directory, temporary2_directory = get_target_directories(job)
    logging.info(f'Job destination directory: {destination_directory}')

    work = deepcopy(Work())
    work.job = job
    work.log_file = log_file_path
    work.datetime_start = now
    work.work_id = job.current_work_id

    job.current_work_id += 1

    if job.temporary2_destination_sync:
        logging.info(f'Job temporary2 and destination sync')
        temporary2_directory = destination_directory
    logging.info(f'Job temporary2 directory: {temporary2_directory}')

    plot_command = plots.create(
        chia_location=chia_location,
        farmer_public_key=job.farmer_public_key,
        pool_public_key=job.pool_public_key,
        size=job.size,
        memory_buffer=job.memory_buffer,
        temporary_directory=job.temporary_directory,
        temporary2_directory=temporary2_directory,
        destination_directory=destination_directory,
        threads=job.threads,
        buckets=job.buckets,
        bitfield=job.bitfield,
    )
    logging.info(f'Starting with plot command: {plot_command}')

    log_file = open(log_file_path, 'a')
    logging.info(f'Starting process')
    process = start_process(args=plot_command, log_file=log_file)
    pid = process.pid
    logging.info(f'Started process: {pid}')

    logging.info(f'Setting priority level: {nice_val}')
    psutil.Process(pid).nice(nice_val)
    logging.info(f'Set priority level')

    work.pid = pid
    job.total_running += 1
    job.running_work = job.running_work + [pid]
    logging.info(f'Job total running: {job.total_running}')
    logging.info(f'Job running: {job.running_work}')

    return job, work
