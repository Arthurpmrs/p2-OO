from datetime import datetime
from typing import Iterator
from itertools import count
from cms.models import (
    AnalyticsEntry,
    Comment,
    MediaFile,
    Permission,
    Post,
    PostAction,
    PostAnalyticsEntry,
    Site,
    SiteAction,
    SiteAnalyticsEntry,
    User,
)


class UserRepository:
    __users: dict[int, User]
    __id_counter: Iterator[int]

    def __init__(self):
        self.__users = {}
        self.__id_counter = count(1)

    def add_user(self, user: User) -> int:
        user_id = next(self.__id_counter)
        user.id = user_id
        self.__users.update({user_id: user})
        return user_id

    def get_users(self) -> list[User]:
        return list(self.__users.values())

    def validate_user(self, username: str, password: str) -> User:
        selected_user = None
        for user in self.__users.values():
            if user.username == username:
                selected_user = user
                break

        if not selected_user:
            raise ValueError("Credenciais inválidas.")

        if selected_user.password != password:
            raise ValueError("Credenciais inválidas.")

        return selected_user

    def delete_user(self, user_id: int):
        self.__users.pop(user_id)


class AnalyticsRepository:
    __entries: dict[int, AnalyticsEntry]
    __id_counter: Iterator[int]

    def __init__(self):
        self.__entries = {}
        self.__id_counter = count(1)

    def log(self, entry: AnalyticsEntry) -> int:
        entry_id = next(self.__id_counter)
        entry.id = entry_id
        self.__entries.update({entry_id: entry})
        return entry_id

    def show_logs(self, limit: int = 5):
        entries = sorted(
            [e for e in self.__entries.values()], key=lambda x: x.created_at
        )
        for entry in entries[-limit:]:
            entry.display_log()

    def get_site_accesses(self, site_id: int) -> int:
        return self._get_site_info_by_action(site_id, SiteAction.ACCESS)

    def get_site_post_creation_count(self, site_id: int) -> int:
        return self._get_site_info_by_action(site_id, SiteAction.CREATE_POST)

    def get_site_media_upload_count(self, site_id: int) -> int:
        return self._get_site_info_by_action(site_id, SiteAction.UPLOAD_MEDIA)

    def _get_site_info_by_action(self, site_id: int, action: SiteAction) -> int:
        return len(
            [
                entry
                for entry in self.__entries.values()
                if isinstance(entry, SiteAnalyticsEntry)
                and entry.action == action
                and site_id == entry.site.id
            ]
        )

    def get_site_total_post_views(self, site_id: int) -> int:
        return self._get_site_total_post_info_by_action(site_id, PostAction.VIEW)

    def get_site_total_post_shares(self, site_id: int) -> int:
        return self._get_site_total_post_info_by_action(site_id, PostAction.SHARE)

    def get_site_total_post_comments(self, site_id: int) -> int:
        return self._get_site_total_post_info_by_action(site_id, PostAction.COMMENT)

    def _get_site_total_post_info_by_action(
        self, site_id: int, action: PostAction
    ) -> int:
        return len(
            [
                entry
                for entry in self.__entries.values()
                if isinstance(entry, PostAnalyticsEntry)
                and entry.action == action
                and site_id == entry.site.id
            ]
        )

    def get_post_views(self, post_id: int) -> int:
        return self._get_post_info_by_action(post_id, PostAction.VIEW)

    def get_post_shares(self, post_id: int) -> int:
        return self._get_post_info_by_action(post_id, PostAction.SHARE)

    def get_post_comments(self, post_id: int) -> int:
        return self._get_post_info_by_action(post_id, PostAction.COMMENT)

    def _get_post_info_by_action(self, post_id: int, action: PostAction) -> int:
        return len(
            [
                entry
                for entry in self.__entries.values()
                if isinstance(entry, PostAnalyticsEntry)
                and entry.action == action
                and post_id == entry.post.id
            ]
        )


class SiteRepository:
    __sites: dict[int, Site]
    __id_counter: Iterator[int]

    def __init__(self):
        self.__sites = {}
        self.__id_counter = count(1)

    def add_site(self, site: Site) -> int:
        site_id = next(self.__id_counter)
        site.id = site_id
        self.__sites.update({site_id: site})
        return site_id

    def get_sites(self) -> list[Site]:
        return [site for site in self.__sites.values()]

    def get_user_sites(self, user: User) -> list[Site]:
        return [site for site in self.__sites.values() if site.owner.id == user.id]


class PermissionRepository:
    __permissions: dict[tuple[int, int], Permission]

    def __init__(self):
        self.__permissions = {}

    def grant_permission(self, permission: Permission):
        self.__permissions.update(
            {(permission.user.id, permission.site.id): permission}
        )

    def has_permission(self, user: User, site: Site) -> bool:
        return True if self.__permissions.get((user.id, site.id)) else False

    def get_not_managers(self, site: Site, repo: UserRepository) -> list[User]:
        has_permission = [
            permission.user.id
            for permission in self.__permissions.values()
            if permission.site.id == site.id
        ]
        users = repo.get_users()

        return [user for user in users if user.id not in has_permission]


class PostRepository:
    __posts: dict[int, Post]
    __id_counter: Iterator[int]

    def __init__(self):
        self.__posts = {}
        self.__id_counter = count(1)

    def add_post(self, post: Post) -> int:
        post_id = next(self.__id_counter)
        post.id = post_id
        self.__posts.update({post_id: post})
        return post_id

    def get_site_posts(self, site: Site) -> list[Post]:
        posts: list[Post] = []
        now = datetime.now()
        for post in self.__posts.values():
            if post.site.id == site.id and post.scheduled_to < now:
                posts.append(post)

        return posts


class CommentRepository:
    __comments: dict[int, Comment]
    __id_counter: Iterator[int]

    def __init__(self):
        self.__comments = {}
        self.__id_counter = count(1)

    def add_comment(self, comment: Comment) -> int:
        comment_id = next(self.__id_counter)
        comment.id = comment_id
        self.__comments.update({comment_id: comment})
        return comment_id

    def get_post_comments(self, post: Post) -> list[Comment]:
        return [
            comment
            for comment in self.__comments.values()
            if comment.post.id == post.id
        ]


class MediaRepository:
    __medias: dict[int, MediaFile]
    __id_counter: Iterator[int]

    def __init__(self):
        self.__medias = {}
        self.__id_counter = count(1)

    def add_midia(self, media: MediaFile) -> int:
        media_id = next(self.__id_counter)
        media.id = media_id
        self.__medias.update({media_id: media})
        return media_id

    def get_site_medias(self, site: Site) -> list[MediaFile]:
        return [media for media in self.__medias.values() if media.site.id == site.id]

    def get_media_by_id(self, media_id: int) -> MediaFile:
        return self.__medias[media_id]

    def remove_media(self, media_id: int):
        self.__medias.pop(media_id)
