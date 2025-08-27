from cms.models import Language, LanguageCode, Post


class LanguageService:
    supported_languages: list[Language]

    def __init__(self):
        self.supported_languages = [
            Language(
                name="Português Brasileiro", code="pt-br", aliases=["ptbr", "pt", "br"]
            ),
            Language(
                name="Inglês", code="en-us", aliases=["en-us", "enus", "en", "us"]
            ),
            Language(name="Espanhol", code="es"),
            Language(name="Chinês", code="zh"),
            Language(name="Japonês", code="ja"),
        ]

    def get_language_by_code(self, code: LanguageCode) -> Language:
        for lang in self.supported_languages:
            if lang.is_language(code):
                return lang

        raise ValueError("Language not found.")

    def get_missing_languages(self, post: Post) -> list[Language]:
        return [
            lang
            for lang in self.supported_languages
            if lang not in post.get_languages()
        ]

    def select_language(self, languages: list[Language]) -> Language | None:
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

            if selected_option < 0 or selected_option > len(self.supported_languages):
                print("Opção inválida.\n")
                continue

            return languages[selected_option - 1]

    def select_from_supported_languages(self) -> Language | None:
        return self.select_language(self.supported_languages)
