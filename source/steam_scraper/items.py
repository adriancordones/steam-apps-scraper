from dataclasses import dataclass

@dataclass
class AppItem:
    id: int = None
    title: str = None
    developer_name: str = None
    editor_name: str = None

    date: str = None
    total_reviews: int = None

    short_desc: str = None
    tags: str = None
    
    game_link: str = None
    developer_link: str = None
    editor_link: str = None