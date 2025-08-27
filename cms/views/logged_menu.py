import os
from cms.models import (
    Permission,
    Site,
    SiteAction,
    SiteAnalyticsEntry,
    User,
    UserRole,
)
from cms.views.menu import AbstractMenu, AppContext, MenuOptions
from cms.views.site_menu import SiteMenu


class LoggedMenu(AbstractMenu):
    context: AppContext
    logged_user: User

    def __init__(self, context: AppContext, logged_user: User):
        self.context = context
        self.logged_user = logged_user

    def show(self):
        options: list[MenuOptions] = [
            {"message": "Exibir dados de perfil", "function": self.show_profile},
            {"message": "Criar um site", "function": self.create_site},
            {"message": "Selecionar um site", "function": self.select_site},
            {"message": "Listar sites do usuário", "function": self.show_user_sites},
        ]

        if self.logged_user.role == UserRole.ADMIN:
            options.extend(
                [
                    {"message": "Ver logs do sistema", "function": self.show_logs},
                ]
            )

        LoggedMenu.prompt_menu_option(
            options,
            lambda: print(f"CMS\nBem vindo, {self.logged_user.first_name}!\n"),
            "Fazer logout",
        )

    def show_logs(self):
        try:
            os.system("clear")
            limit = int(
                input("Insira a quantidade de logs que deseja ver (ou 0 para voltar): ")
            )

            if limit == 0:
                return

            self.context.analytics_repo.show_logs(limit=limit)

        except ValueError:
            print("Valor inválido.")

        print(" ")
        input("Clique Enter para voltar ao menu.")

    def show_profile(self):
        print(f"Nome: {self.logged_user.first_name} {self.logged_user.last_name}")
        print(f"E-mail: {self.logged_user.email}")
        print(f"Role: {self.logged_user.role}")

        print(" ")
        input("Clique Enter para voltar ao Menu.")

    def create_site(self):
        site_name = input("Diga o nome do seu site: ")
        description = input("Informe uma descrição breve para o site: ")
        site = Site(owner=self.logged_user, name=site_name, description=description)
        self.context.site_repo.add_site(site)
        permission = Permission(user=self.logged_user, site=site)
        self.context.permission_repo.grant_permission(permission)

        input("Site criado. Clique Enter para voltar ao menu.")

    def select_site(self):
        sites: list[Site] = self.context.site_repo.get_sites()

        def execute_for_option(selected_site: Site):
            self.context.analytics_repo.log(
                SiteAnalyticsEntry(
                    user=self.logged_user,
                    site=selected_site,
                    action=SiteAction.ACCESS,
                )
            )

            SiteMenu(self.context, self.logged_user, selected_site).show()

        LoggedMenu.prompt_generic(
            sites, "Sites disponíveis", execute_for_option, lambda m: m.name
        )

    def show_user_sites(self):
        if not self.logged_user:
            return

        user_sites: list[Site] = self.context.site_repo.get_user_sites(self.logged_user)
        for i, site in enumerate(user_sites):
            print(f"{i + 1}. {site.name}")

        print(" ")
        input("Clique Enter para voltar ao Menu.")
