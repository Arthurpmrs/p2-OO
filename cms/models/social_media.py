from enum import Enum
import re
from dataclasses import dataclass
from abc import ABC, abstractmethod

from . import (
    Post,
    Language,
    Content,
    LanguageCode,
    TextBlock,
    MediaBlock,
    CaroulselBlock,
    MediaType,
)


class SocialMedia(Enum):
    TWITTER = "Twitter"
    FACEBOOK = "Facebook"
    INSTAGRAM = "Instagram"


@dataclass
class SocialMediaPost(ABC):
    original_post: Post
    language: Language | None = None

    @abstractmethod
    def get_suggested_text(self) -> str:
        pass

    @abstractmethod
    def get_character_limit(self) -> int:
        pass

    @abstractmethod
    def get_max_media_count(self) -> int:
        pass

    @abstractmethod
    def get_media_recommendation(self) -> str:
        pass

    def _get_post_content(self) -> tuple[Content, LanguageCode]:
        return self.original_post.get_content_by_language(self.language)

    def _extract_text_blocks(self) -> list[str]:
        content, _ = self._get_post_content()
        text_blocks: list[str] = []

        for block in content.body:
            if isinstance(block, TextBlock):
                text_blocks.append(block.text)

        return text_blocks

    def _extract_media_blocks(self) -> list[MediaBlock]:
        content, _ = self._get_post_content()
        media_blocks: list[MediaBlock] = []

        for block in content.body:
            if isinstance(block, MediaBlock):
                media_blocks.append(block)
            elif isinstance(block, CaroulselBlock):
                for media in block.medias:
                    media_blocks.append(
                        MediaBlock(order=block.order, media=media, alt=block.alt)
                    )

        return media_blocks

    def _get_hash_tags_from_title(self) -> list[str]:
        tags: list[str] = []

        title_words = self.original_post.get_default_title().lower().split()
        for word in title_words[:3]:
            clean_word = re.sub(r"[^a-zA-Z0-9]", "", word)
            if len(clean_word) > 2:
                tags.append(f"#{clean_word}")

        return tags

    def get_media_summary(self) -> str:
        media_blocks = self._extract_media_blocks()

        if not media_blocks:
            return "❌ Nenhuma mídia disponível para esta rede social."

        summary = f"📎 {len(media_blocks)} mídia(s) disponível(is) para anexar:\n"
        for i, media_block in enumerate(media_blocks):
            media = media_block.media
            summary += f"   {i + 1}. {media.media_type}: {media.filename}\n"
            summary += f"      URL: {media.url}\n"
            if media.media_type == MediaType.VIDEO:
                summary += f"      Duração: {media.duration}\n"
            summary += (
                f"      Dimensões: {media.dimension} | Alt: {media_block.alt}\n\n"
            )

        return summary

    def display_sharing_suggestion(self):
        print(f"\n{'=' * 60}")
        print(
            f"📱 SUGESTÃO DE COMPARTILHAMENTO - {self.__class__.__name__.replace('Post', '').upper()}"
        )
        print(f"{'=' * 60}")

        suggested_text = self.get_suggested_text()
        print("\n📝 TEXTO SUGERIDO PARA COPIAR/COLAR:")
        print("─" * 40)
        print(suggested_text)
        print("─" * 40)
        print(f"📊 Caracteres: {len(suggested_text)}/{self.get_character_limit()}")

        print("\n📋 INFORMAÇÕES DA PLATAFORMA:")
        print(f"   • Limite de caracteres: {self.get_character_limit()}")
        print(f"   • Máximo de mídias: {self.get_max_media_count()}")

        print(f"\n{self.get_media_summary()}")

        print(f"💡 DICAS PARA {self.__class__.__name__.replace('Post', '').upper()}:")
        print(f"   {self.get_media_recommendation()}")

        print(f"\n{'=' * 60}")


@dataclass
class FacebookPost(SocialMediaPost):
    def get_character_limit(self) -> int:
        return 63206

    def get_max_media_count(self) -> int:
        return 10

    def get_suggested_text(self) -> str:
        content, lang_code = self._get_post_content()

        suggested_text = f"📢 {content.title}\n\n"
        suggested_text += self._get_text_content_to_display()
        suggested_text += f"✍️ Por: {self.original_post.poster.first_name} {self.original_post.poster.last_name}\n"
        suggested_text += (
            f"🔗 Leia o artigo completo em: {self.original_post.site.get_url()}\n\n"
        )
        suggested_text += (
            f"#{self.original_post.site.name.replace(' ', '').replace('-', '')} "
        )
        suggested_text += f"#blog #conteúdo #{lang_code}"

        return suggested_text

    def _get_text_content_to_display(self) -> str:
        text_blocks = self._extract_text_blocks()

        content = ""
        for text in text_blocks:
            content += f"{text}\n\n"

        return content[: self.get_character_limit()]

    def get_media_recommendation(self) -> str:
        return (
            "Facebook: Use imagens em alta resolução (1200x630px recomendado). "
            "Suporta múltiplas imagens, vídeos até 240min, carrosséis até 10 itens."
        )


@dataclass
class InstagramPost(SocialMediaPost):
    def get_character_limit(self) -> int:
        return 2200

    def get_max_media_count(self) -> int:
        return 10

    def get_suggested_text(self) -> str:
        content, lang_code = self._get_post_content()

        suggested_text = f"{content.title} ✨\n\n"

        text_blocks = self._extract_text_blocks()
        if text_blocks:
            first_text = text_blocks[0]
            if len(first_text) > 300:
                first_text = first_text[:297] + "..."
            suggested_text += f"{first_text}\n\n"

        suggested_text += "🔗 Link na bio para ler completo\n\n"

        hashtags = self._generate_instagram_hashtags(lang_code)
        suggested_text += hashtags

        return suggested_text[: self.get_character_limit()]

    def _generate_instagram_hashtags(self, lang_code: str) -> str:
        base_tags = [
            f"#{self.original_post.site.name.replace(' ', '').replace('-', '')}",
            "#blog",
            "#conteudo",
            "#inspiracao",
            "#dicasdodia",
            "#lifestyle",
            "#motivacao",
            "#criatividade",
            f"#{lang_code}",
            "#post",
            "#novidades",
        ]
        base_tags.extend(self._get_hash_tags_from_title())
        return " ".join(base_tags)

    def get_media_recommendation(self) -> str:
        return (
            "Instagram: Use formato quadrado (1080x1080px) ou vertical (1080x1350px). "
            "Carrossel até 10 itens, vídeos até 60s no feed, stories 15s."
        )


@dataclass
class TwitterPost(SocialMediaPost):
    def get_character_limit(self) -> int:
        return 280

    def get_max_media_count(self) -> int:
        return 4

    def get_suggested_text(self) -> str:
        content, lang_code = self._get_post_content()

        available_chars = self.get_character_limit()

        link = f" {self.original_post.site.get_url()}"
        hashtags = f" #{self.original_post.site.name.replace(' ', '').replace('-', '')} #{lang_code}"
        reserved_chars = len(link) + len(hashtags) + 10

        title_and_text_limit = available_chars - reserved_chars

        main_text = self._get_text_content_limit(content, title_and_text_limit)
        suggested_text = main_text + hashtags + link

        return suggested_text

    def _get_text_content_limit(self, content: Content, limit: int) -> str:
        main_text = content.title
        text_blocks = self._extract_text_blocks()
        if text_blocks and len(main_text) < limit - 50:
            first_text = text_blocks[0][:100]
            main_text += f"\n\n{first_text}"

        if len(main_text) > limit:
            main_text = main_text[: limit - 3] + "..."

        return main_text

    def get_media_recommendation(self) -> str:
        return (
            "Twitter: Imagens 1200x675px, até 4 imagens por tweet, "
            "vídeos até 2min20s, GIFs até 15MB."
        )
