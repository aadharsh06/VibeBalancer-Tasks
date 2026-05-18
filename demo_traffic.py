import argparse
import itertools
import random
import threading
import time

import requests


def send_load_balancer_request(url, algorithm, delay, label, timeout):
    try:
        response = requests.get(
            url,
            params={"type": algorithm, "delay": delay},
            timeout=timeout,
        )
        print(
            f"lb {algorithm:17s} {label:12s} "
            f"delay={delay} status={response.status_code}"
        )
    except requests.RequestException as exc:
        print(f"lb {algorithm:17s} {label:12s} delay={delay} error={exc}")


def ping_backend(session, base_url):
    for path in ("/", "/info"):
        try:
            response = session.get(f"{base_url}{path}", timeout=3)
            print(f"backend {base_url}{path:5s} status={response.status_code}")
        except requests.RequestException as exc:
            print(f"backend {base_url}{path:5s} error={exc}")


def main():
    parser = argparse.ArgumentParser(description="Generate demo traffic for VibeBalancer.")
    parser.add_argument("--url", default="http://127.0.0.1:8000/work")
    parser.add_argument(
        "--backend-url",
        action="append",
        default=["http://127.0.0.1:8001", "http://127.0.0.1:8003"],
        help="Backend server base URL to ping. Can be used multiple times.",
    )
    parser.add_argument("--interval", type=float, default=0.4)
    parser.add_argument("--max-delay", type=int, default=3)
    parser.add_argument("--ping-backends-every", type=int, default=10)
    parser.add_argument(
        "--error-every",
        type=int,
        default=12,
        help="Send one background timeout request every N load-balancer requests. Use 0 to disable.",
    )
    parser.add_argument(
        "--error-delay",
        type=int,
        default=12,
        help="Delay used for timeout requests. Task 6/7 load balancer times out after 10 seconds.",
    )
    args = parser.parse_args()

    algorithms = itertools.cycle(["round_robin", "least_connections"])
    request_number = 0

    with requests.Session() as session:
        while True:
            request_number += 1
            algorithm = next(algorithms)
            is_error_demo = args.error_every and request_number % args.error_every == 0
            delay = random.randint(0, args.max_delay)

            if is_error_demo:
                threading.Thread(
                    target=send_load_balancer_request,
                    args=(
                        args.url,
                        algorithm,
                        args.error_delay,
                        "timeout-demo",
                        (args.error_delay * 2) + 5,
                    ),
                    daemon=True,
                ).start()

            try:
                response = session.get(
                    args.url,
                    params={"type": algorithm, "delay": delay},
                    timeout=args.max_delay + 5,
                )
                print(
                    f"lb {algorithm:17s} normal       "
                    f"delay={delay} status={response.status_code}"
                )
            except requests.RequestException as exc:
                print(f"lb {algorithm:17s} normal       delay={delay} error={exc}")

            if args.ping_backends_every and request_number % args.ping_backends_every == 0:
                for backend_url in args.backend_url:
                    ping_backend(session, backend_url)

            time.sleep(args.interval)


if __name__ == "__main__":
    main()
