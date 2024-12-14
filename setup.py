from setuptools import setup, find_packages

setup(
    name="ros-build-time-visualizer",
    version="1.0.0",
    description="A tool to visualize build times for packages in a ROS workspace.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="M. Fatih Cırıt",
    author_email="mfc@autoware.org",
    url="https://github.com/xmfcx/ros-build-time-visualizer",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas",
        "plotly",
    ],
    entry_points={
        "console_scripts": [
            "ros-build-time-visualizer=ros_build_time_visualizer.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
