# .../api/user
from flask import Blueprint, jsonify, redirect, render_template
from models.user import RegistrationModel
from crud import user_crud, bill_crud
from core.db import get_connection
from blueprints import deps

user_blueprint = Blueprint("user_blueprint", __name__, url_prefix="/user")


@user_blueprint.route("/", methods=["POST"])
def register():
    registration_data = deps.get_input(RegistrationModel)

    with get_connection() as conn:
        user_crud.create(conn, registration_data)

    return jsonify({"info": "OK"}), 201


@user_blueprint.route("/bill")
def get_bill(a=0):
    current_user = deps.get_current_user()
    with get_connection() as conn:
        bills = user_crud.get_all_bills(conn, current_user.id)
        if a == 0:
            return jsonify({'bills': bills})
        elif a == 1:
            return bills


@user_blueprint.route("/transfer/<string:bill_id_sender>/<string:receiver_bill_id>/<int:money>")
def transfer(bill_id_sender: str, receiver_bill_id: str, money: int):
    with get_connection() as conn:
        bill_crud.transfer_money(conn, sender_bill_id=bill_id_sender, receiver_bill_id=receiver_bill_id, money=money)
        user_crud.restore_balance(conn, bill_crud.get(conn, bill_id_sender).owner)
        user_crud.restore_balance(conn, bill_crud.get(conn, receiver_bill_id).owner)
    return jsonify({'info': 'OK'})


@user_blueprint.route("/transaction")
def red_page():
    current_user = deps.get_current_user()
    return redirect(f"/user/transaction/{current_user.login}")


@user_blueprint.route("/transaction/<string:login>")
def get_transact(login):
    with get_connection() as conn:
        transactions = []
        moneys = []
        user_id = user_crud.get(conn, login).id
        data = user_crud.get_user_transactions(conn, user_id)
        a = data[0]
        for i in a:
            if a[0] == i:
                s = f'''{i[1]}-->{i[2]}'''
                transactions.append(s)
                moneys.append(f"-{i[3]}")
            elif a[1] == i:
                s = f'''{i[1]}-->{i[2]}'''
                transactions.append(s)
                moneys.append(f"+{i[3]}")
    return {transactions[i]: moneys[i] for i in range(len(transactions))}
