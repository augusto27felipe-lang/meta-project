import time
from typing import List, Dict


class MockAdapter:
    def __init__(self, name: str = "mock"):
        self.name = name
        self._running = False

    def start(self):
        self._running = True
        # simulate startup
        time.sleep(0.05)

    def search(self, keyword: str, country: str = "us") -> List[Dict]:
        if not self._running:
            raise RuntimeError("Adapter not started")
        # simulate network + scraping
        time.sleep(0.1)
        return [
            {
                "unique_id": f"{keyword}:{country}:1",
                "keyword": keyword,
                "country": country,
                "title": f"Mock ad for {keyword}",
                # gerar domínio fictício baseado na keyword
                "domain": f"{keyword.lower()}.example.com",
            }
        ]

    def stop(self):
        self._running = False
        time.sleep(0.01)
