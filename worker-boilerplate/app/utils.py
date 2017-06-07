import math
import urlparse


def generate_followup_urls(response_dict):
    """
    Given a paginated response body, returns a list of URLS for all
    pages of pagination.
    """
    next_url = response_dict['next']
    base_url, params = next_url.split('?', 1)

    # Figure out how many pages of data exist
    params_dict = {k: v[0] for k, v in urlparse.parse_qs(params).items()}
    limit = int(params_dict['limit'])
    total_records = response_dict['count']
    num_pages = int(math.ceil(total_records / float(limit)))

    # Create urls for subsequent pages of data
    def join_url(base, params):
        return '?'.join([
            base,
            '&'.join(["{}={}".format(k, v) for k, v in params.items()])
        ])
    return [
        join_url(base_url, dict(params_dict, offset=i * limit))
        for i in range(1, num_pages)
    ]


response = dict(count=1000, next="http://foo.com/api?offset=100&limit=100")
assert generate_followup_urls(response) == [
    'http://foo.com/api?limit=100&offset=100',
    'http://foo.com/api?limit=100&offset=200',
    'http://foo.com/api?limit=100&offset=300',
    'http://foo.com/api?limit=100&offset=400',
    'http://foo.com/api?limit=100&offset=500',
    'http://foo.com/api?limit=100&offset=600',
    'http://foo.com/api?limit=100&offset=700',
    'http://foo.com/api?limit=100&offset=800',
    'http://foo.com/api?limit=100&offset=900']

response = dict(count=1000, next="http://foo.com/api?offset=100&limit=100&x=y")
assert generate_followup_urls(response) == [
    'http://foo.com/api?x=y&limit=100&offset=100',
    'http://foo.com/api?x=y&limit=100&offset=200',
    'http://foo.com/api?x=y&limit=100&offset=300',
    'http://foo.com/api?x=y&limit=100&offset=400',
    'http://foo.com/api?x=y&limit=100&offset=500',
    'http://foo.com/api?x=y&limit=100&offset=600',
    'http://foo.com/api?x=y&limit=100&offset=700',
    'http://foo.com/api?x=y&limit=100&offset=800',
    'http://foo.com/api?x=y&limit=100&offset=900']

response = dict(count=1001, next="http://foo.com/api?offset=100&limit=100")
assert generate_followup_urls(response) == [
    'http://foo.com/api?limit=100&offset=100',
    'http://foo.com/api?limit=100&offset=200',
    'http://foo.com/api?limit=100&offset=300',
    'http://foo.com/api?limit=100&offset=400',
    'http://foo.com/api?limit=100&offset=500',
    'http://foo.com/api?limit=100&offset=600',
    'http://foo.com/api?limit=100&offset=700',
    'http://foo.com/api?limit=100&offset=800',
    'http://foo.com/api?limit=100&offset=900',
    'http://foo.com/api?limit=100&offset=1000']
