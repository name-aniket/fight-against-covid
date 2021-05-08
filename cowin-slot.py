import requests
import time
import json
import hashlib
from datetime import date

BASE_URL = "https://cdn-api.co-vin.in/api"
MOBILE_NUMBER = "7981645735"
PINCODES = ["221003","221002","221005","221311"]
MIN_CAPACITY = 5
MIN_AGE = 45

def wait_no_of_seconds(seconds = 15):
    time.sleep(seconds)

def get_input(message = "Enter the OTP : "):
    return input(message)    

def authenticate():
    return requests.post(
        url=BASE_URL + "/v2/auth/public/generateOTP",
        json={
            "mobile" : MOBILE_NUMBER
        }
    )
    
def authorize(txnId, OTP):
    return requests.post(
        url  = BASE_URL + "/v2/auth/public/confirmOTP",
        json = {
            "otp" : hashlib.sha256(str(OTP).encode("utf-8")).hexdigest(),
            "txnId" : txnId
        }
    )

def findByPin(bearer_token):
    for pincode in PINCODES:
        result = {}
        while True:
            response = requests.get(
                url = BASE_URL + "/v2/appointment/sessions/public/findByPin",
                params = {
                    "pincode" : pincode,
                    "date": date.today().strftime("%d-%m-%y")
                },
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51",
                    "Authorization": "Bearer " + bearer_token,
                    "Content-type": "application/json"
                    }
                )
            if response.status_code in [403, 401, 400]:
                print("Got status code {}! Trying again after 15 sec.".format(str(response.status_code)))
                wait_no_of_seconds(15)
            else:
                result.update(json.loads(response.text))
                break
        display_centers_available_slots(result)

def display_centers_available_slots(result):
    for center in result['sessions']:
        age = int(center['min_age_limit'])
        capacity = int(center['available_capacity'])
        if age == MIN_AGE and capacity >= CAPACITY:
            print("Pincode : {}".format(center['pincode']))
            print("Center name : {}".format(center['name']))
            print("Address : {}".format(center['address']))
            print("State : {}".format(center['state_name']))
            print("District : {}".format(center['district_name']))
            print("Block Name : {}".format(center['block_name']))
            print("Available Capacity : {}".format(center['available_capacity']))
            print("Fee type : {}".format(center['fee_type']))
            print("Fee : {}".format(center['fee']))
            print("Minimum Age : {}+".format(center['min_age_limit']))
            print("Vaccine : {}".format(center['vaccine']))
            print("Pincode : {}".format(center['pincode']))
            print("Slots")
            for slot in center['slots']:
                print("\t{}".format(slot))
            print("**************************************************************")

def main():
    response_authenticate = authenticate()

    while True:
        if response_authenticate.text == "OTP Already Sent":
            print("OTP Already Sent")
            wait_no_of_seconds()
            response_authenticate = authenticate()
        else:
            break
    
    txnId = json.loads(response_authenticate.text)['txnId']
    
    OTP = get_input()
    
    bearer_token = json.loads(authorize(txnId=txnId, OTP=OTP).text)['token']
    
    while True:
        findByPin(bearer_token=bearer_token)
        print("TRYING AGAIN IN 2 MINUTES......")
        wait_no_of_seconds(seconds=120)

if __name__ == "__main__":
    main()