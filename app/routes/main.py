from app import app, db
from app.models.Plan import Plan
from app.models.Dictionary import Dictionary
from app.models.Credit import Credit
from app.models.Payment import Payment

from sqlalchemy.sql import func

from datetime import datetime

import pandas as pd

# main methods


@app.get("/user_credits/{user_id}")
async def user_credits(user_id: int):
    try:
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
                    [issuance_date, is_closed, actual_return_date, body, percent, sum]
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
                    [
                        issuance_date,
                        is_closed,
                        return_date,
                        days_late,
                        body,
                        percent,
                        sum_by_body,
                        sum_by_percent,
                    ]
                )

        return {"response": resp}
    except Exception as e:
        print(e)


@app.get("/plans_insert/{file_name}")
async def plans_insert(file_name):
    rsp = []
    try:
        try:
            df = pd.read_csv(file_name)
        except Exception:
            file_name = "test.xlsx"
            df = pd.read_csv(file_name)

        for k, d in df.items():
            for i in range(len(d)):
                row = d[0].split(",")
                if (
                    db.query(Plan)
                    .join(Dictionary)
                    .filter(Plan.period == row[0])
                    .filter(Dictionary.name == row[1])
                    .exists()
                ) is not None:
                    rsp.append({"message": "plan already exist"})
                elif row[0][:2] != "01":
                    rsp.append({"message": "wrong period format"})
                elif row[2] is None:
                    rsp.append({"message": "sum is null"})
                else:
                    category_id = (
                        db.query(Dictionary.id)
                        .filter(row[1] == Dictionary.name)
                        .first()
                    )
                    id = db.query(Plan.id).order_by(Plan.id.desc()).first()[0] + 1
                    plan = Plan(
                        id=id, period=row[0], sum=row[2], category_id=category_id[0]
                    )
                    db.add(plan)
                    db.commit()
                    rsp.append({"message": "ok! added"})

    except Exception as e:
        rsp.append({"message": f"error {e}"})
        db.rollback()
    return rsp
