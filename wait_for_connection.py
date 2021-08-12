#!/usr/bin/python3

# Copyright 2021 Michael de Gans

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Waits `--timeout` seconds for `--urls` before returning the number of failed
urls in the returncode. -1 is returned if the failed urls are greater than 126.
-2 is returned on invalid url. -3 is returned on any unexpected error.
"""

import logging
import sys
import concurrent.futures
import urllib.request
import time

from urllib.error import URLError, HTTPError

from typing import (
    Dict,
    List,
)

logger = logging.getLogger(__name__)

## defaults
TIMEOUT = 30.0
URLS = (
    "https://google.com/",
    "http://archive.raspberrypi.org/debian",
    "http://raspbian.raspberrypi.org/raspbian",
)
VERBOSE = False
THREADS = 8


def check_url(url, timeout=TIMEOUT) -> bool:
    """
    Return True if a `url` is reachable, else False.

    >>> check_url(URLS[0])
    True
    """
    logger.debug(f"Trying to reach {url}")
    with urllib.request.urlopen(url, timeout=timeout) as _:
        logger.debug(f"Reached {url}")
        return True


def check_failed(url_up: Dict[str, bool]) -> List[str]:
    """
    >>> len(check_failed({
    ...     'https://www.google.com': True,
    ...     'http://archive.raspberrypi.org/debian': False,
    ...     'http://raspbian.raspberrypi.org/raspbian': False,
    ... }))
    2
    """
    return [u for u, ok in url_up.items() if not ok]


def i_can_has_threaded_connection(
    urls=URLS,
    timeout=TIMEOUT,
    verbose=VERBOSE,
    threads=THREADS,
) -> int:
    if not threads:
        threads = len(urls)
        logger.debug(f"Using {threads} threads.")
    
    # we need to keep track of the time since we might restart `as_completed`
    start = time.time()

    # we'll keep track of what urls are up with this
    url_up = {u: False for u in urls}

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as exe:
        try:
            while True:
                # check if we timed out
                time_left = timeout - (time.time() - start)
                logger.debug(f"{time_left:.2f} seconds left before timeout")
                if time_left < 0.0:
                    logger.debug(f"TIMEOUT:time_left < 0.0")
                    break

                # (re)submit all urls that aren't already up
                future_to_url = {
                    exe.submit(check_url, url, timeout=timeout): url
                    for url in urls
                    if not url_up[url]
                }

                # iterate through the futures as they complete
                for future in concurrent.futures.as_completed(
                    future_to_url, timeout=time_left,
                ):
                    url = future_to_url[future]
                    try:
                        url_up[url] = future.result()
                        logger.info(f"OK:{url}")
                    except (URLError, HTTPError) as e:
                        logger.debug(f"RETRY:{url}:{e}", exc_info=verbose)  # pragma no cover
                        continue  # pragma no cover
                
                # if we suceeded, we'll return 0
                if not check_failed(url_up):
                    logger.info(f"OK:All Urls.")
                    return 0

        except concurrent.futures.TimeoutError as e:
            logger.debug(f"TIMEOUT:executor:{e}")
            pass
        except ValueError as e:
            logger.error(f"{e}", exc_info=verbose)
            return -2
        except Exception as e:  # pragma no cover
            logger.error(f"Unexpected Error: {e}", exc_info=True)  # pragma no cover
            return -3  # pragma no cover

    failed = check_failed(url_up)
    logger.error(f"FAIL:{failed}")
    return len(failed) if len(failed) < 126 else -1


def cli_main(args=None):
    import argparse

    ap = argparse.ArgumentParser(
        description="Waits for a connection for `--timeout` seconds",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    ap.add_argument(
        "--timeout",
        help="before returning the number of inaccessable urls",
        type=float,
        default=TIMEOUT,
    )

    ap.add_argument(
        "--urls",
        help="to wait on in parallel",
        nargs="*",
        default=URLS,
    )

    ap.add_argument(
        "-v",
        "--verbose",
        action="store_true",
    )

    ap.add_argument(
        "--threads",
        type=int,
        help="size of thread pool (default is number of `--urls`)",
    )

    args = ap.parse_args(args)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    return i_can_has_threaded_connection(**vars(args))


if __name__ == "__main__":
    sys.exit(cli_main())  # pragma no cover
