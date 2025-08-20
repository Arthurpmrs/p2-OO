import os
from typing import Callable, TypedDict
from pathlib import Path

from cms.models import (
    Comment,
    Content,
    MediaFile,
    MediaBlock,
    Permission,
    Post,
    PostAction,
    PostAnalyticsEntry,
    Site,
    SiteAction,
    SiteAnalyticsEntry,
    SiteTemplateType,
    TextBlock,
    User,
    UserRole,
    Language,
)
from cms.services.post_builder import PostBuilder
from cms.services.post_translator import PostTranslator
from cms.repository import (
    AnalyticsRepository,
    CommentRepository,
    MediaRepository,
    PermissionRepository,
    PostRepository,
    SiteRepository,
    UserRepository,
)
from cms.services.seo_analyzier import display_seo_report
from cms.services.site_template import build_site_template
from cms.services.social_media import SocialMedia, build_social_media_post
from cms.utils import (
    infer_media_type,
    get_language_by_code,
    select_language,
    select_enum,
)


MenuOptions = TypedDict(
    "MenuOptions", {"message": str, "function": Callable[..., None]}
)


class Menu:
    logged_user: User | None
    selected_site: Site | None
    selected_post: Post | None
    selected_media: MediaFile | None
    selected_post_language: Language | None

    def __init__(self):
        self.user_repo = UserRepository()
        self.site_repo = SiteRepository()
        self.post_repo = PostRepository()
        self.comment_repo = CommentRepository()
        self.media_repo = MediaRepository()
        self.analytics_repo = AnalyticsRepository()
        self.permission_repo = PermissionRepository()
        self._populate()
        self.logged_user = None
        self.selected_site = None
        self.selected_post = None
        self.selected_media = None
        self.selected_post_language = None

    def show(self):
        try:
            self.main_menu()
        except KeyboardInterrupt:
            print("\nSaindo.")

    def main_menu(self):
        while True:
            os.system("clear")
            print("CMS\n")

            if self.logged_user:
                print(f"User logged in: {self.logged_user.username}")
                options: list[MenuOptions] = [
                    {
                        "message": "Exibir dados de perfil",
                        "function": self.show_profile,
                    },
                    {"message": "Criar um site", "function": self.create_site},
                    {"message": "Listar sites", "function": self.select_site},
                    {
                        "message": "Listar sites do usuário",
                        "function": self.show_user_sites,
                    },
                    {"message": "Fazer logout", "function": self.logout},
                ]

                if self.logged_user.role == UserRole.ADMIN:
                    options.extend(
                        [
                            {
                                "message": "Ver logs do sistema",
                                "function": self.show_logs,
                            },
                        ]
                    )

            else:
                options: list[MenuOptions] = [
                    {"message": "Fazer Login", "function": self.login},
                    {
                        "message": "Registrar um novo usuário",
                        "function": self.create_user,
                    },
                ]

            for i, option in enumerate(options):
                print(f"{i + 1}. {option['message']}")
            print("0. Sair")
            print(" ")

            try:
                selected_option = int(
                    input("Digite o número da opção para selecioná-la: ")
                )
            except ValueError:
                print("Opção inválida.\n")
                continue

            if selected_option == 0:
                break

            if selected_option < 0 or selected_option > len(options):
                print("Opção inválida.\n")
                continue

            os.system("clear")
            options[selected_option - 1]["function"]()

    def site_menu(self):
        if not self.logged_user or not self.selected_site:
            return

        options: list[MenuOptions] = [
            {"message": "Selecionar posts do site", "function": self.select_post},
        ]

        if self.permission_repo.has_permission(self.logged_user, self.selected_site):
            options.extend(
                [
                    {
                        "message": "Criar post no site",
                        "function": self.create_site_post,
                    },
                    {"message": "Biblioteca de Mídias", "function": self.media_menu},
                    {
                        "message": "Ver estatísticas do site",
                        "function": self.show_site_analytics,
                    },
                    {
                        "message": "Mudar template do site",
                        "function": self.configure_site_template,
                    },
                ]
            )

            if self.logged_user.username == self.selected_site.owner.username:
                options.extend(
                    [
                        {
                            "message": "Adicionar Gerente",
                            "function": self.add_manager,
                        },
                    ]
                )

        while True:
            os.system("clear")
            template = build_site_template(
                site=self.selected_site,
                post_repo=self.post_repo,
                analytics_repo=self.analytics_repo,
            )
            template.display()
            for i, option in enumerate(options):
                print(f"{i + 1}. {option['message']}")
            print("0. Voltar")
            print(" ")

            try:
                selected_option = int(
                    input("Digite o número da opção para selecioná-la: ")
                )
            except ValueError:
                print("Opção inválida.\n")
                continue

            if selected_option == 0:
                return

            if selected_option < 0 or selected_option > len(options):
                print("Opção inválida.\n")
                continue

            os.system("clear")
            options[selected_option - 1]["function"]()

    def post_menu(self):
        if not self.logged_user or not self.selected_post or not self.selected_site:
            return

        self.selected_post_language = self.selected_post.default_language

        options: list[MenuOptions] = [
            {
                "message": "Mostrar comentários do post",
                "function": self.show_post_comments,
            },
            {"message": "Comentar no post", "function": self.comment_on_post},
            {"message": "Trocar idioma do post", "function": self.change_post_language},
            {
                "message": "Sugestão de estrutura para comparilhamento em redes sociais",
                "function": self.sharing_suggestion,
            },
        ]

        if self.permission_repo.has_permission(self.logged_user, self.selected_site):
            options.extend(
                [
                    {
                        "message": "Traduzir post",
                        "function": self.translate_post,
                    },
                    {
                        "message": "Ver estatísticas do post",
                        "function": self.show_post_analytics,
                    },
                    {
                        "message": "Ver relatório de análise de SEO",
                        "function": self.show_seo_report,
                    },
                ]
            )

        while True:
            os.system("clear")
            self.selected_post.display_post(self.selected_post_language)

            print("Opções para o post ")
            for i, option in enumerate(options):
                print(f"{i + 1}. {option['message']}")
            print("0. Voltar")
            print(" ")

            try:
                selected_option = int(
                    input("Digite o número da opção para selecioná-la: ")
                )
            except ValueError:
                print("Opção inválida.\n")
                continue

            if selected_option == 0:
                return

            if selected_option < 0 or selected_option > len(options):
                print("Opção inválida.\n")
                continue

            os.system("clear")
            options[selected_option - 1]["function"]()

    def media_menu(self):
        if not self.logged_user or not self.selected_site:
            return

        if not self.permission_repo.has_permission(
            self.logged_user, self.selected_site
        ):
            return

        options: list[MenuOptions] = [
            {"message": "Importar nova mídia", "function": self.import_media},
            {"message": "Listar mídias", "function": self.select_media},
        ]

        while True:
            os.system("clear")
            print(f"Biblioteca de mídias do site '{self.selected_site.name}'")
            for i, option in enumerate(options):
                print(f"{i + 1}. {option['message']}")
            print("0. Voltar")
            print(" ")

            try:
                selected_option = int(
                    input("Digite o número da opção para selecioná-la: ")
                )
            except ValueError:
                print("Opção inválida.\n")
                continue

            if selected_option == 0:
                return

            if selected_option < 0 or selected_option > len(options):
                print("Opção inválida.\n")
                continue

            os.system("clear")
            options[selected_option - 1]["function"]()

    def create_user(self):
        first_name = input("Digite seu primeiro nome: ")
        last_name = input("Digite seu último nome: ")
        email = input("Digite seu email: ")
        username = input("Digite um username: ")
        password = input("Digite uma senha: ")

        user = User(first_name, last_name, email, username, password, UserRole.USER)
        self.user_repo.add_user(user)

        input("Usuário Criado! Clique Enter para voltar ao menu.")

    def login(self):
        while True:
            username = input("Username: ")
            password = input("Senha: ")

            try:
                user = self.user_repo.validate_user(username, password)
                break
            except ValueError:
                os.system("clear")
                print("Credenciais Inválidas!\n")

        self.logged_user = user

    def logout(self):
        self.logged_user = None

    def show_logs(self):
        try:
            os.system("clear")
            limit = int(
                input("Insira a quantidade de logs que deseja ver (ou 0 para voltar): ")
            )

            if limit == 0:
                return

            self.analytics_repo.show_logs(limit=limit)

        except ValueError:
            print("Valor inválido.")

        print(" ")
        input("Clique Enter para voltar ao menu.")

    def show_profile(self):
        if self.logged_user:
            print(f"Nome: {self.logged_user.first_name} {self.logged_user.last_name}")
            print(f"E-mail: {self.logged_user.email}")
            print(f"Role: {self.logged_user.role}")

        print(" ")
        input("Clique Enter para voltar ao Menu.")

    def create_site(self):
        if not self.logged_user:
            print("Usuário não está logado.")
            return

        site_name = input("Diga o nome do seu site: ")
        description = input("Informe uma descrição breve para o site: ")
        site = Site(owner=self.logged_user, name=site_name, description=description)
        self.site_repo.add_site(site)
        permission = Permission(user=self.logged_user, site=site)
        self.permission_repo.grant_permission(permission)

        input("Site criado. Clique Enter para voltar ao menu.")

    def show_user_sites(self):
        if not self.logged_user:
            return

        user_sites: list[Site] = self.site_repo.get_user_sites(self.logged_user)
        for i, site in enumerate(user_sites):
            print(f"{i + 1}. {site.name}")

        print(" ")
        input("Clique Enter para voltar ao Menu.")

    def select_site(self):
        if not self.logged_user:
            return

        sites: list[Site] = self.site_repo.get_sites()
        for i, site in enumerate(sites):
            print(f"{i + 1}. {site.name}")
        print("0. Voltar")
        print(" ")

        while True:
            try:
                selected_option = int(
                    input("Digite o número do site para selecioná-lo: ")
                )
            except ValueError:
                print("Opção inválida.\n")
                continue

            if selected_option == 0:
                return

            if selected_option < 0 or selected_option > len(sites):
                print("Opção inválida.\n")
                continue

            self.selected_site = sites[selected_option - 1]
            break

        self.analytics_repo.log(
            SiteAnalyticsEntry(
                user=self.logged_user, site=self.selected_site, action=SiteAction.ACCESS
            )
        )
        self.site_menu()
        self.selected_site = None

    def create_site_post(self):
        if not self.selected_site or not self.logged_user:
            return

        pb = PostBuilder(self.selected_site, self.logged_user, self.media_repo)
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
            self.post_repo.add_post(post)
            self.analytics_repo.log(
                SiteAnalyticsEntry(
                    user=self.logged_user,
                    site=self.selected_site,
                    action=SiteAction.CREATE_POST,
                )
            )

            print(" ")
            input("Post criado. Clique Enter para voltar ao menu.")

    def add_manager(self):
        if not self.logged_user or not self.selected_site:
            return

        print("Selecione um usuário para ser gerente da página:")
        users = self.permission_repo.get_not_managers(
            self.selected_site, self.user_repo
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
                self.permission_repo.grant_permission(
                    Permission(user=user, site=self.selected_site)
                )

        print(" ")
        input("Clique Enter para voltar ao menu.")

    def show_site_analytics(self):
        if not self.selected_site:
            return

        site = self.selected_site

        accesses = self.analytics_repo.get_site_accesses(site.id)
        post_creations = self.analytics_repo.get_site_post_creation_count(site.id)
        media_uploads = self.analytics_repo.get_site_media_upload_count(site.id)

        total_views = self.analytics_repo.get_site_total_post_views(site.id)
        total_comments = self.analytics_repo.get_site_total_post_comments(site.id)
        total_shares = self.analytics_repo.get_site_total_post_shares(site.id)

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

    def configure_site_template(self):
        if not self.selected_site:
            return
        new_template = select_enum(
            SiteTemplateType, "Escolha o layout de apresentação do site:"
        )
        if new_template:
            self.selected_site.template = new_template
            print(f"Template atualizado para: {new_template.value}.", end=" ")
        else:
            print("Opção inválida.", end=" ")

        input("Clique enter para voltar ao menu.")

    def select_post(self):
        if not self.selected_site or not self.logged_user:
            return

        posts: list[Post] = self.post_repo.get_site_posts(self.selected_site)
        for i, post in enumerate(posts):
            print(f"{i + 1}. {post.get_default_title()}")
        print("0. Voltar")
        print(" ")

        while True:
            try:
                selected_option = int(
                    input("Digite o número do site para selecioná-lo: ")
                )
            except ValueError:
                print("Opção inválida.\n")
                continue

            if selected_option == 0:
                return

            if selected_option < 0 or selected_option > len(posts):
                print("Opção inválida.\n")
                continue

            self.selected_post = posts[selected_option - 1]
            break

        self.analytics_repo.log(
            PostAnalyticsEntry(
                user=self.logged_user,
                site=self.selected_site,
                post=self.selected_post,
                action=PostAction.VIEW,
            )
        )
        self.post_menu()
        self.selected_post = None

    def comment_on_post(self):
        if not self.selected_site or not self.selected_post or not self.logged_user:
            return

        body = input("Digite seu comentário: ")

        comment = Comment(
            post=self.selected_post, commenter=self.logged_user, body=body
        )
        self.comment_repo.add_comment(comment)

        self.analytics_repo.log(
            PostAnalyticsEntry(
                user=self.logged_user,
                site=self.selected_site,
                post=self.selected_post,
                action=PostAction.COMMENT,
                metadata={"comment_id": str(comment.id)},
            )
        )

    def show_post_analytics(self):
        if not self.selected_post:
            return

        views = self.analytics_repo.get_post_views(self.selected_post.id)
        shares = self.analytics_repo.get_post_shares(self.selected_post.id)
        comments = self.analytics_repo.get_post_comments(self.selected_post.id)

        self.selected_post.display_post_short()

        print(f"Visualizações: {views}")
        print(f"Comentários: {comments}")
        print(f"Compartilhamentos: {shares}")

        print(" ")
        input("Clique Enter para voltar ao Menu.")

    def show_post_comments(self):
        if not self.selected_post:
            return

        post_comments: list[Comment] = self.comment_repo.get_post_comments(
            self.selected_post
        )

        for comment in post_comments:
            print(comment.body)
            print(f"{comment.commenter.username} @ {comment.created_at}")
            print(" ")

        print(" ")
        input("Clique Enter para voltar ao Menu.")

    def translate_post(self):
        if not self.selected_post:
            return

        pt = PostTranslator(self.selected_post)
        pt.translate()

    def change_post_language(self):
        if not self.selected_post:
            return

        languages = self.selected_post.get_languages()
        if len(languages) == 1:
            os.system("clear")
            input(
                f"O Post só tem uma linguagem: {languages[0]}. Clique enter para voltar."
            )
            return

        self.selected_post_language = select_language(languages)

    def show_seo_report(self):
        if not self.selected_post:
            return

        languages = self.selected_post.get_languages()
        if len(languages) == 1:
            language = languages[0]
        else:
            language = select_language(languages)
            if not language:
                return

        display_seo_report(self.selected_post, language)

        input("Clique Enter para voltar ao menu.")

    def sharing_suggestion(self):
        if not self.selected_post or not self.logged_user or not self.selected_site:
            return

        print("Esta ferramenta te ajuda a estruturar seu Post para")
        print("compartilhamento em redes sociais.")

        print("\nPara obter sugestões, escolha o idioma do Post e a rede social.")
        languages = self.selected_post.get_languages()
        if len(languages) == 1:
            language = languages[0]
        else:
            language = select_language(languages)
            if not language:
                input(
                    "Não é possível continuar sem escolher um idioma. "
                    "Clique Enter para voltar"
                )
                return

        print(" ")

        social_media = select_enum(SocialMedia, "Selecione uma rede social: ")
        if not social_media:
            input(
                "Não é possível continuar sem escolher uma Rede Social. "
                "Clique Enter para voltar"
            )
            return

        os.system("clear")

        print(f"Post: {self.selected_post.get_default_title()}")
        print(f"Idioma: {language}")
        print(f"Rede Social: {social_media}")

        social_post = build_social_media_post(
            social_media, self.selected_post, language
        )
        social_post.display_sharing_suggestion()

        input("\nRecomendação finalizada. Clique Enter para voltar.")

    def share_post(self):
        if not self.selected_post or not self.logged_user or not self.selected_site:
            return

        print("Preview do post para Rede Social:")
        print(" ")
        print(self.selected_post.format_post_to_social_network())
        print(" ")

        print("Selecione as redes sociais para compartilhar:")

        for i, network in enumerate(SocialMedia):
            print(f"{i + 1}. {network.value}")
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

            if n < 0 or n > len(SocialMedia):
                print("Opção inválida.\n")
                continue

            if 1 <= n <= len(SocialMedia):
                network = list(SocialMedia)[n - 1]
                print(f"Post compartilhado em {network.value}.")
                self.analytics_repo.log(
                    PostAnalyticsEntry(
                        user=self.logged_user,
                        site=self.selected_site,
                        post=self.selected_post,
                        action=PostAction.SHARE,
                        metadata={"shared_to": network.value},
                    )
                )

        print(" ")
        input("Clique Enter para voltar ao menu.")

    def media_detail_menu(self):
        if not self.selected_media:
            return

        options: list[MenuOptions] = [
            {"message": "Deletar mídia", "function": self.delete_selected_media},
        ]

        while True:
            os.system("clear")
            media = self.selected_media
            print(f"Informações da mídia '{media.filename}':")
            print(f"ID: {media.id}")
            print(f"Tipo: {media.media_type.name}")
            print(f"Caminho: {media.path}")
            print(" ")

            for i, option in enumerate(options):
                print(f"{i + 1}. {option['message']}")
            print("0. Voltar")
            print(" ")

            try:
                selected_option = int(
                    input("Digite o número da opção para selecioná-la: ")
                )
            except ValueError:
                print("Opção inválida.\n")
                continue

            if selected_option == 0:
                return

            if selected_option < 0 or selected_option > len(options):
                print("Opção inválida.\n")
                continue

            os.system("clear")
            options[selected_option - 1]["function"]()

            if not self.selected_media:
                return

    def import_media(self):
        if not self.selected_site or not self.logged_user:
            return

        filepath = input(
            "Digite o caminho completo do arquivo de mídia a ser importado:\n> "
        ).strip()

        if not filepath:
            print("Nenhum caminho informado.")
            input("Clique Enter para voltar.")
            return

        path = Path(filepath)

        if not path.exists():
            print("Arquivo não encontrado. Verifique o caminho digitado.")
            input("Clique Enter para voltar.")
            return

        path = Path(filepath)
        filename = path.name

        try:
            media_type = infer_media_type(path.suffix)

            media = MediaFile(
                uploader=self.logged_user,
                filename=filename,
                path=path,
                media_type=media_type,
                site=self.selected_site,
                width="1000",
                height="1000",
                duration=None,
            )

            media_id = self.media_repo.add_midia(media)
            print(f"Mídia importada com id {media_id}.")

            self.analytics_repo.log(
                SiteAnalyticsEntry(
                    user=self.logged_user,
                    site=self.selected_site,
                    action=SiteAction.UPLOAD_MEDIA,
                )
            )

            input("Clique Enter para voltar ao menu.")
        except ValueError:
            print("Arquivo não suportado.")
            input("Clique Enter para voltar ao menu e tentar novamente.")

    def select_media(self):
        if not self.selected_site:
            return

        medias: list[MediaFile] = self.media_repo.get_site_medias(self.selected_site)

        if not medias:
            print("Nenhuma mídia encontrada para este site.")
            input("Clique Enter para voltar ao menu.")
            return

        while True:
            os.system("clear")
            print(f"Mídias do site '{self.selected_site.name}':")
            for i, media in enumerate(medias):
                print(f"{i + 1}. {media.filename}")
            print("0. Voltar")
            print(" ")

            try:
                selected_option = int(
                    input("Digite o número da mídia para selecioná-la: ")
                )
            except ValueError:
                print("Opção inválida.\n")
                continue

            if selected_option == 0:
                return

            if selected_option < 0 or selected_option > len(medias):
                print("Opção inválida.\n")
                continue

            self.selected_media = medias[selected_option - 1]
            break

        self.media_detail_menu()
        self.selected_media = None

    def delete_selected_media(self):
        if not self.selected_media:
            return

        confirm = (
            input(
                f"Tem certeza que deseja deletar a mídia '{self.selected_media.filename}'? (y/n): "
            )
            .strip()
            .lower()
        )
        if confirm == "y":
            self.media_repo.remove_media(self.selected_media.id)
            print("Mídia deletada.")
            input("Clique Enter para voltar ao menu.")
            self.selected_media = None
            return
        else:
            print("Operação cancelada.")
            input("Clique Enter para voltar ao menu.")

    def _populate(self):
        admin = User(
            first_name="Admin",
            last_name="Admin",
            email="admin@admin.com",
            username="admin",
            password="Admin123",
            role=UserRole.ADMIN,
        )
        self.user_repo.add_user(admin)
        user1 = User(
            first_name="User1",
            last_name="User1",
            email="user1@user.com",
            username="user1",
            password="User123",
            role=UserRole.USER,
        )
        self.user_repo.add_user(user1)
        user2 = User(
            first_name="User2",
            last_name="User2",
            email="user2@user.com",
            username="user2",
            password="User123",
            role=UserRole.USER,
        )
        self.user_repo.add_user(user2)
        site = Site(
            owner=admin, name="Meu blog", description="Meus pensamentos e dia-a-dia."
        )
        self.site_repo.add_site(site)
        self.permission_repo.grant_permission(Permission(user=admin, site=site))
        self._populate_medias(admin, site)
        post1 = Post(
            poster=admin,
            site=site,
            content_by_language={
                "pt-br": Content(
                    title="Título do meu post",
                    language=get_language_by_code("br"),
                    body=[
                        TextBlock(
                            order=1,
                            text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
                        ),
                        MediaBlock(
                            order=2,
                            alt="Uma imagem.",
                            media=self.media_repo.get_media_by_id(1),
                        ),
                        TextBlock(
                            order=3,
                            text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
                        ),
                    ],
                ),
                "en-us": Content(
                    title="Super duper title of doom",
                    language=get_language_by_code("en"),
                    body=[
                        TextBlock(
                            order=1,
                            text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
                        ),
                        MediaBlock(
                            order=2,
                            alt="Some Imagee.",
                            media=self.media_repo.get_media_by_id(1),
                        ),
                        TextBlock(
                            order=3,
                            text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
                        ),
                    ],
                ),
            },
        )
        post2 = Post(
            poster=admin,
            site=site,
            content_by_language={
                "en-us": Content(
                    title="Title of my post",
                    language=get_language_by_code("en"),
                    body=[
                        TextBlock(
                            order=1,
                            text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
                        ),
                        MediaBlock(
                            order=2,
                            alt="Some video",
                            media=self.media_repo.get_media_by_id(5),
                        ),
                        TextBlock(
                            order=3,
                            text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
                        ),
                    ],
                )
            },
        )
        self.post_repo.add_post(post1)
        self.post_repo.add_post(post2)
        self.analytics_repo.log(
            SiteAnalyticsEntry(
                user=admin,
                site=site,
                action=SiteAction.CREATE_POST,
                metadata={"post_id": str(post1.id)},
            )
        )
        self.analytics_repo.log(
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
        self.comment_repo.add_comment(comment1_post1)
        self.comment_repo.add_comment(comment2_post1)
        self.comment_repo.add_comment(comment3_post1)
        self.analytics_repo.log(
            PostAnalyticsEntry(
                user=user1,
                site=site,
                post=post1,
                action=PostAction.VIEW,
            )
        )
        self.analytics_repo.log(
            PostAnalyticsEntry(
                user=user1,
                site=site,
                post=post1,
                action=PostAction.COMMENT,
                metadata={"comment_id": str(comment1_post1.id)},
            )
        )
        self.analytics_repo.log(
            PostAnalyticsEntry(
                user=user2,
                site=site,
                post=post1,
                action=PostAction.VIEW,
            )
        )
        self.analytics_repo.log(
            PostAnalyticsEntry(
                user=user2,
                site=site,
                post=post1,
                action=PostAction.COMMENT,
                metadata={"comment_id": str(comment2_post1.id)},
            )
        )
        self.analytics_repo.log(
            PostAnalyticsEntry(
                user=user2,
                site=site,
                post=post1,
                action=PostAction.VIEW,
            )
        )
        self.analytics_repo.log(
            PostAnalyticsEntry(
                user=user2,
                site=site,
                post=post1,
                action=PostAction.COMMENT,
                metadata={"comment_id": str(comment3_post1.id)},
            )
        )

    def _populate_medias(self, uploader: User, selected_site: Site):
        folder = Path("static")
        for filepath in folder.rglob("*"):
            if filepath.is_file():
                filepath = filepath.resolve()
                media_type = infer_media_type(filepath.suffix)

                self.media_repo.add_midia(
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

                self.analytics_repo.log(
                    SiteAnalyticsEntry(
                        user=uploader,
                        site=selected_site,
                        action=SiteAction.UPLOAD_MEDIA,
                    )
                )
