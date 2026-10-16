from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

@dataclass
class Post:
    post_id: str
    page_name: str
    text: str
    url: str
    published_at: Optional[str] = None
    scraped_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    images: List[str] = field(default_factory=list)
    video: Optional[str] = None
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "post_id": self.post_id,
            "page_name": self.page_name,
            "text": self.text,
            "url": self.url,
            "published_at": self.published_at,
            "scraped_at": self.scraped_at,
            "images": self.images,
            "video": self.video,
            "raw_metadata": self.raw_metadata,
        }
