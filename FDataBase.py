import datetime
import math
import time
import sqlite3
import re
from flask_login import current_user

from flask import url_for


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = """Select * from mainmenu"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из бд")
        return []


    def getCategory(self):
        sql = """Select * from Category"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из бд")
        return []


    def addCategory(self, category):
        try:
            self.__cur.execute(f"SELECT COUNT() AS 'count' from Category where category LIKE'{category}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Такая категория  уже существует")
                return False
            print("aaa")
            self.__cur.execute("INSERT INTO Category VALUES(?)", (category,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления категории в БД " + str(e))
            return False

        return True


    def addPost(self, title, text,url,category,author):
        try:
            self.__cur.execute(f"SELECT COUNT() AS 'count' from posts where url LIKE'{url}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Cтатья с таким url уже существует")
                return False
            base = url_for("static", filename='images')
            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>" + "../" + base + "/\\g<url>>",
                          text)

            tm = datetime.datetime.now()
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?,?,?,?)", (title, category, text,url,tm,author))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД " + str(e))
            return False

        return True

    def getPost(self, alias):
        try:
            self.__cur.execute(f"SELECT title,text,time,id FROM posts WHERE url Like '{alias}' LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))
        return (False, False)


    def DeletePost(self, id):
        try:
            self.__cur.execute(f"SELECT id AS 'count' from posts where id ='{id}'")
            res = self.__cur.fetchone()
            if res['count'] <= 0:
                print("Пост есть  уже существует")
                return False
            self.__cur.execute(f"delete from posts  where id ={id}")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка Удаления поста из БД " + str(e))
            return False


    def getPostsAnonce(self):
        try:
            author = current_user.getName()
            self.__cur.execute(f"SELECT id, title, text,url FROM posts where author='{author}' Order by time asc")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))
        return []

    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE name LIKE '{name}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким  именем уже существует")
                return False

            tm = datetime.datetime.now()
            #NULL в конце avatar
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, ?,NULL)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД " + str(e))
            return False

        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False


    def getUserByName(self, name):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE name = '{name}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False

        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления аватара в БД: " + str(e))
            return False
        return True


    def DeleteUser(self, author):
        try:
            self.__cur.execute(f"delete from users  where author ={author}")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка Удаления поста из БД " + str(e))
            return False
