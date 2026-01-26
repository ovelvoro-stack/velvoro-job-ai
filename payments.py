import razorpay
from config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)

def create_payment(amount):
    return client.order.create({
        "amount": amount * 100,
        "currency": "INR",
        "payment_capture": 1
    })
