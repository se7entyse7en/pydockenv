import sys

import requests


if __name__ == '__main__':
    url = sys.argv[1]
    r = requests.get(url)
    print("Requested {url}: status code = {code}".format(
        url=url, code=r.status_code))
