import pandas as pd

import io
from app import app, db, File, UploadFile
from app.models.Plan import Plan
from app.models.Dictionary import Dictionary
from app.models.Credit import Credit
from app.models.Payment import Payment

from sqlalchemy.sql import func

from datetime import datetime


@app.get("/user_credits/{user_id}")
async def user_credits(user_id: int):
    all_credits = db.query(Credit).filter(Credit.user_id == user_id).all()
    resp = []

    for cred in all_credits:
        issuance_date = cred.issuance_date
        is_closed = cred.actual_return_date is not None

        if is_closed:
            actual_return_date = cred.actual_return_date
            body = cred.body
            percent = cred.percent

            sum = (
                db.query(Payment.credit_id, func.sum(Payment.sum).label("sum"))
                .join(Credit)
                .filter(Credit.id == cred.id)
                .group_by(Payment.credit_id)
                .all()[0]["sum"]
            )

            resp.append(
                {"issuance_date": issuance_date,
                 "is_closed": is_closed,
                 "return_date": actual_return_date,
                 "days_late": body,
                 "percent": percent,
                 "sum_by_body": sum}
            )
        else:
            return_date = cred.return_date
            days_late = (datetime.now().date() - return_date).days
            body = cred.body
            percent = cred.percent
            sum_by_body = (
                db.query(func.sum(Payment.sum).label("sum"))
                .join(Credit)
                .join(Dictionary)
                .filter(Credit.id == cred.id)
                .filter(Dictionary.id == 1)
                .group_by(Payment.credit_id)
                .all()[0]["sum"]
            )

            sum_by_percent = (
                db.query(func.sum(Payment.sum).label("sum"))
                .join(Credit)
                .join(Dictionary)
                .filter(Credit.id == cred.id)
                .filter(Dictionary.id == 2)
                .group_by(Payment.credit_id)
                .all()[0]["sum"]
            )

            resp.append(
                {
                    "issuance_date": issuance_date,
                    "is_closed": is_closed,
                    "return_date": return_date,
                    "days_late": days_late,
                    "body": body,
                    "percent": percent,
                    "sum_by_body": sum_by_body,
                    "sum_by_percent": sum_by_percent,
                }
            )

    if not resp:
        return {"response": resp,
                "status": "error",
                "message": "no user"}
    return {"response": resp,
            "status": "ok"}


@app.post("/plans_insert/")
async def plans_insert(file: UploadFile = File()):
    rsp = []
    f = io.BytesIO(await file.read())
    df = pd.read_excel(f)

    for idx, row_ in df.iterrows():
        row = row_.to_dict()
        row["period"] = row["period"].date()

        if db.query(
            db.query(Plan)
            .join(Dictionary)
            .filter(Plan.period == row["period"])
            .filter(Dictionary.name == row["name"])
            .exists()
        ).scalar():
            rsp.append(
                {
                    "row": row,
                    "status": "error",
                    "message": "plan already exist",
                }
            )
        elif row["period"].day != 1:
            rsp.append(
                {
                    "row": row,
                    "status": "error",
                    "message": "wrong period format",
                }
            )
        elif not row["sum"]:
            rsp.append(
                {"row": row,
                 "status": "error",
                 "message": "sum is null"}
            )
        else:
            category_id = (
                db.query(Dictionary.id)
                .filter(row["name"] == Dictionary.name)
                .first()
            )
            plan = Plan(
                period=row["period"], sum=row["sum"], category_id=category_id[0]
            )
            db.add(plan)
            db.commit()
            rsp.append(
                {
                    "row": row,
                    "id": plan.id,
                    "status": "success",
                    "message": "row added",
                }
            )
    #
    # except:
    #     rsp.append({"status": "error", "message": "technical issues"})
    #     db.rollback()
    return rsp
