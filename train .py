from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import uuid

app = FastAPI()

# Replace with your sandbox or production keys
PRIMARY_KEY = "5f0ae0e8e28e466091a57b73e265591b"
SUBSCRIPTION_KEY = "d3775ca1ddb04f368c4e2fd1fe3f6d9e"
BASE_URL = "https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay"  # sandbox URL

class PaymentRequest(BaseModel):
    phone_number: str
    amount: float

@app.post("/pay")
def create_payment(payment: PaymentRequest):
    external_id = str(uuid.uuid4())

    headers = {
        "Authorization": f"Bearer {PRIMARY_KEY}",   # For sandbox, key may work; in production get OAuth token
        "X-Reference-Id": external_id,
        "X-Target-Environment": "sandbox",  # change to "production" for live
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "amount": str(payment.amount),
        "currency": "XAF",
        "externalId": external_id,
        "payer": {
            "partyIdType": "MSISDN",
            "partyId": payment.phone_number
        },
        "payerMessage": "Payment for test order",
        "payeeNote": "Thank you for your order"
    }

    response = requests.post(BASE_URL, headers=headers, json=payload)

    if response.status_code not in [200, 202]:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return {
        "external_id": external_id,
        "status_code": response.status_code,
        "response": response.json() if response.content else response.text
    }
