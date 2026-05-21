import uuid

class PaymentError(Exception):
    pass

def charge_card(token, amount):
    """
    Fake payment processor for demo/testing purposes.
    """

    return f"demo_charge_{uuid.uuid4().hex[:10]}"