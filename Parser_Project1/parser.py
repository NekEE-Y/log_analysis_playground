import json


# log parsing function, extracts only valid json events meetings the requirements
def parselogs(logfile):
    with open(logfile, "r") as file:
        data = []
        required_fields = ('timestamp', 'level', 'service', 'message')
        parsing_errors = {"VALID_JSON_WRONG_SHAPE":0 , "MALFORMED_JSON": 0, "INCOMPLETE_JSON": 0}
        for count,line in enumerate(file,1):
            try:
                line_content = json.loads(line)
                if isinstance(line_content,dict):
                    json_format_is_good = True
                    for element in required_fields:
                        if element in line_content:
                            pass
                        else:
                            json_format_is_good = False
                            break
                    if json_format_is_good: 
                        data.append(line_content)
                    else: 
                        parsing_errors["INCOMPLETE_JSON"] += 1 
                else:
                    parsing_errors["VALID_JSON_WRONG_SHAPE"] += 1
            except json.JSONDecodeError:
                parsing_errors["MALFORMED_JSON"] += 1
    return data, parsing_errors


# only extracts warning and error messages from the data we have
def error_warn_extraction(data):
    relevant_events = []
    for entry in data:
        if entry["level"].lower().startswith("warn") or entry["level"].lower() == "error":
            relevant_events.append(entry)

    return relevant_events


# building a final report to present event impacts
def final_report(relevant_events):
    summarized_event_counts = {"errors":0, "warnings":0}
    for event in relevant_events:
        if event["level"].lower().startswith("warn"):
            summarized_event_counts["warnings"] += 1
        elif event["level"].lower() == "error":
            summarized_event_counts["errors"] += 1

    relevant_messages = {}
    relevant_services = {}
    
    for event in relevant_events:
        if event["message"] not in relevant_messages:
            relevant_messages[event["message"]] = 1
        else:
            relevant_messages[event["message"]] += 1
        
        if event["service"] not in relevant_services:
            relevant_services[event["service"]] = 1 
        else: 
            relevant_services[event["service"]] += 1
    
    return summarized_event_counts, sorted(relevant_messages.items(), key= lambda x: x[1], reverse=True), sorted(relevant_services.items(), key= lambda x: x[1], reverse=True)


# main execution loop and output
def main():
    data, parsing_errors = parselogs("sample_logs.jsonl")
    relevant_events = error_warn_extraction(data)
    summarized_event_counts, important_messages, impacted_services = final_report(relevant_events)

    print(f"During parsing of the file the following parsing errors were encountered: \n")
    for x in parsing_errors.items():
        print(x[0],": ",x[1])
    print(f"\nThere were {len(relevant_events)} significant events identified. \n") 
    print(f"The summary of these events is below: \n")
    print("Event counts: \n")
    for x in summarized_event_counts.items():
        print(x[0],": ",x[1])
    print("Significant Messages: \n")
    for x in important_messages:
        print(x[0],": ",x[1], "events")
    print("\nMost Impacted Services: \n")
    for x in impacted_services:
        print(x[0],": ",x[1], "events")

if __name__=="__main__":
    main()






        


