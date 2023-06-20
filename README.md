# sb8200_exporter
A prometheus exporter for the Arris SB8200

[![Docker Image CI](https://github.com/gallis-local/sb8200_exporter/actions/workflows/main.yml/badge.svg)](https://github.com/gallis-local/sb8200_exporter/actions/workflows/main.yml)

Need to update to work with new Arris Login page, need to troubleshoot. Setup for automated build

**UNMAINTAINED**: I no longer have an SB8200 due to moving out of the service area where I could use one. Please follow a fork, or make your own!

## Requirements

* Selenium WebDriver
* Python 3

The major update to this exporter is the requirement of an additional selenium webdriver container to properly scrape the metrics

## Tests

Rewritten using selenium to properly login via updated JS method compared to previous. Working on integrating with Prometheus exporter. These are helpful for troubleshooting
