from datetime import datetime
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
    users: dict[int, User] = {}
    id_counter = count(1)

    def add_user(self, user: User) -> int:
        user_id = next(self.id_counter)
        user.id = user_id
        self.users.update({user_id: user})
        return user_id

    def get_users(self) -> list[User]:
        return list(self.users.values())

    def validate_user(self, username: str, password: str) -> User:
        selected_user = None
        for user in self.users.values():
            if user.username == username:
                selected_user = user
                break

        if not selected_user:
            raise ValueError("Credenciais inválidas.")

        if selected_user.password != password:
            raise ValueError("Credenciais inválidas.")

        return selected_user

    def delete_user(self, user_id: int):
        self.users.pop(user_id)


class AnalyticsRepository:
    id_counter = count(1)
    entries: dict[int, AnalyticsEntry] = {}

    def log(self, entry: AnalyticsEntry) -> int:
        entry_id = next(self.id_counter)
        entry.id = entry_id
        self.entries.update({entry_id: entry})
        return entry_id

    def show_logs(self, limit: int = 5):
        entries = sorted([e for e in self.entries.values()], key=lambda x: x.created_at)
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
                for entry in self.entries.values()
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
                for entry in self.entries.values()
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
                for entry in self.entries.values()
                if isinstance(entry, PostAnalyticsEntry)
                and entry.action == action
                and post_id == entry.post.id
            ]
        )


class SiteRepository:
    sites: dict[int, Site] = {}
    id_counter = count(1)

    def add_site(self, site: Site) -> int:
        site_id = next(self.id_counter)
        site.id = site_id
        self.sites.update({site_id: site})
        return site_id

    def get_sites(self) -> list[Site]:
        return [site for site in self.sites.values()]

    def get_user_sites(self, user: User) -> list[Site]:
        return [site for site in self.sites.values() if site.owner.id == user.id]


class PermissionRepository:
    permissions: dict[tuple[int, int], Permission] = {}

    def grant_permission(self, permission: Permission):
        self.permissions.update({(permission.user.id, permission.site.id): permission})

    def has_permission(self, user: User, site: Site) -> bool:
        return True if self.permissions.get((user.id, site.id)) else False

    def get_not_managers(self, site: Site, repo: UserRepository) -> list[User]:
        has_permission = [
            permission.user.id
            for permission in self.permissions.values()
            if permission.site.id == site.id
        ]
        users = repo.get_users()

        return [user for user in users if user.id not in has_permission]


class PostRepository:
    posts: dict[int, Post] = {}
    id_counter = count(1)

    def add_post(self, post: Post) -> int:
        post_id = next(self.id_counter)
        post.id = post_id
        self.posts.update({post_id: post})
        return post_id

    def get_site_posts(self, site: Site) -> list[Post]:
        posts: list[Post] = []
        now = datetime.now()
        for post in self.posts.values():
            if post.site.id == site.id and post.scheduled_to < now:
                posts.append(post)

        return posts


class CommentRepository:
    comments: dict[int, Comment] = {}
    id_counter = count(1)

    def add_comment(self, comment: Comment) -> int:
        comment_id = next(self.id_counter)
        comment.id = comment_id
        self.comments.update({comment_id: comment})
        return comment_id

    def get_post_comments(self, post: Post) -> list[Comment]:
        return [
            comment for comment in self.comments.values() if comment.post.id == post.id
        ]


class MediaRepository:
    medias: dict[int, MediaFile] = {}
    id_counter = count(1)

    def add_midia(self, media: MediaFile) -> int:
        media_id = next(self.id_counter)
        media.id = media_id
        self.medias.update({media_id: media})
        return media_id

    def get_site_medias(self, site: Site) -> list[MediaFile]:
        return [media for media in self.medias.values() if media.site.id == site.id]

    def get_media_by_id(self, media_id: int) -> MediaFile:
        return self.medias[media_id]

    def remove_media(self, media_id: int):
        self.medias.pop(media_id, None)
