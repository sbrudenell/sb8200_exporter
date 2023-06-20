# sb8200_exporter
A prometheus exporter for the Arris SB8200

Need Setup for automated build - Now working with the latest Arris Login page

**UNMAINTAINED**: I no longer have an SB8200 due to moving out of the service area where I could use one. Please follow a fork, or make your own!

## Requirements

* Selenium WebDriver
* Python 3

The "major" update to this exporter is the requirement of an additional selenium webdriver container or local runtime to properly scrape the metrics

## Usage

Fill out the required cli arguments or environment variables. The exporter will scrape the modem and expose the metrics on the port specified, utilzing the username and password to login via a session proxied by the Chrome webdriver.

## Tests

Rewritten using selenium to properly login via updated JS method compared to previous. Working on integrating with Prometheus exporter. These are helpful for troubleshooting
