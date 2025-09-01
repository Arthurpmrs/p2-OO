from cms.models import MediaBlock, Post, ContentBlock, Content, TextBlock
from cms.services.languages import LanguageService


class PostTranslator:
    def __init__(self, post: Post):
        self.__post = post
        self.__original_language = post.default_language
        self.__lang_service = LanguageService()

    def translate(self):
        missing_langs = self.__lang_service.get_missing_languages(self.__post)
        target_language = self.__lang_service.select_language(missing_langs)

        if not target_language:
            return

        original_content = self.__post.get_content_by_language()
        translated_blocks: list[ContentBlock] = []

        print(
            f"Traduzindo post '{original_content.title}' do idioma {self.__original_language} para {target_language}.\n"
        )

        translated_title = input("Tradução do título: ").strip()

        for block in original_content.body:
            if isinstance(block, TextBlock):
                print(f"Texto original:\n{block.text}")
                translated_text = input("Tradução: ").strip()
                translated_block = TextBlock(
                    order=block.order,
                    text=translated_text,
                )
            elif isinstance(block, MediaBlock):
                print(f"Mídia: {block.media.filename} ({block.media.media_type.name})")
                print(f"Texto alternativo original: {block.alt}")
                translated_alt = input("Tradução do texto alternativo (alt): ").strip()
                translated_block = MediaBlock(
                    order=block.order,
                    media=block.media,
                    alt=translated_alt,
                )
            else:
                print(f"Tipo de bloco não suportado para tradução: {type(block)}")
                continue

            translated_blocks.append(translated_block)

        translated_content = Content(
            title=translated_title,
            body=translated_blocks,
            language=target_language,
        )

        self.__post.add_content(target_language.code, translated_content)
        print(f"Tradução para '{target_language}' adicionada ao post.")
        input("Clique Enter para voltar.")
