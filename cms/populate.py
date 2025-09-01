from pathlib import Path
from cms.models import (
    Comment,
    Content,
    MediaBlock,
    MediaFile,
    Permission,
    Post,
    PostAction,
    PostAnalyticsEntry,
    Site,
    SiteAction,
    SiteAnalyticsEntry,
    TextBlock,
    User,
    UserRole,
)
from cms.utils import infer_media_type
from cms.views.menu import AppContext


def populate(context: AppContext):
    admin = User(
        first_name="Admin",
        last_name="Admin",
        email="admin@admin.com",
        username="admin",
        password="Admin123",
        role=UserRole.ADMIN,
    )
    context.user_repo.add_user(admin)
    user1 = User(
        first_name="User1",
        last_name="User1",
        email="user1@user.com",
        username="user1",
        password="User123",
        role=UserRole.USER,
    )
    context.user_repo.add_user(user1)
    user2 = User(
        first_name="User2",
        last_name="User2",
        email="user2@user.com",
        username="user2",
        password="User123",
        role=UserRole.USER,
    )
    context.user_repo.add_user(user2)
    site = Site(
        owner=admin, name="Meu blog", description="Meus pensamentos e dia-a-dia."
    )
    context.site_repo.add_site(site)
    context.permission_repo.grant_permission(Permission(user=admin, site=site))
    _populate_medias(context, admin, site)
    post1 = Post(poster=admin, site=site)
    post1.add_content(
        "pt-br",
        Content(
            title="Título do meu post",
            language=context.lang_service.get_language_by_code("br"),
            body=[
                TextBlock(
                    order=1,
                    text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
                ),
                MediaBlock(
                    order=2,
                    alt="Uma imagem.",
                    media=context.media_repo.get_media_by_id(1),
                ),
                TextBlock(
                    order=3,
                    text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
                ),
            ],
        ),
    )
    post1.add_content(
        "en-us",
        Content(
            title="Super duper title of doom",
            language=context.lang_service.get_language_by_code("en"),
            body=[
                TextBlock(
                    order=1,
                    text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
                ),
                MediaBlock(
                    order=2,
                    alt="Some Imagee.",
                    media=context.media_repo.get_media_by_id(1),
                ),
                TextBlock(
                    order=3,
                    text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
                ),
            ],
        ),
    )
    post2 = Post(poster=admin, site=site)
    post2.add_content(
        "en-us",
        Content(
            title="Title of my post",
            language=context.lang_service.get_language_by_code("en"),
            body=[
                TextBlock(
                    order=1,
                    text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
                ),
                MediaBlock(
                    order=2,
                    alt="Some video",
                    media=context.media_repo.get_media_by_id(5),
                ),
                TextBlock(
                    order=3,
                    text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
                ),
            ],
        ),
    )
    context.post_repo.add_post(post1)
    context.post_repo.add_post(post2)
    context.analytics_repo.log(
        SiteAnalyticsEntry(
            user=admin,
            site=site,
            action=SiteAction.CREATE_POST,
            metadata={"post_id": str(post1.id)},
        )
    )
    context.analytics_repo.log(
        SiteAnalyticsEntry(
            user=admin,
            site=site,
            action=SiteAction.CREATE_POST,
            metadata={"post_id": str(post2.id)},
        )
    )

    comment1_post1 = Comment(post=post1, commenter=user1, body="Nice post bro.")
    comment2_post1 = Comment(post=post1, commenter=user2, body="Thanks!")
    comment3_post1 = Comment(post=post1, commenter=user2, body="A second comment!")
    context.comment_repo.add_comment(comment1_post1)
    context.comment_repo.add_comment(comment2_post1)
    context.comment_repo.add_comment(comment3_post1)
    context.analytics_repo.log(
        PostAnalyticsEntry(
            user=user1,
            site=site,
            post=post1,
            action=PostAction.VIEW,
        )
    )
    context.analytics_repo.log(
        PostAnalyticsEntry(
            user=user1,
            site=site,
            post=post1,
            action=PostAction.COMMENT,
            metadata={"comment_id": str(comment1_post1.id)},
        )
    )
    context.analytics_repo.log(
        PostAnalyticsEntry(
            user=user2,
            site=site,
            post=post1,
            action=PostAction.VIEW,
        )
    )
    context.analytics_repo.log(
        PostAnalyticsEntry(
            user=user2,
            site=site,
            post=post1,
            action=PostAction.COMMENT,
            metadata={"comment_id": str(comment2_post1.id)},
        )
    )
    context.analytics_repo.log(
        PostAnalyticsEntry(
            user=user2,
            site=site,
            post=post1,
            action=PostAction.VIEW,
        )
    )
    context.analytics_repo.log(
        PostAnalyticsEntry(
            user=user2,
            site=site,
            post=post1,
            action=PostAction.COMMENT,
            metadata={"comment_id": str(comment3_post1.id)},
        )
    )


def _populate_medias(context: AppContext, uploader: User, selected_site: Site):
    folder = Path("static")
    for filepath in folder.rglob("*"):
        if filepath.is_file():
            filepath = filepath.resolve()
            media_type = infer_media_type(filepath.suffix)

            context.media_repo.add_midia(
                MediaFile(
                    uploader=uploader,
                    filename=filepath.name,
                    path=filepath,
                    media_type=media_type,
                    site=selected_site,
                    width="1000",
                    height="1000",
                    duration=None,
                )
            )

            context.analytics_repo.log(
                SiteAnalyticsEntry(
                    user=uploader,
                    site=selected_site,
                    action=SiteAction.UPLOAD_MEDIA,
                )
            )
