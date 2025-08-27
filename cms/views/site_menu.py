from cms.models import (
    Permission,
    Post,
    PostAction,
    PostAnalyticsEntry,
    Site,
    SiteAction,
    SiteAnalyticsEntry,
    SiteTemplateType,
    User,
)
from cms.services.post_builder import PostBuilder
from cms.services.site_template import build_site_template
from cms.utils import select_enum
from cms.views.media_library_menu import MediaLibraryMenu
from cms.views.menu import AbstractMenu, AppContext, MenuOptions
from cms.views.post_menu import PostMenu


class SiteMenu(AbstractMenu):
    context: AppContext
    logged_user: User
    selected_site: Site

    def __init__(
        self,
        context: AppContext,
        logged_user: User,
        selected_site: Site,
    ):
        self.context = context
        self.logged_user = logged_user
        self.selected_site = selected_site

    def show(self):
        options: list[MenuOptions] = [
            {"message": "Selecionar posts do site", "function": self._select_post},
        ]

        if self.context.permission_repo.has_permission(
            self.logged_user, self.selected_site
        ):
            options.extend(
                [
                    {
                        "message": "Criar post no site",
                        "function": self._create_site_post,
                    },
                    {
                        "message": "Biblioteca de Mídias",
                        "function": self._media_library_menu,
                    },
                    {
                        "message": "Ver estatísticas do site",
                        "function": self._show_site_analytics,
                    },
                    {
                        "message": "Mudar template do site",
                        "function": self._configure_site_template,
                    },
                ]
            )

            if self.logged_user.username == self.selected_site.owner.username:
                options.extend(
                    [
                        {
                            "message": "Adicionar Gerente",
                            "function": self._add_manager,
                        },
                    ]
                )

        def display_title():
            template = build_site_template(
                site=self.selected_site,
                post_repo=self.context.post_repo,
                analytics_repo=self.context.analytics_repo,
            )
            template.display()

        SiteMenu.prompt_menu_option(options, display_title)

    def _create_site_post(self):
        pb = PostBuilder(self.selected_site, self.logged_user, self.context.media_repo)
        try:
            post = pb.build_post()
        except ValueError:
            print(" ")
            input(
                "Criação do Post não pode continuar sem uma linguagem. "
                "Clique Enter para voltar ao menu."
            )
            return
        else:
            self.context.post_repo.add_post(post)
            self.context.analytics_repo.log(
                SiteAnalyticsEntry(
                    user=self.logged_user,
                    site=self.selected_site,
                    action=SiteAction.CREATE_POST,
                )
            )

            print(" ")
            input("Post criado. Clique Enter para voltar ao menu.")

    def _add_manager(self):
        print("Selecione um usuário para ser gerente da página:")
        users = self.context.permission_repo.get_not_managers(
            self.selected_site, self.context.user_repo
        )
        for i, user in enumerate(users):
            print(f"{i + 1}. {user.username} ({user.email})")
        print("0. Voltar")

        selected_indexes = input(
            "\nDigite os números separados por vírgula (ex: 1,3): "
        ).split(",")

        for idx in selected_indexes:
            idx = idx.strip()

            if not idx.isdigit():
                continue

            n = int(idx)

            if n == 0:
                return

            if n < 0 or n > len(users):
                print("Opção inválida.\n")
                continue

            if 1 <= n <= len(users):
                user = users[n - 1]
                print(f"Permissão de gerência dada ao usuário {user.username}.")
                self.context.permission_repo.grant_permission(
                    Permission(user=user, site=self.selected_site)
                )

        print(" ")
        input("Clique Enter para voltar ao menu.")

    def _show_site_analytics(self):
        site = self.selected_site
        analytics_repo = self.context.analytics_repo

        accesses = analytics_repo.get_site_accesses(site.id)
        post_creations = analytics_repo.get_site_post_creation_count(site.id)
        media_uploads = analytics_repo.get_site_media_upload_count(site.id)

        total_views = analytics_repo.get_site_total_post_views(site.id)
        total_comments = analytics_repo.get_site_total_post_comments(site.id)
        total_shares = analytics_repo.get_site_total_post_shares(site.id)

        print("=== Estatísticas do Site ===")
        print(f"Nome: {site.name}")
        print(f"Acessos ao site: {accesses}")
        print(f"Posts criados: {post_creations}")
        print(f"Uploads de mídia: {media_uploads}")
        print(" ")
        print("--- Interações com os Posts ---")
        print(f"Visualizações totais: {total_views}")
        print(f"Comentários totais: {total_comments}")
        print(f"Compartilhamentos totais: {total_shares}")

        print(" ")
        input("Clique Enter para voltar ao Menu.")

    def _configure_site_template(self):
        new_template = select_enum(
            SiteTemplateType, "Escolha o layout de apresentação do site:"
        )
        if new_template:
            self.selected_site.template = new_template
            print(f"Template atualizado para: {new_template.value}.", end=" ")
        else:
            print("Opção inválida.", end=" ")

        input("Clique enter para voltar ao menu.")

    def _select_post(self):
        posts: list[Post] = self.context.post_repo.get_site_posts(self.selected_site)

        def execute_for_option(selected_post: Post):
            self.context.analytics_repo.log(
                PostAnalyticsEntry(
                    user=self.logged_user,
                    site=self.selected_site,
                    post=selected_post,
                    action=PostAction.VIEW,
                )
            )
            PostMenu(
                self.context, self.logged_user, self.selected_site, selected_post
            ).show()

        SiteMenu.prompt_generic(
            posts,
            "Posts do site",
            execute_for_option,
            lambda m: m.get_default_title(),
        )

    def _media_library_menu(self):
        MediaLibraryMenu(self.context, self.logged_user, self.selected_site).show()
