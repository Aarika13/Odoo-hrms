import re
from dateutil import parser
from datetime import date


class Validation:

    @staticmethod
    def check_phone(mobile_no):
        if re.match("^(\+\d{1,3}[- ]?)?\d{10}$", mobile_no) is None:
            return False
        return True

    @staticmethod
    def check_names(name):
        if len(name) > 60:
            return False
        elif re.match("^[a-zA-Z\s]+$", name) is None:
            return False
        return True

    @staticmethod
    def check_email(email):
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) is None:
            return False
        return True 

    @staticmethod
    def check_confirm_date(join_date, confirm_date):
        if not join_date:
            return False
        elif parser.parse(join_date) > parser.parse(confirm_date):
            return False
        else:
            return True

    @staticmethod
    def check_date(effective_from, effective_to):
        from_date = date.strftime(effective_from, "%Y-%m-%d")
        to_date = date.strftime(effective_to, "%Y-%m-%d")
        if parser.parse(from_date) > parser.parse(to_date):
            return False
        else:
            return True
