from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from abc import ABC, abstractmethod
from typing import TypedDict


class UserRole(Enum):
    ADMIN = 1
    USER = 2


class MediaType(Enum):
    IMAGE = 1
    VIDEO = 2


class SiteTemplateType(Enum):
    TOP_POSTS_FIRST = "Posts mais vistos"
    TOP_COMMENTS_FIRST = "Posts mais comentados"
    LATEST_POSTS = "Últimos posts"
    FOCUS_ON_MEDIA = "Galeria de mídia"


type LanguageCode = str


@dataclass
class Language:
    name: str
    code: LanguageCode
    aliases: list[LanguageCode] = field(default_factory=list[str])

    def add_alias_code(self, code: LanguageCode):
        if code.lower().strip() not in self.aliases:
            self.aliases.append(code.lower().strip())

    def is_language(self, code: LanguageCode) -> bool:
        p_code = code.lower().strip()
        return p_code == self.code or p_code in self.aliases

    def __str__(self) -> str:
        return f"Lang('{self.name}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Language):
            return NotImplemented
        return other.code == self.code


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
    template: SiteTemplateType = SiteTemplateType.LATEST_POSTS

    def get_domain(self) -> str:
        return self.name.lower().replace(" ", "-")

    def get_url(self) -> str:
        domain = self.get_domain()
        return f"https://www.cms.{domain}.com.br"


@dataclass
class Permission:
    user: User
    site: Site


@dataclass
class MediaFile(ABC):
    id: int = field(init=False)
    uploader: User
    filename: str
    path: Path
    media_type: MediaType
    site: Site
    width: str
    height: str
    duration: float | None

    @property
    def url(self):
        site_domain = self.site.get_domain()
        return f"https://www.cms-media.{site_domain}.com.br/{self.filename}"

    @property
    def dimension(self):
        return f"{self.width}X{self.height}"


@dataclass
class ContentBlock(ABC):
    order: int

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
    media: MediaFile
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
    medias: list[MediaFile]
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
    scheduled_to: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    __content_by_language: dict[LanguageCode, Content] = field(
        init=False, default_factory=dict[LanguageCode, Content]
    )

    def add_content(self, lang: LanguageCode, content: Content):
        self.__content_by_language[lang] = content

    @property
    def default_language(self) -> Language:
        if not self.__content_by_language:
            raise ValueError(f"No content provided for Post(id={self.id}).")
        return next(iter(self.__content_by_language.values())).language

    def is_visible(self) -> bool:
        return self.scheduled_to >= datetime.now()

    def display_post(self, language: Language | None = None):
        content = self.get_content_by_language(language)

        print(f"[{content.language.code}] ", content.title)
        print(f"Data de criação: {self.created_at}")
        print(" ")
        for block in content.body:
            block.display_content()
        print(" ")
        print(f"Criado por: {self.poster.username}")
        print(" ")
        print(" ")

    def display_post_short(self, language: Language | None = None):
        content = self.get_content_by_language(language)

        print(f"[{content.language.code}] ", content.title)
        print(f"{self.poster.username}@{self.created_at}")
        print(" ")

    def format_post_to_social_network(self, language: Language | None = None) -> str:
        SIZE_LIMIT = 100
        content = self.get_content_by_language(language)

        block_to_display = None
        for block in content.body:
            if isinstance(block, TextBlock):
                block_to_display = block
                break

        s = f"[{content.language.code}] {content.title}\n"
        s += f"{self.poster.username}@{self.created_at}\n"
        s += "\n"

        if block_to_display:
            s += block_to_display.get_content()[:SIZE_LIMIT]
            s += "\n" if len(block_to_display.get_content()) < SIZE_LIMIT else "...\n"

        s += "\n"
        s += f"Veja o post completo em: {self.site.get_url()}\n"

        return s

    def display_first_post_image(self):
        for block in self.__content_by_language[self.default_language.code].body:
            if isinstance(block, MediaBlock):
                block.display_content()
                return

    def get_content_by_language(self, language: Language | None = None) -> Content:
        if not language:
            language = self.default_language

        return self.__content_by_language[language.code]

    def get_default_title(self) -> str:
        if not self.__content_by_language:
            raise ValueError(f"No content provided for Post(id={self.id}).")

        return self.__content_by_language[self.default_language.code].title

    def get_languages(self) -> list[Language]:
        return [content.language for content in self.__content_by_language.values()]

    def get_default_body(self) -> list[ContentBlock]:
        return self.__content_by_language[self.default_language.code].body


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


ReportItem = TypedDict("ReportItem", {"name": str, "value": str})
ReportSection = TypedDict("ReportSection", {"title": str, "items": list[ReportItem]})


# The ideia here is to create a generic function that prints the report not caring
# if it is from a site or from a post. It just knows the basic structure of a report
@dataclass
class AnalyticsReport(ABC):
    entries: list[AnalyticsEntry]

    @abstractmethod
    def generate_metrics(self) -> list[ReportSection]:
        pass


@dataclass
class SiteAnalyticsReport(AnalyticsReport):
    site: Site

    def generate_metrics(self) -> list[ReportSection]:
        return [
            {
                "title": "Estatísticas do Site",
                "items": [
                    {"name": "Nome", "value": self.site.name},
                    {"name": "Acessos ao site", "value": str(self.get_site_accesses())},
                    {
                        "name": "Posts criados",
                        "value": str(self.get_site_post_creation_count()),
                    },
                    {
                        "name": "Uploads de mídia",
                        "value": str(self.get_site_media_upload_count()),
                    },
                ],
            },
            {
                "title": "Interações com os Posts",
                "items": [
                    {
                        "name": "Visualizações totais",
                        "value": str(self.get_site_total_post_views()),
                    },
                    {
                        "name": "Comentários totais",
                        "value": str(self.get_site_total_post_comments()),
                    },
                    {
                        "name": "Compartilhamentos totais",
                        "value": str(self.get_site_total_post_shares()),
                    },
                ],
            },
        ]

    def get_site_accesses(self) -> int:
        return self._get_site_info_by_action(SiteAction.ACCESS)

    def get_site_post_creation_count(self) -> int:
        return self._get_site_info_by_action(SiteAction.CREATE_POST)

    def get_site_media_upload_count(self) -> int:
        return self._get_site_info_by_action(SiteAction.UPLOAD_MEDIA)

    def _get_site_info_by_action(self, action: SiteAction) -> int:
        return len(
            [
                entry
                for entry in self.entries
                if isinstance(entry, SiteAnalyticsEntry) and entry.action == action
            ]
        )

    def get_site_total_post_views(self) -> int:
        return self._get_site_total_post_info_by_action(PostAction.VIEW)

    def get_site_total_post_shares(self) -> int:
        return self._get_site_total_post_info_by_action(PostAction.SHARE)

    def get_site_total_post_comments(self) -> int:
        return self._get_site_total_post_info_by_action(PostAction.COMMENT)

    def _get_site_total_post_info_by_action(self, action: PostAction) -> int:
        return len(
            [
                entry
                for entry in self.entries
                if isinstance(entry, PostAnalyticsEntry) and entry.action == action
            ]
        )


@dataclass
class PostAnalyticsReport(AnalyticsReport):
    post: Post

    def generate_metrics(self) -> list[ReportSection]:
        return [
            {
                "title": "Interações com os Posts",
                "items": [
                    {"name": "Visualizações", "value": str(self.get_post_views())},
                    {"name": "Comentários", "value": str(self.get_post_comments())},
                    {"name": "Compartilhamentos", "value": str(self.get_post_shares())},
                ],
            },
        ]

    def get_post_views(self) -> int:
        return self._get_post_info_by_action(PostAction.VIEW)

    def get_post_shares(self) -> int:
        return self._get_post_info_by_action(PostAction.SHARE)

    def get_post_comments(self) -> int:
        return self._get_post_info_by_action(PostAction.COMMENT)

    def _get_post_info_by_action(self, action: PostAction) -> int:
        return len(
            [
                entry
                for entry in self.entries
                if isinstance(entry, PostAnalyticsEntry) and entry.action == action
            ]
        )
