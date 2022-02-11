from models.user import RegistrationModel, UserModel
from models.bill import BaseBillModel
import sqlite3
import uuid
from core import passwords
from werkzeug.datastructures import Authorization
from core.errors.auth_errors import AuthError
from core.errors.registration_errors import UserExistsError


class UserCRUD:
    def create(self, conn: sqlite3.Connection, data: RegistrationModel):
        cur = conn.cursor()

        try:

            user_id = uuid.uuid4()
            cur.execute(
                "INSERT INTO User VALUES(?, ?, ?,?,?)",
                (str(user_id), data.login, passwords.hash_password(data.password), 1, 0),
            )
        finally:
            cur.close()

    def authenticate(
            self, conn: sqlite3.Connection, auth_data: Authorization
    ) -> UserModel:
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT password FROM User WHERE login=?", (auth_data.username,)
            )
            row = cur.fetchone()

            assert auth_data.username is not None

            return self.get(conn, auth_data.username)
        finally:
            cur.close()

    def get_login_by_id(self, conn: sqlite3.Connection, id):
        cur = conn.cursor()
        try:
            cur.execute("SELECT login FROM User WHERE id=?", (id,), )
            row = cur.fetchone()
            if row is not None:
                return row[0]
        finally:
            cur.close()

    def get(self, conn: sqlite3.Connection, login: str) -> UserModel or None:
        cur = conn.cursor()

        try:
            cur.execute(
                "SELECT User.id, User.login, User.bills,User.balance,User.password FROM User WHERE User.login=?",
                (login,),
            )
            row = cur.fetchone()

            if row is None:
                return None

            id, login, bills, balance, password = row

            if id is None:
                return None

            return row
        finally:
            cur.close()

    def get_all_bills(self, conn: sqlite3.Connection, user_id: str):
        cur = conn.cursor()
        try:
            cur.execute("Select Bill.id, Bill.balance FROM Bill WHERE Bill.owner=?", (user_id,), )
            row = cur.fetchall()
            return row
        finally:
            cur.close()

    def new_bill(self, conn: sqlite3.Connection, login) -> None:
        cur = conn.cursor()
        try:
            amount_of_bills = self.get(conn, login).bills
            cur.execute('''UPDATE User SET bills = REPLACE(bills,?,?) WHERE User.login=?''', (int(amount_of_bills), int(amount_of_bills) + 1, login), )
        finally:
            cur.close()

    def get_balance(self, conn: sqlite3.Connection, id: str):
        cur = conn.cursor()
        try:
            cur.execute("SELECT SUM(Bill.balance) FROM Bill WHERE Bill.owner=?", (id,), )
            row = cur.fetchone()
            return row
        finally:
            cur.close()

    def restore_balance(self, conn: sqlite3.Connection, id: str):
        cur = conn.cursor()
        try:

            login = self.get_login_by_id(conn, id)
            password = self.get(conn, login).password
            bills = self.get(conn, login).bills
            start_balance = self.get_balance(conn, id)[0]
            print(start_balance)
            cur.execute("DELETE FROM User WHERE User.login=?", (login,), )
            cur.execute("INSERT INTO User VALUES (?,?,?,?,?)", (id, login, password, bills, start_balance))
        finally:
            cur.close()

    def get_user_transactions(self, conn: sqlite3.Connection, id: str):
        cur = conn.cursor()
        try:
            for i in self.get_all_bills(conn, id):
                cur.execute("SELECT * FROM Transact WHERE sender=?", (i[0],), )
                sender_row = cur.fetchall()
                cur.execute("SELECT * FROM Transact WHERE receiver=?", (i[0],), )
                receiver_row = cur.fetchall()
                return [sender_row, receiver_row]
        finally:
            cur.close()
