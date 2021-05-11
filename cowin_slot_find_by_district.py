import requests
import time
import json
import hashlib
import tkinter
from sys import exit
from os import system
from datetime import date, timedelta
from tkinter import messagebox

"""
    GLOBAL variables
"""
TXNID = ""
BEARER_TOKEN = ""

"""
    Co-win base URL
"""
BASE_URL = "https://cdn-api.co-vin.in/api"

"""
    Generate OTP endpoint
"""
GENERATE_OTP_URL = "/v2/auth/public/generateOTP"

"""
    Confirm OTP endpoint
"""
CONFIRM_OTP_URL = "/v2/auth/public/confirmOTP"

"""
    Provided full path of the sound file
"""
ALERT_SOUND = "~/Documents/CODEBASE/fight-againt-covid/notification_sound.mp3"

"""
    Change accordingly
    For 18+ change to 18
    For 45+ change to 45
"""
MIN_AGE = 18

"""
    Atleast this many slots should be available
    otherwise the time by you will login
    to book the slots you might not find any slots 
"""
MIN_CAPACITY = 10

"""
    This list will contain the all the centers which
    you have marked NO from the notfication pop-up 
"""
CENTERS = []

"""
    Your district code.
    For getting distrit code follow the following steps:
        1) Get your state id by clicking this link
            (i) https://cdn-api.co-vin.in/api/v2/admin/location/states
        
        2) Get you district code by clicking this link
            (i) https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}
            
            NOTE change the {state_id} with the id you got from the earlier link
"""
DISTRICT_ID = 696


def wait_no_of_seconds(seconds=15):
    time.sleep(seconds)


def post_request(url, body):
    return requests.post(
        url=url,
        json=body
    )


def get_request(url, params, headers={}):
    return requests.get(
        url=url,
        params=params,
        headers=headers
    )


def get_error_message(error_code):
    return {
        '400': 'Not Found',
        '401': 'Unauthenticated Access',
        '403': 'Request Blocked',
        '500': 'Internal Server Error'
    }[error_code]


def notification_pop_up(center):
    root = tkinter.Tk()
    root.withdraw()
    """
        TODO Create a voice alert
        TODO The message box needs to delete when user selects NO
    """
    response = messagebox.askyesno(
        title="Free slots found",
        message="Pincode : {}\nAvailable Slots : {}\nCenter Name : {}\nVaccine : {}\nAge : {}\n".format(
            center['pincode'],
            center['available_capacity'],
            center['name'],
            center['vaccine'],
            center['min_age_limit']
        )
    )
    if response:
        exit(0)
    else:
        CENTERS.append(center['center_id'])
        root.destroy()


def authenticate():
    """
        Takes mobile number
        Returns txnId
    """
    mobile_number = input("Enter mobile number : ")
    response = post_request(
        url=BASE_URL + GENERATE_OTP_URL,
        body={
            "mobile": mobile_number
        }
    )
    if response.status_code in [200, 400]:
        """
            Check if OTP sent within last few minutes
        """
        while True:
            if response.text == "OTP Already Sent":
                print("OTP Already Sent")
                wait_no_of_seconds()
                response = post_request(
                    url=BASE_URL + GENERATE_OTP_URL,
                    body={
                        "mobile": mobile_number
                    }
                )
            else:
                return json.loads(response.text)['txnId']
    else:
        print(get_error_message(str(response.status_code)))
        exit(1)


def authorization(txnId):
    """
        Takes Transaction ID (txnId)
        Returns authorization token
    """
    otp = input("Enter OTP : ")
    response = post_request(
        url=BASE_URL + CONFIRM_OTP_URL,
        body={
            "otp": hashlib.sha256(str(otp).encode("utf-8")).hexdigest(),
            "txnId": txnId
        }
    )
    if response.status_code == 200:
        return json.loads(response.text)['token']
    else:
        print(get_error_message(str(response.status_code)))
        exit(1)


def findByDistrict(bearer_token, session, district_id=DISTRICT_ID):
    response = session.get(
        url=BASE_URL + "/v2/appointment/sessions/public/findByDistrict",
        params={
            "district_id": district_id,
            "date": (date.today() + timedelta(days=1)).strftime("%d-%m-%y")
        },
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51",
            "Authorization": "Bearer " + bearer_token,
            "Content-type": "application/json"
        }
    )
    if response.status_code == 401:
        global TXNID, BEARER_TOKEN
        TXNID = authenticate()
        BEARER_TOKEN = authorization(txnId=TXNID)
    elif response.status_code == 200:
        display_centers_available_slots(json.loads(response.text))


def display_centers_available_slots(result):
    for center in result['sessions']:
        age = int(center['min_age_limit'])
        capacity = int(center['available_capacity'])
        if age == MIN_AGE and capacity >= MIN_CAPACITY and center['center_id'] not in CENTERS:
            print("Pincode : {}".format(center['pincode']))
            print("Center name : {}".format(center['name']))
            print("Address : {}".format(center['address']))
            print("State : {}".format(center['state_name']))
            print("District : {}".format(center['district_name']))
            print("Block Name : {}".format(center['block_name']))
            print("Available Capacity : {}".format(
                center['available_capacity']))
            print("Fee type : {}".format(center['fee_type']))
            print("Fee : {}".format(center['fee']))
            print("Minimum Age : {}+".format(center['min_age_limit']))
            print("Vaccine : {}".format(center['vaccine']))
            print("Slots")
            for slot in center['slots']:
                print("\t{}".format(slot))

            for _ in range(3):
                system("mpg123 " + ALERT_SOUND)
                time.sleep(1)

            notification_pop_up(center=center)
            print("**************************************************************")


def main():
    global TXNID, BEARER_TOKEN
    TXNID = authenticate()
    BEARER_TOKEN = authorization(txnId=TXNID)
    
    session = requests.Session()
    while True:
        findByDistrict(bearer_token=BEARER_TOKEN, session=session)
        print("Trying again in 4 seconds seconds ......")
        wait_no_of_seconds(seconds=4)


if __name__ == "__main__":
    main()
