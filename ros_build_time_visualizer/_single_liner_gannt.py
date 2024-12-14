import re
import plotly.graph_objects as go
import pandas as pd
import os
import argparse

from datetime import timedelta

# Function to parse the events.log file and extract build times
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
                    # Store start and end times
                    start_time = job_start_times[package]
                    end_time = time
                    package_times[package] = (start_time, end_time)

    return package_times

# Function to convert seconds to a more readable time format
def seconds_to_time(seconds):
    td = timedelta(seconds=seconds)
    return str(td)

# Function to plot the Gantt chart using Plotly
def plot_gantt_chart(build_times):
    # Prepare data for the Gantt chart
    df = pd.DataFrame([
        dict(Task=package, Start=start, Finish=end)
        for package, (start, end) in build_times.items()
    ])

    df['Duration'] = df['Finish'] - df['Start']

    # Sort tasks by duration for better readability
    # df.sort_values(by='Duration', ascending=False, inplace=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['Duration'],
        y=df['Task'],
        base=df['Start'],
        orientation='h',
        marker=dict(color='rgba(50, 171, 96, 0.6)', line=dict(color='rgba(50, 171, 96, 1.0)', width=1)),
        hovertemplate='<b>%{y}</b><br>Start: %{base:.2f} s<br>Duration: %{x:.2f} s<extra></extra>',
    ))

    # Adjust layout for readability and navigation
    fig.update_layout(
        title='Build Gantt Chart',
        xaxis_title='Time (seconds)',
        yaxis_title='Packages',
        height=max(600, 20 * len(df)),  # Dynamically adjust chart height based on number of packages
        yaxis=dict(
            autorange="reversed",  # Reverse Y-axis to match typical Gantt chart layouts
            tickmode='linear',     # Ensure all packages are displayed
            tickfont=dict(size=10),  # Adjust font size for better readability
        ),
        xaxis=dict(
            rangeslider=dict(visible=True),  # Add range slider for horizontal navigation
        ),
    )

    # Save the chart to an HTML file and show it
    fig.write_html("build_gantt_chart.html")
    fig.show()

# Function to parse command-line arguments
def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process a ROS workspace and generate a build Gantt chart. "
                    "Provide the path to the ROS workspace as an argument.",
        epilog="Example: python script_name.py /home/user/projects/ros_workspace"
    )
    parser.add_argument(
        'ros_workspace',
        type=str,
        help="The path to the ROS workspace."
    )
    return parser.parse_args()

def main():
    # Parse the command-line arguments
    args = parse_args()
    ros_workspace = args.ros_workspace

    # Path to the events.log file
    file_path = os.path.join(ros_workspace, "log/latest_build/events.log")

    if not os.path.exists(file_path):
        print(f"Log file not found at {file_path}")
        exit(1)

    # Parse build times from the log file
    build_times = parse_build_times(file_path)

    if not build_times:
        print("No build times found in the log file.")
        exit(1)

    # Plot Gantt chart
    plot_gantt_chart(build_times)

if __name__ == "__main__":
    main()
