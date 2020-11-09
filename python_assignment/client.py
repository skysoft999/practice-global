# client file simulate Sensor Module

import datetime
import pytz
from json import dumps
import random
from kafka import KafkaProducer
from time import sleep


def client_main():
    """ Main function for Client start up"""
    try:
        producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                                 value_serializer=lambda x:
                                 dumps(x).encode('utf-8'))

        start_time = int(datetime.datetime.now(tz=pytz.utc).timestamp())
        hour_max = 30 * 60
        delay_sec = 1
        print("*************sensor Started sending signal***************")
        while start_time:
            nowt = datetime.datetime.now()
            print(f"time now client side: {nowt}")
            pat1 = generate_client("patient1", 3, 5.5)
            pat2 = generate_client("patient2", 30, -4)
            # data = [pat1, pat2]
            producer.send('sensor_stream', value=pat1)
            producer.send('sensor_stream', value=pat2)
            # loop break condition
            now_time = int(datetime.datetime.now(tz=pytz.utc).timestamp())
            if abs(start_time - now_time) == hour_max:
                print(f"Sensor stop sending Data @ {now_time}")
                break
            sleep(delay_sec)
        print("--------------sensor Stopped sending signal-----------------")
    except Exception as e:
        print(f"Exception at client main: {e}")



def generate_client(user_id, activity, tz):
    """generate patient data dynamically """
    patient_data = dict()
    patient_data["user_id"] = user_id
    patient_data["heart_rate"] = random.randint(40, 100)
    patient_data["respiration_rate"] = random.randint(11, 30)
    patient_data["activity"] = activity
    patient_data["timezone_offset"] = tz
    utctime = int(datetime.datetime.now(tz=pytz.utc).timestamp())
    tz_time = utctime + int(tz * 60 * 60)
    patient_data["timestamp"] = tz_time
    return patient_data


if __name__ == "__main__":
    print("Client Started")
    client_main()
    print("closed main program")
