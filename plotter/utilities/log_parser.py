import os
import re
import dateparser

from plotter.parse.configuration import get_config_info

chia_location, log_directory, config_jobs, log_check_seconds = get_config_info()

total_phases = {1: 0, 2: 0, 3: 0, 4: 0}

for file_name in os.listdir(log_directory):
    file_path = os.path.join(log_directory, file_name)
    f = open(file_path, 'r')
    contents = f.read()
    f.close()
    # print(file_path)

    rows = []

    total_time_match = re.search(rf'total time = ([\d\.]+) seconds\. CPU \([\d\.]+%\) [A-Za-z]+\s([^\n]+)\n', contents, flags=re.I)
    if not total_time_match:
        continue
    seconds, date_raw = total_time_match.groups()
    parsed_date = dateparser.parse(date_raw)

    rows.append(file_path)
    rows.append(str(parsed_date))
    # print(f"{file_path}\t{parsed_date}")
    # continue

    phase_times = {}
    for phase in range(1, 5):
        match = re.search(rf'time for phase {phase} = ([\d\.]+) seconds\. CPU \([\d\.]+%\) [A-Za-z]+\s([^\n]+)\n', contents, flags=re.I)
        seconds, date_raw = match.groups()
        seconds = float(seconds)
        phase_times[phase] = seconds
        total_phases[phase] += seconds
        rows.append(str(seconds))

    print("\t".join(rows))

    # total_seconds = sum(phase_times.values())
    # for phase, seconds in phase_times.items():
    #     print(phase, f"{round(seconds / total_seconds * 100, 2)}%")


print()
total_seconds = sum(total_phases.values())
for phase, seconds in total_phases.items():
    print(phase, f"{round(seconds / total_seconds * 100, 2)}%")