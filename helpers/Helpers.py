from datetime import datetime
from datetime import date


class DateHelper:
    @staticmethod
    def get_age_from_bdate(bdate):
        today = date.today()
        try:
            birthday = datetime.strptime(bdate, "%d-%m-%Y").date()
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
            return age
        finally:
            return 30
