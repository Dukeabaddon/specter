from abc import ABC, abstractmethod
from typing import List
from ..models import Post

class BaseFetcher(ABC):
    @abstractmethod
    def fetch_posts(self, page_name: str, limit: int = 5) -> List[Post]:
        """
        Fetch latest posts for a given public Facebook page.
        """
        pass
