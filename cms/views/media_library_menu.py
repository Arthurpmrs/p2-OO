from pathlib import Path
from cms.models import MediaFile, Site, SiteAction, SiteAnalyticsEntry, User
from cms.utils import infer_media_type
from cms.views.media_detail_menu import MediaMenu
from cms.views.menu import AbstractMenu, AppContext, MenuOptions


class MediaLibraryMenu(AbstractMenu):
    context: AppContext
    logged_user: User
    selected_site: Site

    def __init__(self, context: AppContext, logged_user: User, selected_site: Site):
        self.context = context
        self.logged_user = logged_user
        self.selected_site = selected_site

    def show(self):
        if not self.context.permission_repo.has_permission(
            self.logged_user, self.selected_site
        ):
            return

        options: list[MenuOptions] = [
            {"message": "Importar nova mídia", "function": self._import_media},
            {"message": "Listar mídias", "function": self._select_media},
        ]

        MediaLibraryMenu.prompt_menu_option(
            options,
            lambda: print(f"Biblioteca de mídias do site {self.selected_site.name}\n"),
        )
        # while True:
        #     os.system("clear")
        #     print(f"Biblioteca de mídias do site '{self.selected_site.name}'")
        #     for i, option in enumerate(options):
        #         print(f"{i + 1}. {option['message']}")
        #     print("0. Voltar")
        #     print(" ")

        #     try:
        #         selected_option = int(
        #             input("Digite o número da opção para selecioná-la: ")
        #         )
        #     except ValueError:
        #         print("Opção inválida.\n")
        #         continue

        #     if selected_option == 0:
        #         return

        #     if selected_option < 0 or selected_option > len(options):
        #         print("Opção inválida.\n")
        #         continue

        #     os.system("clear")
        #     options[selected_option - 1]["function"]()

    def _import_media(self):
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

            media_id = self.context.media_repo.add_midia(media)
            print(f"Mídia importada com id {media_id}.")

            self.context.analytics_repo.log(
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

    def _select_media(self):
        medias: list[MediaFile] = self.context.media_repo.get_site_medias(
            self.selected_site
        )

        if not medias:
            print("Nenhuma mídia encontrada para este site.")
            input("Clique Enter para voltar ao menu.")
            return

        def execute_for_option(selected_media: MediaFile):
            MediaMenu(self.context, selected_media).show()

        MediaLibraryMenu.prompt_generic(
            medias,
            f"Mídias do site {self.selected_site.name}\n",
            execute_for_option,
            lambda m: m.filename,
        )

        # while True:
        #     os.system("clear")
        #     print(f"Mídias do site '{self.selected_site.name}':")
        #     for i, media in enumerate(medias):
        #         print(f"{i + 1}. {media.filename}")
        #     print("0. Voltar")
        #     print(" ")

        #     try:
        #         selected_option = int(
        #             input("Digite o número da mídia para selecioná-la: ")
        #         )
        #     except ValueError:
        #         print("Opção inválida.\n")
        #         continue

        #     if selected_option == 0:
        #         return

        #     if selected_option < 0 or selected_option > len(medias):
        #         print("Opção inválida.\n")
        #         continue

        #     selected_media = medias[selected_option - 1]
        #     MediaMenu(self.context, selected_media).show()
