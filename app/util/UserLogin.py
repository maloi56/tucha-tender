from app.util import dbase
from flask_login import UserMixin


class UserLogin(UserMixin):
    def fromDB(self, user_id):
        self.__user = dbase.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user.id)

    def get_role(self):
        return str(self.__user['role'])

    def get_menu(self):
        if self.get_role() == 'tender':
            return [{'title': 'Главная', 'url': '.index', 'page': None},
                    {'title': 'Рассматриваемые', 'url': '.considered', 'page': 1},
                    {'title': 'Отобранные', 'url': '.selected', 'page': None},
                    {'title': 'База правил', 'url': '.rules', 'page': None},
                    {'title': 'Выход', 'url': 'auth.logout', 'page': None}
                    ]
        elif self.get_role() == 'admin':
            return [{'title': 'Выход', 'url': 'auth.logout'}]

        else:
            return [{'title': 'Главная', 'url': '.index', 'page': None},
                    {'title': 'Отобранные', 'url': '.selected', 'page': None},
                    {'title': 'Выход', 'url': 'auth.logout', 'page': None}]
