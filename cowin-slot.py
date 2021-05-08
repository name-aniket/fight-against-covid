import requests
import time
import json
import hashlib
import tkinter
from sys import exit
from datetime import date
from tkinter import messagebox

BASE_URL = "https://cdn-api.co-vin.in/api"
MIN_CAPACITY = 5
MIN_AGE = 18

root = tkinter.Tk()
root.withdraw()

def wait_no_of_seconds(seconds = 15):
    time.sleep(seconds)

def get_input(message = "Enter the OTP : "):
    return input(message)    


def post_request(url, body):
    return requests.post(
        url=url,
        json=body
    )

def get_request(url, params, headers = {}):
    return requests.get(
        url=url,
        params=params,
        headers=headers
    )

def findByPin(bearer_token, pincodes):
    for pincode in pincodes:
        result = {}
        while True:
            response = get_request(
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
        if age == MIN_AGE and capacity >= MIN_CAPACITY:
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
            print("Slots")
            for slot in center['slots']:
                print("\t{}".format(slot))
            """
                TODO Create a voice alert
                TODO The message box needs to delete when user selects NO
            """
            response = messagebox.askyesno(
                title = "Free slots found",
                message = "Pincode : {}\nAvailable Slots : {}\nCenter Name : {}\n".format(
                    center['pincode'],
                    center['available_capacity'],
                    center['name']
                )
            )
            if response:
                exit(0)
            print("**************************************************************")

def main(): 
    pincodes = get_input(message = "Enter list of pincodes comma seprated : ").split(",")
    mobile_number = get_input(message = "Enter you mobile number : ")
    response_authenticate = post_request(
        url = BASE_URL + "/v2/auth/public/generateOTP",
        body = {
            "mobile" : mobile_number
        }
    )
    while True:
        if response_authenticate.text == "OTP Already Sent":
            print("OTP Already Sent")
            wait_no_of_seconds()
            response_authenticate = post_request(
                url = BASE_URL + "/v2/auth/public/generateOTP",
                body = {
                    "mobile" : mobile_number
                }
            )
        else:
            break
    txnId = json.loads(response_authenticate.text)['txnId']
    print(txnId)
    OTP = get_input()
    bearer_token = json.loads(
        post_request(
            url = BASE_URL + "/v2/auth/public/confirmOTP",
            body = {
                "otp" : hashlib.sha256(str(OTP).encode("utf-8")).hexdigest(),
                "txnId" : txnId
            }
        ).text
    )['token']
    print(bearer_token)
    while True:
        findByPin(bearer_token=bearer_token, pincodes=pincodes)
        print("TRYING AGAIN IN 2 MINUTES......")
        wait_no_of_seconds(seconds=120)

if __name__ == "__main__":
    main()
