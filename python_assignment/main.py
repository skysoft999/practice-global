import pytz
import redis
import datetime
from ast import literal_eval
from kafka import KafkaConsumer
# from pymongo import MongoClient
from json import loads, dumps, load, dump
from statistics import mean
import pandas as pd
from os import path


r = redis.Redis()
# client = MongoClient('localhost:27017')
# collection = client.test.test


def main():
    """ main landing function
        - 5 minute segmented data
        - 30 minutes interval
        - create json and csv
    """
    time_segment = 5*60
    consumer = KafkaConsumer(
        'sensor_stream',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='my-group',
        value_deserializer=lambda x: loads(x.decode('utf-8')),
        consumer_timeout_ms=2000
    )

    for message in consumer:
        messages = message.value
        # print(f"message {message}")
        if messages:
            process_data(messages, time_segment)

    consumer.close()
    print("Main Program Excited")


def process_data(message, time_segment):
    try:
        data_hash = "sensor_data"
        user_data = r.hget(data_hash, message.get("user_id"))
        HR_list, RR_list = [], []
        data = dict()
        patient_list = r.get("patient_list")
        if patient_list:
            patient_list = loads(patient_list)
            patient_list.append(message.get('user_id'))
        else:
            patient_list = []
            patient_list.append(message.get('user_id'))
        patient_list = list(set(patient_list))
        r.set("patient_list", dumps(patient_list))

        if not user_data:
            # starting time
            upt = int(datetime.datetime.now(tz=pytz.utc).timestamp())
            print(f"uptime set {upt}")
            r.set("up_time", upt)

            HR_list.append(int(message.get("heart_rate")))
            RR_list.append(int(message.get("respiration_rate")))
            data["HR"] = HR_list
            data["RR"] = RR_list
            data["start_hour"] = int(message.get("timestamp"))
            data["tz"] = message.get("timezone_offset")
            data["activity"] = message.get("activity")
            data["end_hour"] = int(message.get("timestamp")) + time_segment
            data = dumps(data)
            r.hset(data_hash, message.get("user_id"), data)
        else:
            user_data = loads(user_data)
            HR_list = user_data.get("HR")
            RR_list = user_data.get("RR")
            HR_list.append(int(message.get("heart_rate")))
            RR_list.append(int(message.get("respiration_rate")))
            user_data["RR"] = RR_list
            user_data["HR"] = HR_list
            user_data = dumps(user_data)
            r.hset(data_hash, message.get("user_id"), user_data)

        up_time = literal_eval(r.get("up_time").decode('utf-8'))
        time_utc = int(datetime.datetime.now(tz=pytz.utc).timestamp())
        if abs(up_time - time_utc) == time_segment:
            do_calc(data_hash)
    except Exception as e:
        print(f"Exception at process_data function {e}")


def do_calc(data_hash):
    patient_list = loads(r.get("patient_list"))
    print(f"patient list docalc {patient_list}")
    data = []
    if patient_list:
        for patient_id in patient_list:
            redis_data = r.hget(data_hash, patient_id)
            redis_data = loads(redis_data)
            HR_list = redis_data.get("HR")
            RR_list = redis_data.get("RR")
            data_op = dict()
            data_op["user_id"] = patient_id
            data_op["start_ts"] = redis_data.get("start_hour")
            data_op["end_ts"] = redis_data.get("end_hour")
            data_op["tz"] = redis_data.get("tz")
            data_op["avg_hr"] = round(mean(HR_list),2)
            data_op["min_hr"] = round(min(HR_list),2)
            data_op["max_hr"] = round(max(HR_list), 2)
            data_op["avg_rr"] = round(mean(RR_list), 2)
            
            if path.exists("response.json"):
                with open('response.json') as json_file:
                    data = load(json_file)
                data.append(data_op)
                with open('response.json', 'w') as outfile:
                    dump(data, outfile)
            else:
                data.append(data_op)
                with open('response.json', 'w') as outfile:
                    dump(data, outfile)
    create_csv()
    r.delete("sensor_data")
    print("Sensor Cached Data Deleted")


def create_csv():
    df = pd.read_json("response.json")
    df.to_csv('response.csv', index=None, header=True)
    print("Response CSV created")


if __name__ == "__main__":
    print("Main Script Started")
    main()
    print("Main Script Stopped")


