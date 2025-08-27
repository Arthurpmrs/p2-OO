from abc import ABC, abstractmethod
from typing import Callable, TypedDict

from cms.models import Site, User
from cms.repository import (
    AnalyticsRepository,
    CommentRepository,
    MediaRepository,
    PermissionRepository,
    PostRepository,
    SiteRepository,
    UserRepository,
)

MenuOptions = TypedDict(
    "MenuOptions", {"message": str, "function": Callable[..., None]}
)


class AbstractMenu(ABC):
    @abstractmethod
    def show(self):
        pass


class AppContext:
    """Centraliza repositórios e estado global da aplicação com encapsulamento."""

    def __init__(self):
        self.__site_repo = SiteRepository()
        self.__post_repo = PostRepository()
        self.__user_repo = UserRepository()
        self.__comment_repo = CommentRepository()
        self.__media_repo = MediaRepository()
        self.__analytics_repo = AnalyticsRepository()
        self.__permission_repo = PermissionRepository()

        self.__logged_user: User | None = None
        self.__selected_site: Site | None = None

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
    def logged_user(self) -> User | None:
        """Usuário logado atual (somente leitura direta)."""
        return self.__logged_user

    def login(self, user: User):
        """Faz login de um usuário."""
        self.__logged_user = user

    def logout(self):
        """Desloga o usuário atual."""
        self.__logged_user = None
        self.__selected_site = None

    def require_logged_user(self) -> User:
        if not self.__logged_user:
            raise RuntimeError("No user is logged in")
        return self.__logged_user

    @property
    def selected_site(self) -> Site | None:
        """Site atualmente selecionado (somente leitura direta)."""
        return self.__selected_site

    def select_site(self, site: Site):
        """Seleciona um site válido para o contexto."""
        self.__selected_site = site

    def require_selected_site(self) -> Site:
        if not self.__selected_site:
            raise RuntimeError("No site selected")
        return self.__selected_site

    def clear_selected_site(self):
        """Reseta o site selecionado (sem logout)."""
        self.__selected_site = None

    def reset_context(self):
        """Reinicia os repositórios e estado."""
        self.__site_repo = SiteRepository()
        self.__post_repo = PostRepository()
        self.__user_repo = UserRepository()
        self.__comment_repo = CommentRepository()
        self.__analytics_repo = AnalyticsRepository()
        self.__logged_user = None
        self.__selected_site = None
