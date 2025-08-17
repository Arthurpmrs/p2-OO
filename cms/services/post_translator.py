from cms.models import Language, MediaBlock, Post, ContentBlock, Content, TextBlock


class PostTranslator:
    def __init__(self, post: Post):
        self.post = post
        self.original_language = post.default_language

    def translate(self):
        target_language = input(
            "Para qual idioma você deseja traduzir este post? "
        ).strip()

        if target_language in self.post.content_by_language:
            overwrite = (
                input(
                    f"O post já possui tradução para '{target_language}'. Deseja sobrescrever? (s/n): "
                )
                .strip()
                .lower()
            )
            if overwrite != "s":
                print("Tradução cancelada.")
                return

        original_content, _ = self.post.get_content_by_language()
        translated_blocks: list[ContentBlock] = []

        print(
            f"Traduzindo post '{original_content.title}' do idioma {self.original_language} para {target_language}.\n"
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
            language=Language(name=target_language, codes=[target_language]),
        )

        self.post.content_by_language[target_language] = translated_content
        print(f"Tradução para '{target_language}' adicionada ao post.")
        input("Clique Enter para voltar.")
