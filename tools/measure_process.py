"""Sample RSS and interval CPU usage of an already running packaged app."""

import argparse
import json
import subprocess
import time


def time_seconds(value):
    """Parse ps TIME, including long-running day/hour formats."""
    days, _, clock = value.rpartition("-")
    total = 0.0
    for part in (clock or value).split(":"):
        total = total * 60 + float(part)
    return total + (int(days) * 86400 if days else 0)


def sample(pid):
    row = subprocess.check_output(["ps", "-o", "rss=,time=", "-p", str(pid)], text=True)
    rss, cpu = row.split()
    return int(rss) / 1024, time_seconds(cpu)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pid", type=int)
    parser.add_argument("--seconds", type=float, default=30)
    args = parser.parse_args()
    if args.seconds <= 0:
        parser.error("--seconds must be positive")
    started = time.monotonic()
    baseline, first_cpu = sample(args.pid)
    samples = [baseline]
    while time.monotonic() - started < args.seconds:
        time.sleep(min(1, args.seconds))
        rss, last_cpu = sample(args.pid)
        samples.append(rss)
    elapsed = time.monotonic() - started
    report = {
        "duration_seconds": round(elapsed, 1),
        "rss_start_mib": round(baseline, 2),
        "rss_end_mib": round(samples[-1], 2),
        "rss_peak_mib": round(max(samples), 2),
        "interval_cpu_percent": round(100 * (last_cpu - first_cpu) / elapsed, 3),
    }
    print(json.dumps(report, indent=2))
    assert max(samples) < 160, "Packaged RSS exceeds the 160 MiB regression budget"
    assert report["interval_cpu_percent"] < 1, "Unexpected sustained idle CPU activity"


if __name__ == "__main__":
    main()
