from datetime import datetime
from enum import Enum
from typing import Type, TypeVar

from cms.models import MediaType, Language, LanguageCode, Post


def read_datetime_from_cli() -> datetime:
    while True:
        date_str = input(
            "Digite a data que o post deve estar disponível (YYYY-MM-DD): "
        )
        time_str = input("Digite a hora que o post deve estar disponível (HH:MM): ")

        try:
            combined_str = f"{date_str} {time_str}"
            scheduled_datetime = datetime.strptime(combined_str, "%Y-%m-%d %H:%M")
            return scheduled_datetime
        except ValueError:
            print("Formato de data ou hora inválido. Tente novamente.\n")


def infer_media_type(extension: str) -> MediaType:
    ext = extension.lower()
    if ext in [".jpg", ".jpeg", ".png", ".gif", "webp"]:
        return MediaType.IMAGE
    elif ext in [".mp4", ".mov", ".avi"]:
        return MediaType.VIDEO
    else:
        raise ValueError("Tipo do arquivo de mídia não é suportado.")


supported_languages = [
    Language(name="Português Brasileiro", code="pt-br", aliases=["ptbr", "pt", "br"]),
    Language(name="Inglês", code="en-us", aliases=["en-us", "enus", "en", "us"]),
    Language(name="Espanhol", code="es"),
    Language(name="Chinês", code="zh"),
    Language(name="Japonês", code="ja"),
]


def get_language_by_code(code: LanguageCode) -> Language:
    for lang in supported_languages:
        if lang.is_language(code):
            return lang

    raise ValueError("Language not found.")


def get_missing_languages(post: Post) -> list[Language]:
    return [lang for lang in supported_languages if lang not in post.get_languages()]


def select_language(languages: list[Language]) -> Language | None:
    if not languages:
        input("Não há linguagens suportadas disponíveis. Clique Enter para voltar.")
        return None

    for i, lang in enumerate(languages):
        print(f"{i + 1}. {lang.name} ({', '.join([lang.code] + lang.aliases)})")
    print("0. Voltar")
    print(" ")

    while True:
        try:
            selected_option = int(
                input("Digite o número da linguagem para selecioná-la: ")
            )
        except ValueError:
            print("Opção inválida.\n")
            continue

        if selected_option == 0:
            return None

        if selected_option < 0 or selected_option > len(supported_languages):
            print("Opção inválida.\n")
            continue

        return languages[selected_option - 1]


def select_from_supported_languages() -> Language | None:
    return select_language(supported_languages)


E = TypeVar("E", bound=Enum)


def select_enum(enum_cls: Type[E], prompt: str = "Escolha uma opção:") -> E | None:
    print(prompt)
    for i, option in enumerate(enum_cls):
        print(f"{i + 1}. {option.value}")
    print("0. Voltar")
    print(" ")

    while True:
        try:
            selected_option = int(input("Digite a opção desejada: "))
        except ValueError:
            print("Opção inválida.\n")
            continue

        if selected_option == 0:
            return None

        if selected_option < 0 or selected_option > len(enum_cls):
            print("Opção inválida.\n")
            continue

        return list(enum_cls)[selected_option - 1]
