from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from abc import ABC, abstractmethod
# from typing import TypedDict


class UserRole(Enum):
    ADMIN = 1
    USER = 2


class MediaType(Enum):
    IMAGE = 1
    VIDEO = 2


class SocialNetwork(Enum):
    TWITTER = "Twitter"
    FACEBOOK = "Facebook"
    INSTAGRAM = "Instagram"
    LINKEDIN = "LinkedIn"


class SiteTemplate(Enum):
    TOP_POSTS_FIRST = "Posts mais vistos"
    TOP_COMMENTS_FIRST = "Posts mais comentados"
    LATEST_POSTS = "Últimos posts"
    FOCUS_ON_MEDIA = "Galeria de mídia"


# PostContent = TypedDict("PostContent", {"title": str, "body": list["PostBlock"]})

type LanguageCode = str


@dataclass
class Language:
    name: str
    codes: list[LanguageCode]

    def add_code(self, code: str):
        self.codes.append(code)

    def get_code(self) -> str:
        if not self.codes:
            raise Exception("Language code not provided!")

        return self.codes[0]


@dataclass
class User:
    id: int = field(init=False)
    first_name: str
    last_name: str
    email: str
    username: str
    password: str
    role: UserRole


@dataclass
class Site:
    id: int = field(init=False)
    owner: User
    name: str
    description: str
    template: SiteTemplate = SiteTemplate.LATEST_POSTS

    def get_url(self) -> str:
        domain = self.name.lower().replace(" ", "-")
        return f"www.cms.{domain}.com.br"


@dataclass
class Media(ABC):
    id: int = field(init=False)
    uploader: User
    filename: str
    path: Path
    media_type: MediaType
    site: Site
    width: str
    height: str


@dataclass
class Video(Media):
    duration: float


@dataclass
class Image(Media):
    pass


@dataclass
class ContentBlock(ABC):
    order: int
    language: str

    @abstractmethod
    def display_content(self):
        print(self.get_content())
        print(" ")

    @abstractmethod
    def get_content(self) -> str:
        pass


@dataclass
class TextBlock(ContentBlock):
    text: str

    def get_content(self) -> str:
        return f"<p>{self.text}</p>"


@dataclass
class MediaBlock(ContentBlock):
    media: Media
    alt: str

    def get_content(self) -> str:
        content = ""

        if self.media.media_type == MediaType.IMAGE:
            content = f"<Img src='{self.media.filename}' alt='{self.alt}' />"
        else:
            content = f"<Video src='{self.media.filename}' alt='{self.alt}' />"

        return content


@dataclass
class CaroulselBlock(ContentBlock):
    medias: list[Media]
    alt: str

    def get_content(self) -> str:
        return ""


@dataclass
class Content(ABC):
    title: str
    body: list[ContentBlock]
    language: Language


@dataclass
class Post:
    id: int = field(init=False)
    poster: User
    site: Site
    content_by_language: dict[LanguageCode, Content]
    default_language: Language
    scheduled_to: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)

    def is_visible(self) -> bool:
        return self.scheduled_to >= datetime.now()

    def display_post(self, language: Language | None = None):
        content, lang = self._get_content_by_language(language)

        print(f"[{lang}] ", content.title)
        print(f"Data de criação: {self.created_at}")
        print(" ")
        for block in content.body:
            block.display_content()
        print(" ")
        print(f"Criado por: {self.poster.username}")
        print(" ")
        print(" ")

    def display_post_short(self, language: Language | None = None):
        content, lang = self._get_content_by_language(language)

        print(f"[{lang}] ", content.title)
        print(f"{self.poster.username}@{self.created_at}")
        print(" ")

    def format_post_to_social_network(self, language: Language | None = None) -> str:
        SIZE_LIMIT = 100
        content, lang = self._get_content_by_language(language)

        block_to_display = None
        for block in content.body:
            if isinstance(block, TextBlock):
                block_to_display = block
                break

        s = f"[{lang}] {content.title}\n"
        s += f"{self.poster.username}@{self.created_at}\n"
        s += "\n"

        if block_to_display:
            s += block_to_display.get_content()[:SIZE_LIMIT]
            s += "\n" if len(block_to_display.get_content()) < SIZE_LIMIT else "...\n"

        s += "\n"
        s += f"Veja o post completo em: {self.site.get_url()}\n"

        return s

    def display_first_post_image(self):
        for block in self.content_by_language[self.default_language.get_code()].body:
            if isinstance(block, MediaBlock):
                block.display_content()
                return

    def _get_content_by_language(
        self, language: Language | None = None
    ) -> tuple[Content, Language]:
        if not language:
            language = self.default_language

        return self.content_by_language[language.get_code()], language

    def get_default_title(self) -> str:
        if len(self.content_by_language) == 0:
            return "Não foi fornecido um título para esse Post."

        return self.content_by_language[self.default_language.get_code()].title


@dataclass
class Comment:
    id: int = field(init=False)
    post: Post
    commenter: User
    body: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(kw_only=True)
class AnalyticsEntry(ABC):
    id: int = field(init=False)
    user: User
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, str] = field(default_factory=dict[str, str])

    @abstractmethod
    def display_log(self):
        pass


class SiteAction(Enum):
    ACCESS = 1
    CREATE_POST = 2
    UPLOAD_MEDIA = 3


@dataclass(kw_only=True)
class SiteAnalyticsEntry(AnalyticsEntry):
    site: Site
    action: SiteAction

    def display_log(self):
        print(
            f"{self.site.name} - {self.user.username}@{self.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {str(self.action)}"
        )


class PostAction(Enum):
    VIEW = 1
    COMMENT = 2
    SHARE = 3


@dataclass(kw_only=True)
class PostAnalyticsEntry(AnalyticsEntry):
    site: Site
    post: Post
    action: PostAction

    def display_log(self):
        print(f"{self.site.name} - {self.post.get_default_title()[:40]}")
        print(
            f"  {self.user.username}@{self.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {str(self.action)}"
        )
