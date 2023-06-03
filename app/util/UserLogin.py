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
        print(str(self.__user['role']))
        return str(self.__user['role'])

    def get_menu(self):
        if self.get_role() == 'tender':
            return [{'title': 'Главная', 'url': '.index'},
                    {'title': 'Рассматриваемые', 'url': '.considered'},
                    {'title': 'Отобранные', 'url': '.selected'},
                    {'title': 'База правил', 'url': '.rules'},
                    {'title': 'Выход', 'url': 'auth.logout'}
                    ]
        elif self.get_role() == 'admin':
            return [{'title': 'Выход', 'url': 'auth.logout'}]

        else:
            return [{'title': 'Главная', 'url': '.index'},
                    {'title': 'Отобранные', 'url': '.selected'},
                    {'title': 'Выход', 'url': 'auth.logout'}]
