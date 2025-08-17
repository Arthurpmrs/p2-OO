from datetime import datetime

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
