from datetime import datetime
from enum import Enum
from typing import Type, TypeVar

from cms.models import MediaType


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
