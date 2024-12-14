# ROS Build Time Visualizer

A tool to visualize build times for packages in a ROS workspace.

## Features
- Parses ROS `events.log` files to extract build times.
- Constructs a hierarchical directory structure for visualization.
- Generates a treemap of package build times using Plotly.

## Installation

### From Source
1. Clone the repository:
    ```bash
    git clone https://github.com/xmfcx/ros-build-time-visualizer.git
    cd ros-build-time-visualizer
    ```
2. Install the package using `pip`:
    ```bash
    pip install .
    ```

### Using `pip` from GitHub
Alternatively, you can install directly from the GitHub repository:
```bash
pip install git+https://github.com/xmfcx/ros-build-time-visualizer.git
```

## Usage
After installation, you can use the tool via the command line:

```bash
ros-build-time-visualizer /path/to/ros/workspace
```

## Output
The tool generates an interactive treemap (`build_time_treemap.html`) in the current directory, which can be opened in any web browser.

## Development
To contribute to the project:
1. Fork the repository and clone your fork.
2. Install the package in editable mode along with development dependencies:
    ```bash
    pip install -e .[dev]
    ```
3. Run tests and format the code before submitting a pull request.

## License
This project is licensed under the Apache 2.0 License. See the `LICENSE` file for details.
