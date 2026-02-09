'''

logfile for test -> sample_logs_v2.jsonl

'''

from pathlib import Path
from shared.parser import parselogs, error_warn_extraction
from datetime import datetime, timedelta
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"

dateformat = '%Y-%m-%dT%H:%M:%SZ'

# getting logs from user and validating they are useable
log_file = LOGS_DIR / input("provide the log file name to be analyzed: ")
data, parsing_errors = parselogs(log_file)
attempt_counter = 1

while len(data) == 0 and attempt_counter < 5:
    print("There are no useable events in the provided data") 
    user_decision = input("Do you wish to provide another file? y/n").lower()[:1]
    if user_decision == "y":
        log_file = LOGS_DIR / input("provide the log file name to be analyzed: ")
        data, parsing_errors = parselogs(log_file)
        attempt_counter += 1
    else:
        print("Exiting.")
        sys.exit(0)
if len(data) == 0:
    print(f"Max attempts ({attempt_counter}) reached. Exiting")
    sys.exit(0)


#grab relevant info from the parsed logs

def useful_data_from_parsed_logs(data):
    all_valid_events_count = len(data)
    first_event_in_parsed_log = datetime.strptime(data[0]["timestamp"],dateformat)
    last_event_in_parsed_log = datetime.strptime(data[-1]["timestamp"],dateformat)

    return all_valid_events_count, first_event_in_parsed_log, last_event_in_parsed_log




#get start time for analysis
def analysis_start_time(first_event_in_parsed_log, last_event_in_parsed_log):

    print(f"The provided log's first valid event occured at {first_event_in_parsed_log} and the last occured at {last_event_in_parsed_log}.")

    time_window = timedelta(minutes=int(input("Please provide a window (in minutes) before the last timestamp you wish to analyze: ")))

    start_time = last_event_in_parsed_log - time_window

    return start_time


#trim logs around start time
def trim_logs(data,start_time):
    trimmed_logs = []
    for event in data:
        if datetime.strptime(event["timestamp"],dateformat) >= start_time:
            trimmed_logs.append(event)       
    return trimmed_logs

def data_analysis(trimmed_logs):

    all_service_event_tracking={}

    for event in trimmed_logs:

        service = event["service"].lower()
        level = event["level"].lower()

        if service not in all_service_event_tracking:
            all_service_event_tracking[service] = {"total": 0,"error":0, "warn":0,"messages":{}  }

        if level.startswith("warn"):
            all_service_event_tracking[service]["total"] += 1
            all_service_event_tracking[service]["warn"] += 1
        elif level == "error":
            all_service_event_tracking[service]["total"] += 1
            all_service_event_tracking[service]["error"] += 1
        else:
            all_service_event_tracking[service]["total"] += 1
            continue

        if event["message"] not in all_service_event_tracking[service]["messages"]:
            all_service_event_tracking[service]["messages"][event["message"]] = 1
        else:
            all_service_event_tracking[service]["messages"][event["message"]] += 1

    return all_service_event_tracking


def rate_calculation(all_service_event_tracking):

    error_rates = {}
    signal_rates = {}

    for key, value in all_service_event_tracking.items():
        try:
            signal_rate = (value["error"] + value["warn"]) / value["total"]
            error_rate = value["error"] / value["total"]
            error_rates[key] = error_rate
            signal_rates[key] = signal_rate
        except ZeroDivisionError:
            print(f"Error and Signal Rates cannot be calculated. Total number of events for service {key} is zero.\n")
        
    return error_rates, signal_rates


def main():

    all_valid_events_count, first_event_in_parsed_log, last_event_in_parsed_log = useful_data_from_parsed_logs(data)

    start_time = analysis_start_time(first_event_in_parsed_log,last_event_in_parsed_log)
    trimmed_logs= trim_logs(data,start_time)

    while len(trimmed_logs) == 0:
        print("There are no events in the selected timeframe.\n")
        trim_decision = input("Would you like to define another time delta? y/n\n").lower()[:1]
        if trim_decision == "y":
            start_time = analysis_start_time(first_event_in_parsed_log,last_event_in_parsed_log)
            trimmed_logs= trim_logs(data,start_time)
        else:
            print("Exiting based on user input.")
            sys.exit(0)

    print(f"The total number of valid events is: {all_valid_events_count}. They were trimmed down to {len(trimmed_logs)}\n")
    print("Trimming for relevant events within selected timeframe..\n")
    trimmed_relevant_events = error_warn_extraction(trimmed_logs)
    print(f"The total number of identified relevant events in the selected timeframe is: {len(trimmed_relevant_events)}.\n")
    
    all_service_event_tracking = data_analysis(trimmed_logs)
    error_rates, signal_rates = rate_calculation(all_service_event_tracking)

    print(f"Window: {start_time.isoformat()} -> {last_event_in_parsed_log.isoformat()}\n")
    for service,value in all_service_event_tracking.items():
        if value["error"] > 0:
            print(f"CRITICAL {service}, total:{value['total']} error:{value['error']}  warning:{value['warn']}   Error Rate= {round(error_rates[service]*100,ndigits=2)}% Signal Rate = {round(signal_rates[service]*100,ndigits=2)}% Top Message: {max(value['messages'], key=value['messages'].get)}")
        elif value["warn"] > 0:
            print(f"UNHEALTHY {service}, total:{value['total']} error:{value['error']}  warning:{value['warn']}   Error Rate= {round(error_rates[service]*100,ndigits=2)}% Signal Rate = {round(signal_rates[service]*100,ndigits=2)}% Top Message: {max(value['messages'], key=value['messages'].get)}")
        else:
            print(f"OK {service}, total:{value['total']} error:{value['error']}  warning:{value['warn']}   Error Rate= {round(error_rates[service]*100,ndigits=2)}% Signal Rate = {round(signal_rates[service]*100,ndigits=2)}% ")
    


if __name__=="__main__":
    main()

   
    

