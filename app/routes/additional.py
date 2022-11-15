import pandas as pd

from app import app, db
from app.models.Dictionary import Dictionary
from app.models.Plan import Plan
from app.models.Credit import Credit
from app.models.Payment import Payment

from sqlalchemy.sql import func, extract

from datetime import datetime


@app.get("/plans_performance/{input_date}")
async def plans_performance(input_date: str):
    period = input_date.replace(input_date[:2], "01", 1)
    period_date = datetime.strptime(period, "%d.%m.%Y").date()
    input_date = datetime.strptime(input_date, "%d.%m.%Y").date()

    plans = db.query(Plan).filter(Plan.period == period_date).all()

    rsp = []
    for plan in plans:
        category = (
            db.query(Dictionary).filter(Dictionary.id == plan.category_id).first()
        )

        try:
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

            rsp.append(
                {
                    "period": plan.period,
                    "category": category.name,
                    "sum_from_plan": plan.sum,
                    "output_sum": sum_,
                    "percent_success": f"{percent_success:.2f}",
                }
            )
        except ValueError as err:
            rsp.append(
                {
                    "message": f"{err}",
                    "status": "error"
                }
            )

    if not rsp:
        return {"response": rsp,
                "status": "error",
                "message": "plan doesn't exist"}
    return {"response": rsp,
            "status": "ok"}


@app.get("/year_performance/{year}")
async def year_performance(year: int):
    rsp = []
    months = pd.date_range(start=f"{year}-01-01", end=f"{year}-12-01", freq="MS")

    sum_of_credits_by_year = (
        db.query(func.sum(Credit.body))
        .filter(
            extract('year', Credit.issuance_date) == year
        )
        .first()
    )[0]
    sum_of_payments_by_year = (
        db.query(func.sum(Payment.sum))
        .filter(
            extract('year', Payment.payment_date) == year
        ).first()
    )[0]

    for month in months:
        try:
            credits_count = db.query(func.count(Credit.id)).filter(
                extract('year', Credit.issuance_date) == month.date().year,
                extract('month', Credit.issuance_date) == month.date().month
            ).first()[0]

            credits_sum_by_plan = (
                db.query(func.sum(Plan.sum))
                .join(Dictionary)
                .filter(
                    Dictionary.name == 'видача',
                    extract('year', Plan.period) == month.date().year,
                    extract('month', Plan.period) == month.date().month
                )
                .first()
            )[0]
            sum_of_credits = (
                db.query(func.sum(Credit.body))
                .filter(
                    extract('year', Credit.issuance_date) == month.date().year,
                    extract('month', Credit.issuance_date) == month.date().month
                )
                .first()
            )[0]
            percent_credits_success = 100 * (sum_of_credits / credits_sum_by_plan)

            payments_count = (
                db.query(func.count(Payment.id))
                .filter(
                    extract('year', Payment.payment_date) == month.date().year,
                    extract('month', Payment.payment_date) == month.date().month
                )
                .first()
            )[0]
            payments_sum_by_plan = (
                db.query(func.sum(Plan.sum))
                .join(Dictionary)
                .filter(
                    Dictionary.name == 'збір',
                    extract('year', Plan.period) == month.date().year,
                    extract('month', Plan.period) == month.date().month
                )
                .first()
            )[0]
            sum_of_payments = (
                db.query(func.sum(Payment.sum))
                .filter(
                    extract('year', Payment.payment_date) == month.date().year,
                    extract('month', Payment.payment_date) == month.date().month
                )
                .first()
            )[0]
            percent_payments_success = 100 * (sum_of_payments / payments_sum_by_plan)

            percent_credits_m_to_y = (sum_of_credits / sum_of_credits_by_year) * 100
            percent_payments_m_to_y = (sum_of_payments / sum_of_payments_by_year) * 100

            rsp.append({"response": {"period": month.date(),
                                     "credits_count": credits_count,
                                     "credits_sum_by_plan": credits_sum_by_plan,
                                     "sum_of_credits": sum_of_credits,
                                     "percent_credits_success": f"{percent_credits_success:.2f}",
                                     "payments_count": payments_count,
                                     "payments_sum_by_plan": payments_sum_by_plan,
                                     "sum_of_payments": sum_of_payments,
                                     "percent_payments_success": f"{percent_payments_success:.2f}",
                                     "percent_credits_success_month_year": f"{percent_credits_m_to_y:.2f}",
                                     "percent_payments_success_month_year": f"{percent_payments_m_to_y:.2f}"
                                     },
                        "status": "ok"
                        })
        except:
            rsp.append({"response": {"period": month.date()},
                        "status": "error",
                        "message": "no such month"})
    return rsp
