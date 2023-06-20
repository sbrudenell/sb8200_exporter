import setuptools

setuptools.setup(
    name="sb8200_exporter",
    version="0.0.2",
    author="Steven Brudenell",
    author_email="steven.brudenell@gmail.com",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests>=2.18.4",
        "beautifulsoup4>=4.6.0",
        "prometheus_client>=0.2.0",
        "html5lib>=1.0.1",
        "selenium"
    ],
    entry_points={
        "console_scripts": [
            "sb8200_exporter = sb8200_exporter:exporter_main",
        ],
    },
    # Set the default pip timeout to 100 seconds
    # This will apply to all pip commands run by setuptools
    # including the install_requires packages
    options={
        "install": {
            "default-timeout": 100
        }
    }
)