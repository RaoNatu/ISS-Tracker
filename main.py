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
        # data_iss_location = requests.get(f"https://us1.locationiq.com/v1/reverse.php?key={api_key}"
        #                                  f"&lat={latitude}&lon={longitude}&format=json").json()

        data_iss_location = requests.get("https://api.bigdatacloud.net/data/reverse-geocode-client?"
                                         f"latitude={latitude}&longitude={longitude}&localityLanguage=en").json()

        # data_iss_location = requests.get("https://api.bigdatacloud.net/data/reverse-geocode-client?"
        #                                  "latitude=37.42159&longitude=-122.0837&localityLanguage=en").json()

        iss_location_info = ""
        if data_iss_location["localityInfo"]["administrative"]:
            for i in range(0, 4):
                iss_location_info += data_iss_location["localityInfo"]["administrative"][i]["name"] + ", "
        else:
            print("Entering Else")
            iss_location_info = data_iss_location["localityInfo"]["informative"][0]["name"] + ", "
        print(iss_location_info[0:-2])
        return iss_location_info[0:-2]
    except KeyError:
        pass


def send_mail(text=""):
    connection = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    connection.login(email, password)
    msg = MIMEText(f"International Space Station is at: {iss_location}\n\n"
                   f"Longitude: {longitude}\n\nLatitude: {latitude}\n\n{text}")
    msg["Subject"] = "ISS Tracker"
    msg["From"] = email
    msg["To"] = to_email
    try:
        connection.sendmail(from_addr=email,
                            to_addrs=to_email,
                            msg=msg.as_string())
        print("Mail Sent!")
        connection.close()
    except Exception as e:
        print(f"Mail not Sent: {e}")


load_dotenv()
email = os.environ["EMAIL"]
password = os.environ["PASSWORD"]
# api_key = os.environ["API_KEY"]
to_email = "raoshreyayadav@yahoo.com"   # Receiver Email

while True:
    iss_location = get_location()
    if is_iss_overhead() and is_night():
        send_mail("In Your Area! Look Above ☝️")
        time.sleep(7080)
    elif is_night():
        if iss_location is not None:
            print("Night Time: Next Detection in 30 minutes")
            send_mail("It's Night Time! May get a chance to see ISS.")
            time.sleep(1180)
        else:
            print("ISS is at None Location")
    else:
        if iss_location is not None:
            print("Day Time: Next Detection in 2 hours")
            send_mail("Next message in 2 hours")
            time.sleep(7080)
        else:
            print("ISS is at None Location")
    print("Next Detection in 2 minutes")
    print()
    time.sleep(120)
