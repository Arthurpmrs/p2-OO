from abc import ABC, abstractmethod
from typing import Callable, TypedDict

from cms.repository import (
    AnalyticsRepository,
    CommentRepository,
    MediaRepository,
    PermissionRepository,
    PostRepository,
    SiteRepository,
    UserRepository,
)
from cms.services.languages import LanguageService

MenuOptions = TypedDict(
    "MenuOptions", {"message": str, "function": Callable[..., None]}
)


class AbstractMenu(ABC):
    @abstractmethod
    def show(self):
        pass


class AppContext:
    def __init__(self):
        self.__site_repo = SiteRepository()
        self.__post_repo = PostRepository()
        self.__user_repo = UserRepository()
        self.__comment_repo = CommentRepository()
        self.__media_repo = MediaRepository()
        self.__analytics_repo = AnalyticsRepository()
        self.__permission_repo = PermissionRepository()
        self.__lang_service = LanguageService()

    @property
    def site_repo(self) -> SiteRepository:
        return self.__site_repo

    @property
    def post_repo(self) -> PostRepository:
        return self.__post_repo

    @property
    def user_repo(self) -> UserRepository:
        return self.__user_repo

    @property
    def comment_repo(self) -> CommentRepository:
        return self.__comment_repo

    @property
    def media_repo(self) -> MediaRepository:
        return self.__media_repo

    @property
    def analytics_repo(self) -> AnalyticsRepository:
        return self.__analytics_repo

    @property
    def permission_repo(self) -> PermissionRepository:
        return self.__permission_repo

    @property
    def lang_service(self) -> LanguageService:
        return self.__lang_service

    def reset_context(self):
        """Reinicia os repositórios e estado."""
        self.__site_repo = SiteRepository()
        self.__post_repo = PostRepository()
        self.__user_repo = UserRepository()
        self.__comment_repo = CommentRepository()
        self.__analytics_repo = AnalyticsRepository()
        self.__language_service = LanguageService()
