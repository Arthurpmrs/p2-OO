import os

from cms.models import User, UserRole
from cms.views.logged_menu import LoggedMenu
from cms.views.menu import AbstractMenu, AppContext, MenuOptions
from cms.populate import populate


class Menu(AbstractMenu):
    context: AppContext

    def __init__(self):
        self.context = AppContext()
        populate(self.context)

    def show(self):
        try:
            self._main_menu()
        except KeyboardInterrupt:
            print("\nSaindo.")

    def _main_menu(self):
        while True:
            os.system("clear")
            print("CMS\n")

            options: list[MenuOptions] = [
                {"message": "Fazer Login", "function": self.login},
                {
                    "message": "Registrar um novo usuário",
                    "function": self.create_user,
                },
            ]

            for i, option in enumerate(options):
                print(f"{i + 1}. {option['message']}")
            print("0. Sair")
            print(" ")

            try:
                selected_option = int(
                    input("Digite o número da opção para selecioná-la: ")
                )
            except ValueError:
                print("Opção inválida.\n")
                continue

            if selected_option == 0:
                break

            if selected_option < 0 or selected_option > len(options):
                print("Opção inválida.\n")
                continue

            os.system("clear")
            options[selected_option - 1]["function"]()

    def create_user(self):
        first_name = input("Digite seu primeiro nome: ")
        last_name = input("Digite seu último nome: ")
        email = input("Digite seu email: ")
        username = input("Digite um username: ")
        password = input("Digite uma senha: ")

        user = User(first_name, last_name, email, username, password, UserRole.USER)
        self.context.user_repo.add_user(user)

        input("Usuário Criado! Clique Enter para voltar ao menu.")

    def login(self):
        while True:
            username = input("Username: ")
            password = input("Senha: ")

            try:
                user = self.context.user_repo.validate_user(username, password)
                LoggedMenu(self.context, user).show()
                break
            except ValueError:
                os.system("clear")
                print("Credenciais Inválidas!\n")

        self.logged_user = user
