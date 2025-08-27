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
