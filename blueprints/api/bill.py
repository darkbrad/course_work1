from flask import Blueprint, jsonify,redirect
from blueprints import deps
from core.db import get_connection
from crud import bill_crud,user_crud

bill_blueprint=Blueprint('bill_blueprint', __name__ ,url_prefix="/bill")


@bill_blueprint.route("/",methods=["POST"])
def create_bill():
    current_user = deps.get_current_user()
    with get_connection() as conn:
        bill_crud.create(conn,current_user)
        user_crud.new_bill(conn,current_user.login)
    return redirect("/user/pages")
@bill_blueprint.route("/<string:bill_id>",methods=["DELETE"])
def unact(bill_id):
    with get_connection() as conn:
        bill_crud.get_unactive(conn,bill_id)
    return jsonify({"info":f"bill {bill_id} has become unactive"})

@bill_blueprint.route("/<string:bill_id>")
def get_info(bill_id):
    with get_connection() as conn:
        data=bill_crud.get(conn,bill_id)
        id,owner,balance,status=data
    return jsonify({"info":[f"id:{id[1]}",f"owner:{owner[1]}",f"balance:{balance[1]}",f"status:{status[1]}"]})
