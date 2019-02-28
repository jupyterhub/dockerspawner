import os
import time
from subprocess import Popen, check_call


import pytest
import requests

here = os.path.dirname(__file__)
hub_url = 'http://127.0.0.1:8000'

@pytest.fixture(scope='session')
def compose_build():
    check_call(['docker-compose', 'build'], cwd=here)


@pytest.fixture(scope='session')
def compose_up(compose_build):
    p = Popen(['docker-compose', 'up'], cwd=here)
    for i in range(60):
        try:
            r = requests.get(hub_url + '/hub/')
            r.raise_for_status()
        except Exception:
            time.sleep(1)
            if p.poll() is not None:
                raise RuntimeError("`docker-compose up` failed")
        else:
            break
    else:
        raise TimeoutError("hub never showed up at %s" % hub_url)

    try:
        yield
    finally:
        p.terminate()
        check_call(['docker-compose', 'stop'], cwd=here)

def test_internal_ssl(compose_up):
    s = requests.Session()
    r = s.post(hub_url + '/hub/login', data={'username': 'fake', 'password': 'ok'})
    r.raise_for_status()
    print(r.url, r.cookies)
    print("end test")
