import sqlite3
import time
import math

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def init_db(self):
        try:
            self.__cur.execute(
                'CREATE TABLE IF NOT EXISTS selected (id TEXT PRIMARY KEY, title TEXT NOT NULL, price INTEGER NOT NULL, date TEXT NOT NULL, href TEXT NOT NULL, status TEXT NOT NULL)')
            self.__cur.execute(
                'CREATE TABLE IF NOT EXISTS filter_words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT NOT NULL)')
            self.__cur.execute(
                'CREATE TABLE IF NOT EXISTS ban_words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT NOT NULL)')
            self.__cur.execute(
                'CREATE TABLE IF NOT EXISTS rules (id INTEGER PRIMARY KEY AUTOINCREMENT,priceFrom INTEGER, priceTo INTEGER,date TEXT NOT NULL)')
            self.__cur.execute(
                'CREATE TABLE IF NOT EXISTS users \
                (id integer PRIMARY KEY AUTOINCREMENT,\
                role INT NOT NULL,\
                login text NOT NULL,\
                psw text NOT NULL,\
                time integer NOT NULL,\
                FOREIGN KEY (role) REFERENCES roles(id))')
            self.__cur.execute(
                'CREATE TABLE IF NOT EXISTS rating \
                (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                rate INT,\
                comment Text,\
                costprice INT,\
                role INT NOT NULL,\
                tender INT NOT NULL,\
                FOREIGN KEY (role) REFERENCES roles (id),\
                FOREIGN KEY (tender) REFERENCES selected (id))')
            self.__cur.execute(
                'CREATE TABLE IF NOT EXISTS roles \
                (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)')
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка вставки данных в БД " + str(e))

    def insert_tenders(self, res):
        try:
            self.__cur.execute('DELETE FROM selected WHERE status = "отбор"')
            selected = self.__cur.execute('SELECT * FROM selected').fetchall()
            for key, value in res.items():
                if key not in [item[0] for item in selected]:
                    value['status'] = 'отбор'
                    self.__cur.execute(
                        'INSERT OR REPLACE INTO selected VALUES (:id,:title, :price, :date, :href, :status)', value)
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

    def get_considered(self, status):
        try:
            self.__cur.execute('SELECT * FROM selected WHERE status = ?', (status,))
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

    def get_selected(self, status):
        try:
            self.__cur.execute('SELECT * FROM selected WHERE status != ?', (status,))
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

    def get_roles(self):
        try:
            self.__cur.execute('SELECT * FROM roles')
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

    def select_tender(self, tender_id):
        try:
            self.__cur.execute('UPDATE selected SET status = "на рассмотрении" WHERE id = ?', (tender_id, ))
            roles = self.get_roles()
            for role in roles:
                if role['name'] != 'tender' and role['name'] != 'director':
                    self.__cur.execute(
                        "INSERT INTO rating (rate, comment, costprice, role, tender) VALUES (0, NULL, 0, ?, ?)",
                        (role['id'], tender_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

    def get_filter_words(self):
        try:
            self.__cur.execute('SELECT * FROM filter_words')
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

    def get_ban_words(self):
        try:
            self.__cur.execute('SELECT * FROM ban_words')
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

    def get_optional_rules(self):
        try:
            self.__cur.execute('SELECT * FROM rules')
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

    def add_rule(self, new_rule):
        try:
            self.__cur.execute('INSERT INTO filter_words (word) VALUES (?)', [new_rule])
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))
        return False

    def add_user(self, role, login, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE login LIKE '{login}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким login уже существует")
                return False

            tm = math.floor(time.time())
            self.__cur.execute.execute("SELECT id from roles WHERE name = ?", (role,))
            role_id = self.__cur.execute.fetchone()
            print(role_id['id'])
            self.__cur.execute.execute("INSERT INTO users (role, login, psw, time) VALUES(?, ?, ?, ?)",
                        (role_id['id'], login, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))
            return False
        return True

    def add_optional_rule(self, priceFrom, priceTo, date):
        try:
            if len(self.__cur.execute('SELECT * FROM rules').fetchall()) == 0:
                self.__cur.execute('INSERT INTO rules (priceFrom, priceTo, date) VALUES(?,?,?) ',
                                   (priceFrom, priceTo, date))
            else:
                self.__cur.execute('UPDATE rules set priceFrom = ?, priceTo = ?, date = ? WHERE id = 1',
                            (priceFrom, priceTo, date))
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))
        return False

    def delete_filter_word(self, word):
        try:
            self.__cur.execute('DELETE FROM filter_words WHERE word = ?', [word])
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))
        return False

    def add_ban_rule(self, new_rule):
        try:
            self.__cur.execute('INSERT INTO ban_words (word) VALUES (?)', [new_rule])
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))
        return False

    def delete_ban_word(self, word):
        try:
            self.__cur.execute('DELETE FROM ban_words WHERE word = ?', [word])
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))
        return False

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = dict(self.__cur.fetchone())
            self.__cur.execute(f"SELECT name FROM roles WHERE id = ? LIMIT 1", (res['role'],))
            role_name = self.__cur.fetchone()
            res['role'] = role_name['name']
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def getUserByLogin(self, login):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE login = '{login}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def get_tender(self, tender_id):
        try:
            self.__cur.execute(f"SELECT * FROM selected WHERE id = '{tender_id}' AND status != 'отбор' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))
        return False

    def rate_tender(self, role, tender_id, cost_price, comment, rate):
        try:
            self.__cur.execute("UPDATE rating SET rate = ?, comment = ?, costprice = ? WHERE tender = ? AND\
             rating.role = (SELECT id FROM roles WHERE name = ? LIMIT 1)",
                               (rate, comment, cost_price, tender_id, role))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД " + str(e))
            return False
        return True

    def set_status(self, tender_id, status):
        try:
            self.__cur.execute("UPDATE selected SET status = ? WHERE id = ?", (status, tender_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка БД в статусе " + str(e))
            return False
        return True

    def get_tender_rate(self, tender_id, role):
        try:
            self.__cur.execute("SELECT rate, comment, costprice, tender FROM rating \
            INNER JOIN roles on rating.role = roles.id \
            WHERE rating.tender = ? AND roles.name = ?", (tender_id, role))
            res = self.__cur.fetchone()
            if not res:
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))
        return False
