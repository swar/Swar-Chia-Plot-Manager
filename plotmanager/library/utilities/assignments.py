import os

def assign_mount(actual_disk_path, job_path_alias):
    os.symlink(actual_disk_path, job_path_alias)
    return()