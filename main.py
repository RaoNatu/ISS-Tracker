import time
import requests
import datetime
import smtplib
import os
from email.mime.text import MIMEText
import pytz
from dotenv import load_dotenv

MY_LAT = 29.610929
MY_LONG = 74.295097

latitude = 0
longitude = 0


def is_iss_overhead():
    global latitude, longitude
    response = requests.get("http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()
    latitude = float(data["iss_position"]["latitude"])
    longitude = float(data["iss_position"]["longitude"])
    iss_position = (longitude, latitude)
    print(iss_position)
    if MY_LAT - 5 <= latitude <= MY_LAT + 5 and MY_LONG - 5 <= longitude <= MY_LONG + 5:
        return True


def is_night():
    IST = pytz.timezone('Asia/Kolkata')
    current_time = datetime.datetime.now(IST)
    split_current_time = str(current_time).split(" ")
    hour = int(split_current_time[1][0:2])
    if hour >= 18 or hour <= 4:
        return True


def get_location():
    try:
        data_iss_location = requests.get(f"https://us1.locationiq.com/v1/reverse.php?key={api_key}"
                                         f"&lat={latitude}&lon={longitude}&format=json").json()
        print(data_iss_location["display_name"])
        return data_iss_location["display_name"]
    except KeyError:
        pass


load_dotenv()
email = os.environ["EMAIL"]
password = os.environ["PASSWORD"]
api_key = os.environ["API_KEY"]
to_email = ""   # Receiver Email

while True:
    connection = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    connection.login(email, password)
    iss_location = get_location()
    msg = MIMEText(f"International Space Station is at {iss_location}")
    msg["Subject"] = "ISS Tracker"
    msg["From"] = email
    msg["To"] = to_email
    if is_iss_overhead() and is_night():
        try:
            connection.sendmail(from_addr=email,
                                to_addrs=to_email,
                                msg=f"{msg.as_string()}\n\nLook Above!")
            print("In your Area!")
            print("Mail Sent!")
            connection.close()
        except Exception as e:
            print(f"Mail not Sent: {e}")

    elif is_night():
        if iss_location is not None:
            connection.sendmail(from_addr=email,
                                to_addrs=to_email,
                                msg=msg.as_string())
            print("Mail Sent!")
            print("Night Time: Sleeping for 5 minutes")
            time.sleep(5)
            connection.close()
            time.sleep(180)
        else:
            print("ISS is at None Location")
    else:
        if iss_location is not None:
            connection.sendmail(from_addr=email,
                                to_addrs=to_email,
                                msg=msg.as_string())
            print("Mail Sent!")
            print("Day Time: Sleeping for 1 hour")
            time.sleep(5)
            connection.close()
            time.sleep(3480)
        else:
            print("ISS is at None Location")
    print("Next Detection in 2 minutes")
    print()
    time.sleep(120)
