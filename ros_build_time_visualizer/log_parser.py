import re

def parse_build_times(file_path):
    package_times = {}
    job_start_times = {}

    # Regular expressions to match JobStarted and JobEnded
    job_started_pattern = re.compile(r"\[(\d+\.\d+)\] \((.*?)\) JobStarted: {.*}")
    job_ended_pattern = re.compile(r"\[(\d+\.\d+)\] \((.*?)\) JobEnded: {.*}")

    with open(file_path, 'r') as file:
        for line in file:
            # Match JobStarted lines
            started_match = job_started_pattern.match(line)
            if started_match:
                time = float(started_match.group(1))
                package = started_match.group(2)
                job_start_times[package] = time

            # Match JobEnded lines
            ended_match = job_ended_pattern.match(line)
            if ended_match:
                time = float(ended_match.group(1))
                package = ended_match.group(2)

                if package in job_start_times:
                    # Calculate duration and store in dictionary
                    duration = time - job_start_times[package]
                    package_times[package] = duration

    return package_times
