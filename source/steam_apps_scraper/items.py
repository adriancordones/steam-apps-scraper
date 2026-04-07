from dataclasses import dataclass

@dataclass
class AppItem:
    id: int = None
    title: str = None
    date: str = None
    developer_name: str = None
    publisher_name: str = None

    reviews_total: int = None
    reviews_recent: int = None
    reviews_total_summary: str = None
    reviews_recent_summary: str = None

    original_price: float = None
    discount_price: float = None
    discount_percent: int = None

    achievements_number: int = None
    langs_number: int = None
    dlcs_number: int = None
    has_ost: bool = None
    is_dlc: bool = None
    is_ost: bool = None

    short_desc: str = None
    dlcs: str = None
    tags: str = None
    genres: str = None
    languages: str = None
    
    url: str = None
    developer_url: str = None
    publisher_url: str = None