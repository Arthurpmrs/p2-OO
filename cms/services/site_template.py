from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type
from cms.models import MediaBlock, Post, Site, SiteTemplateType
from cms.repository import PostRepository, AnalyticsRepository


@dataclass
class SiteTemplate(ABC):
    site: Site
    post_repo: PostRepository
    analytics_repo: AnalyticsRepository

    @abstractmethod
    def select_posts(self) -> list[Post]:
        pass

    def display(self):
        print(f"<========== {self.site.name} ==========>")
        print(self.site.description)
        print(" ")

        posts = self.select_posts()

        for post in posts[:3]:
            self.display_post(post)

        print(" ")

    def display_post(self, post: Post):
        post.display_post_short()


class TopPostsFirstTemplate(SiteTemplate):
    def select_posts(self):
        return sorted(
            self.post_repo.get_site_posts(self.site),
            key=lambda p: self.analytics_repo.get_post_views(p.id),
            reverse=True,
        )


class TopCommentsFirstTemplate(SiteTemplate):
    def select_posts(self):
        return sorted(
            self.post_repo.get_site_posts(self.site),
            key=lambda p: self.analytics_repo.get_post_comments(p.id),
            reverse=True,
        )


class FocusOnMediaTemplate(SiteTemplate):
    def select_posts(self):
        return [
            p
            for p in self.post_repo.get_site_posts(self.site)
            if any(isinstance(b, MediaBlock) for b in p.get_default_body())
        ]

    def display_post(self, post: Post):
        post.display_first_post_image()


class LatestPostsTemplate(SiteTemplate):
    def select_posts(self):
        return sorted(
            self.post_repo.get_site_posts(self.site),
            key=lambda p: p.created_at,
            reverse=True,
        )


_template_map: dict[SiteTemplateType, Type[SiteTemplate]] = {
    SiteTemplateType.TOP_POSTS_FIRST: TopPostsFirstTemplate,
    SiteTemplateType.TOP_COMMENTS_FIRST: TopCommentsFirstTemplate,
    SiteTemplateType.LATEST_POSTS: LatestPostsTemplate,
    SiteTemplateType.FOCUS_ON_MEDIA: FocusOnMediaTemplate,
}


def build_site_template(
    site: Site,
    post_repo: PostRepository,
    analytics_repo: AnalyticsRepository,
) -> SiteTemplate:
    template_cls = _template_map.get(site.template)
    if not template_cls:
        raise ValueError(f"Unknown template: {site.template}")

    return template_cls(site, post_repo, analytics_repo)
