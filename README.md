# `wait_for_connection.py`



Waits `--timeout` seconds for `--urls` before returning the number of failed
urls in the returncode. -1 is returned if the failed urls are greater than 126.
-2 is returned on invalid url. -3 is returned on any unexpected error.

Usage:

```
usage: wait_for_connection.py [-h] [--timeout TIMEOUT] [--urls [URLS [URLS ...]]] [-v] [--threads THREADS]

Waits for a connection for `--timeout` seconds

optional arguments:
  -h, --help            show this help message and exit
  --timeout TIMEOUT     before returning the number of inaccessable urls (default: 30.0)
  --urls [URLS [URLS ...]]
                        to wait on in parallel (default: ('https://google.com/', 'http://archive.raspberrypi.org/debian', 'http://raspbian.raspberrypi.org/raspbian'))
  -v, --verbose
  --threads THREADS     size of thread pool (default is number of `--urls`) (default: None)
```