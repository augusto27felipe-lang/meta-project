from backend.core.adapters.mock_adapter import MockAdapter


def test_mock_adapter_populates_domain():
    adapter = MockAdapter()
    adapter.start()
    results = adapter.search("Python")
    assert isinstance(results, list)
    assert len(results) > 0
    ad = results[0]
    assert "domain" in ad
    assert ad["domain"] is not None
    assert ad["domain"].endswith(".example.com")
    adapter.stop()
