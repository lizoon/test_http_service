import pandas as pd
import numpy as np
import datetime as dt

from app import *


def add():
    users = "/home/liza/PycharmProjects/test_system/app/tables/users.csv"
    plans = "/home/liza/PycharmProjects/test_system/app/tables/plans.csv"
    payments = "/home/liza/PycharmProjects/test_system/app/tables/payments.csv"
    dictionary = "/home/liza/PycharmProjects/test_system/app/tables/dictionary.csv"
    credits = "/home/liza/PycharmProjects/test_system/app/tables/credits.csv"

    users_df = pd.read_csv(users, delimiter="\t")
    for index, row in users_df.iterrows():
        id = int(row["id"])
        login = row["login"]
        registration_date = dt.datetime.strptime(
            row["registration_date"], "%d.%m.%Y"
        ).date()
        u = User(id=id, login=login, registration_date=registration_date)
        db.add(u)

    db.commit()
    print("users pushed")

    credits_df = pd.read_csv(credits, delimiter="\t")
    for index, row in credits_df.iterrows():
        id = int(row["id"])
        user_id = int(row["user_id"])
        issuance_date = dt.datetime.strptime(row["issuance_date"], "%d.%m.%Y").date()
        return_date = dt.datetime.strptime(row["return_date"], "%d.%m.%Y").date()

        if row["actual_return_date"] is np.nan:
            actual_return_date = None
        else:
            actual_return_date = dt.datetime.strptime(
                row["actual_return_date"], "%d.%m.%Y"
            ).date()

        body = int(row["body"])
        percent = float(row["percent"])

        c = Credit(
            id=id,
            user_id=user_id,
            issuance_date=issuance_date,
            return_date=return_date,
            actual_return_date=actual_return_date,
            body=body,
            percent=percent,
        )
        db.add(c)

    db.commit()
    print("credits pushed")

    dict_df = pd.read_csv(dictionary, delimiter="\t")
    for index, row in dict_df.iterrows():
        id = int(row["id"])
        name = row["name"]

        d = Dictionary(id=id, name=name)
        db.add(d)

    db.commit()
    print("dict pushed")

    payments_df = pd.read_csv(payments, delimiter="\t")
    for index, row in payments_df.iterrows():
        id = int(row["id"])
        sum = int(row["sum"])
        payment_date = dt.datetime.strptime(row["payment_date"], "%d.%m.%Y").date()
        credit_id = int(row["credit_id"])
        type_id = int(row["type_id"])

        pp = Payment(
            id=id,
            sum=sum,
            payment_date=payment_date,
            credit_id=credit_id,
            type_id=type_id,
        )
        db.add(pp)

    db.commit()
    print("payments pushed")

    plans_df = pd.read_csv(plans, delimiter="\t")
    for index, row in plans_df.iterrows():
        id = int(row["id"])
        period = row["period"]
        sum = int(row["sum"])
        category_id = int(row["category_id"])
        p = Plan(id=id, period=period, sum=sum, category_id=category_id)
        db.add(p)

    db.commit()
    print("plans pushed")


if __name__ == "__main__":
    add()
