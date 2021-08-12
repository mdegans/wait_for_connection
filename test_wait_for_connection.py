import pytest
import wait_for_connection

def test_wait():
  wait_for_connection.cli_main((
    '--timeout', '1',
  ))

def test_timeout():
  # this tests the first timeout at the top of the while loop
  assert wait_for_connection.cli_main((
    '--timeout', '0.000001',
  )) > 0
  # and this tests the second timeout
  assert wait_for_connection.cli_main((
    '--timeout', '0.01',
  )) > 0

def test_url_error():
  assert wait_for_connection.cli_main((
    '--urls', 'potato'
  )) == -2
