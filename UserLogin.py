from flask_login import UserMixin

class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def get_role(self):
        return str(self.__user['role'])

    def get_menu(self):
        if self.get_role() == 'tender':
           return [{'title': 'Главная',
                   'url': '/'},
                   {'title': 'Рассматриваемые',
                    'url': '/considered'},
                   {'title': 'Отобранные',
                    'url': '/selected'},
                   {'title': 'База правил',
                    'url': '/rules'},
                   {'title': 'Выход',
                    'url': '/logout'}
                   ]
        else:
            return [{'title': 'Главная',
                   'url': '/'},
                    {'title': 'Отобранные',
                   'url': '/other_selected'},
                   {'title': 'Выход',
                    'url': '/logout'}]