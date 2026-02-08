
'''
example format that the generator will output
{"timestamp":"2026-02-08T09:00:00Z","level":"ERROR","service":"auth","message":"Invalid token","request_id":"req-001"}
'''

import random
import datetime
import json

start_time = datetime.datetime(2026,2,8,9,00)
level_list = ["ERROR", "WARN", "INFO"]
service_list = ["auth","api","worker","default"]
messages = {"auth":["Login attempt","Invalid token","Successful login"],"api":["Slow response","Request started", "Request completed"],"worker":["Job started","Job completed"],"default":["default message response"]}

with open("sample_logs_v2.jsonl", "w") as log_file:

    

    
    new_time = start_time + datetime.timedelta(minutes=3)
    end_time = start_time + datetime.timedelta(hours=2)

    while new_time < end_time:
        data = {}
        new_time = new_time + datetime.timedelta(minutes=1)
        selected_time = new_time.isoformat(timespec="seconds") + "Z"
        selected_level = level_list[random.randint(0,(len(level_list)-1))]
        selected_service = service_list[random.randint(0,(len(service_list)-1))]
        selected_message = messages[selected_service][random.randint(0,len(messages[selected_service])-1)]

        data["timestamp"] = selected_time
        data["level"] = selected_level
        data["service"] = selected_service
        data["message"] = selected_message
        data["request_id"] = f"req-{random.randint(1,999)}"
        json.dump(data, log_file)
        log_file.write("\n")
    



