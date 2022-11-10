from app import app, db
from app.models.Dictionary import Dictionary
from app.models.Plan import Plan
from app.models.Credit import Credit
from app.models.Payment import Payment

from sqlalchemy.sql import func

from datetime import datetime

# additional methods


@app.get("/plans_performance/{input_date}")
async def plans_performance(input_date: str):
    period = input_date.replace(input_date[:2], "01", 1)
    period_date = datetime.strptime(period, "%d.%m.%Y").date()
    input_date = datetime.strptime(input_date, "%d.%m.%Y").date()

    plans = db.query(Plan).filter(Plan.period == period).all()

    rsp = []
    for plan in plans:
        category = (
            db.query(Dictionary).filter(Dictionary.id == plan.category_id).first()
        )
        if category.id == 3:
            sum_ = (
                db.query(func.sum(Credit.body))
                .filter(Credit.issuance_date.between(period_date, input_date))
                .first()
            )[0]

        elif category.id == 4:
            sum_ = (
                db.query(func.sum(Payment.sum))
                .filter(Payment.payment_date.between(period_date, input_date))
                .first()
            )[0]
        else:
            raise ValueError("got unsupported category")

        if sum_ is None:

            sum_ = 0
        percent_success = (sum_ / plan.sum) * 100

        rsp.append([plan.period, category.name, plan.sum, sum_, f"{percent_success:.2f}"])

    return {"message": rsp}
