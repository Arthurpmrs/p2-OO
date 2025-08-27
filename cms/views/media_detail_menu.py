from cms.models import MediaFile, User
from cms.views.menu import AbstractMenu, AppContext, MenuOptions


class MediaMenu(AbstractMenu):
    context: AppContext
    logged_user: User
    selected_media: MediaFile

    def __init__(self, context: AppContext, selected_media: MediaFile):
        self.context = context
        self.selected_media = selected_media

    def show(self):
        if not self.selected_media:
            return

        options: list[MenuOptions] = [
            {"message": "Deletar mídia", "function": self._delete_selected_media},
        ]

        def display_title():
            media = self.selected_media
            print(f"Informações da mídia '{media.filename}':")
            print(f"ID: {media.id}")
            print(f"Tipo: {media.media_type.name}")
            print(f"Caminho: {media.path}")
            print(" ")

        MediaMenu.prompt_menu_option(options, display_title)

        # while True:
        #     os.system("clear")
        #     media = self.selected_media
        #     print(f"Informações da mídia '{media.filename}':")
        #     print(f"ID: {media.id}")
        #     print(f"Tipo: {media.media_type.name}")
        #     print(f"Caminho: {media.path}")
        #     print(" ")

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

    def _delete_selected_media(self):
        confirm = (
            input(
                f"Tem certeza que deseja deletar a mídia '{self.selected_media.filename}'? (y/n): "
            )
            .strip()
            .lower()
        )
        if confirm == "y":
            self.context.media_repo.remove_media(self.selected_media.id)
            print("Mídia deletada.")
            input("Clique Enter para voltar ao menu.")
        else:
            print("Operação cancelada.")
            input("Clique Enter para voltar ao menu.")
