import argparse
import os
import http.server
import prometheus_client
import sb8200_exporter


def main():
    parser = argparse.ArgumentParser("Eagle Parser")

    parser.add_argument("--port", type=int, default=9195)
    parser.add_argument("--bind_address", default="0.0.0.0")
    parser.add_argument("--address", default=os.getenv('MODEM_URL', 'https://192.168.100.1/'))
    parser.add_argument("--username", default=os.getenv('MODEM_USER', 'admin'))
    parser.add_argument("--password", default=os.getenv('MODEM_PASS'))
    parser.add_argument("--selenium_remote", default=os.getenv('SELENIUM_REMOTE', 'true'))
    parser.add_argument("--selenium_driver_url", default=os.getenv('SELENIUM_DRIVER_URL', 'http://localhost:4444'))


    args = parser.parse_args()

    collector = sb8200_exporter.Collector(args.address, args.username, args.password, args.selenium_remote, args.selenium_driver_url)

    prometheus_client.REGISTRY.register(collector)

    handler = prometheus_client.MetricsHandler.factory(
            prometheus_client.REGISTRY)
    server = http.server.HTTPServer(
            (args.bind_address, args.port), handler)
    server.serve_forever()
