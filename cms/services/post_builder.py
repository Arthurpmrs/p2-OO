from datetime import datetime

from cms.utils import read_datetime_from_cli
from cms.services.languages import LanguageService
from cms.models import (
    Site,
    User,
    MediaFile,
    ContentBlock,
    TextBlock,
    MediaBlock,
    Post,
    Content,
)
from cms.repository import MediaRepository


class PostBuilder:
    def __init__(self, site: Site, poster: User, media_repo: MediaRepository):
        self.__site = site
        self.__poster = poster
        self.__media_repo = media_repo
        self.__blocks: list[ContentBlock] = []
        self.__lang_service = LanguageService()

    def build_post(self) -> Post:
        language = self.__lang_service.select_from_supported_languages()
        if not language:
            raise ValueError("Cannot continue post building without language")

        title = input("Digite o título do post: ").strip()

        order_counter = 1

        while True:
            print("Selecione o tipo de conteúdo que deseja inserir:")
            print("1. Texto")
            print("2. Mídia")
            print("0. Finalizar criação do post")
            try:
                block_option = int(input("Opção: "))
            except ValueError:
                print("Opção inválida.")
                continue

            if block_option == 0:
                break
            elif block_option == 1:
                text = input("Digite o conteúdo de texto: ")
                block = TextBlock(order=order_counter, text=text)
                self.__blocks.append(block)
            elif block_option == 2:
                media = self.select_media()
                if not media:
                    continue
                alt = input("Digite o texto alternativo (alt) para a mídia: ")
                block = MediaBlock(order=order_counter, media=media, alt=alt)
                self.__blocks.append(block)
            else:
                print("Opção inválida.")

            order_counter += 1

        is_scheduled = input("Deseja agendar o post? (y/n): ").strip().lower()
        if is_scheduled == "y":
            scheduled_to = read_datetime_from_cli()
        else:
            scheduled_to = datetime.now()

        post_content = Content(
            title=title,
            body=self.__blocks,
            language=language,
        )

        post = Post(
            poster=self.__poster,
            site=self.__site,
            scheduled_to=scheduled_to,
        )
        post.add_content(language.code, post_content)

        return post

    def select_media(self) -> MediaFile | None:
        medias = self.__media_repo.get_site_medias(self.__site)

        if not medias:
            input("Nenhuma mídia disponível para este site. Clique Enter para voltar.")
            return None

        while True:
            print("Selecione a mídia:")
            for i, media in enumerate(medias):
                print(f"{i + 1}. {media.filename} ({media.media_type.name})")
            print("0. Cancelar")
            try:
                selected_option = int(input("Opção: "))
            except ValueError:
                print("Opção inválida.\n")
                continue

            if selected_option == 0:
                return None

            if selected_option < 0 or selected_option > len(medias):
                print("Opção inválida.\n")
                continue

            return medias[selected_option - 1]
