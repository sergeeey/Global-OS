import httpx


def test_base_url_with_query_does_not_corrupt_query_when_enforcing_slash():
    client = httpx.Client(base_url="https://example.org/get?data=1")
    assert client.base_url.query == b"data=1"
    assert str(client.base_url) == "https://example.org/get/?data=1"
    req = client.build_request("GET", "")
    assert req.url.query == b"data=1"
    assert req.url.params["data"] == "1"


def test_base_url_path_still_gets_trailing_slash():
    client = httpx.Client(base_url="https://example.org/path")
    assert str(client.base_url) == "https://example.org/path/"
