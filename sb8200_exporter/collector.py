import re
import bs4
import prometheus_client
import prometheus_client.core
from . import utils

class Collector(object):

    SCHEME = "https"
    PATH = "/cmconnectionstatus.html"

    _DOWNSTREAM_HEADER_DISCRETE = set(("frequency",))
    _DOWNSTREAM_HEADER_COUNTER = set(("corrected", "uncorrectables"))
    _UPSTREAM_HEADER_DISCRETE = set(("frequency", "symbol_rate"))
    _UPSTREAM_HEADER_COUNTER = set(())

    def __init__(self, address, user, password, selenium_remote, selenium_driver_url):
        self.address = address
        self.username = user
        self.password = password
        self.selenium_remote = selenium_remote
        self.selenium_driver_url = selenium_driver_url
        self._prefix = "sb8200_"

    def headerify(self, text):
        text = text.strip().lower()
        text = re.sub(r"[^a-z0-9]", "_", text)
        return text

    def parse_table(self, table):
        result = []
        headers = []
        for tr in table.find_all("tr"):
            cells = tr.find_all("td")
            if not cells:
                continue
            if not headers:
                for cell in cells:
                    headers.append(self.headerify(cell.text))
            else:
                row = {}
                for header, cell in zip(headers, cells):
                    row[header] = cell.text.strip()
                result.append(row)
        return result

    def make_metric(self, _is_counter, _name, _documentation, _value,
                    **_labels):
        if _is_counter:
            cls = prometheus_client.core.CounterMetricFamily
        else:
            cls = prometheus_client.core.GaugeMetricFamily
        label_names = list(_labels.keys())
        metric = cls(
            _name, _documentation or "No Documentation", labels=label_names)
        metric.add_metric([str(_labels[k]) for k in label_names], _value)
        return metric

    def make_table_metrics(self, rows, prefix, id, discrete, counter):
        metrics = []
        for row in rows:
            state = {}
            labels = {k: row[k] for k in id}
            for k, v in row.items():
                if k in id:
                    continue
                if re.match(r"^-?[0-9\.]+( .*)?", v) and k not in discrete:
                    v = float(v.split(" ")[0])
                    metrics.append(self.make_metric(
                        k in counter, prefix + k, None, v, **labels))
                else:
                    state[k] = v
            if state:
                state.update(labels)
                metrics.append(self.make_metric(
                    False, prefix + "state", None, 1, **state))
        return metrics

    def collect(self):
        metrics = []

        h = bs4.BeautifulSoup(utils.collect_modem_metrics_html(self.address, self.username, self.password, self.selenium_remote, self.selenium_driver_url).prettify(), "html5lib")
        global_state = {}

        for table in h.find_all("table"):
            if not table.th:
                continue
            rows = self.parse_table(table)
            title = table.th.text.strip()
            if title == "Startup Procedure":
                for row in rows:
                    row_prefix = self.headerify(row["procedure"]) + "_"
                    for k, v in row.items():
                        if k == "procedure":
                            continue
                        global_state[row_prefix + k] = v
            elif title == "Downstream Bonded Channels":
                metrics.extend(self.make_table_metrics(
                    rows, self._prefix + "downstream_",
                    set(("channel_id", "frequency")),
                    self._DOWNSTREAM_HEADER_DISCRETE,
                    self._DOWNSTREAM_HEADER_COUNTER))
            elif title == "Upstream Bonded Channels":
                metrics.extend(self.make_table_metrics(
                    rows, self._prefix + "upstream_",
                    set(("channel_id", "frequency")),
                    self._UPSTREAM_HEADER_DISCRETE,
                    self._UPSTREAM_HEADER_COUNTER))
            else:
                assert False, title
        if global_state:
            metrics.append(self.make_metric(
                False, self._prefix + "state", None, 1, **global_state))
        return metrics
