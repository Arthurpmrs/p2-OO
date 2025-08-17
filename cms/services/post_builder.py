from datetime import datetime

from cms.utils import read_datetime_from_cli
from cms.models import (
    Language,
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
        self.site = site
        self.poster = poster
        self.media_repo = media_repo
        self.blocks: list[ContentBlock] = []

    def build_post(self) -> Post:
        language = input("Qual o idioma do post? (ex: pt, en): ").strip()
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
                self.blocks.append(block)
            elif block_option == 2:
                media = self.select_media()
                if not media:
                    continue
                alt = input("Digite o texto alternativo (alt) para a mídia: ")
                block = MediaBlock(order=order_counter, media=media, alt=alt)
                self.blocks.append(block)
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
            body=self.blocks,
            language=Language(name=language, codes=[language]),
        )

        post = Post(
            poster=self.poster,
            site=self.site,
            content_by_language={language: post_content},
            scheduled_to=scheduled_to,
        )

        return post

    def select_media(self) -> MediaFile | None:
        medias = self.media_repo.get_site_medias(self.site)

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
