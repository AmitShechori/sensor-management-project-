
import random 
import uuid
import json
import csv
import time
import logging
from datetime import datetime
from sensors import Sensor

logging.basicConfig(filename= 'errors.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EventManager:
    def create_event(self,sensor: Sensor) -> dict:
        if sensor.battery_level <= 0:
            error_msg = f"Cannot access sensor {sensor.sensor_id} - Battery DEAD"
            logging.error(error_msg) # זה ייכנס לקובץ errors.log
            print(f"Error: {error_msg}")
            return None
        current_battery = sensor.battery_level 

        chance = random.random()
        if chance < 0.05:
            sampled_value = round(random.uniform(-50, -200), 2)
            logging.warning(f"Sensor {sensor.sensor_id} ({sensor.location}): Hardware error - Extreme low value detected: {sampled_value}.")
        elif chance < 0.1:
            sampled_value = round(random.uniform(50, 200), 2)
            logging.warning(f"Sensor {sensor.sensor_id} ({sensor.location}): Hardware error - Extreme high value detected: {sampled_value}.")
        elif chance < 0.12:
            sampled_value = "ERR_DATA_CORRUPT"
            logging.error(f"Sensor {sensor.sensor_id} ({sensor.location}): Data corruption - Non-numeric value received")      
        else:  
            # Create a random value (with some offset to test min/max)
            sampled_value = round(random.uniform(sensor.min_val -5, sensor.max_val + 5), 2)
        
        
        # Get status from sensor 
        status = sensor.validate_value(sampled_value)
        # Battery drop: decrease by 1 each time we read data
        
        sensor.battery_level -= 1
          
        if 0 < sensor.battery_level <= 10 :
            print(f"ALERT! Sensor {sensor.sensor_id} battery is low ({sensor.battery_level}%). Please replace soon!")     
        elif sensor.battery_level == 0: 
            print(f"NOTICE: sensor {sensor.sensor_id} just ran out of battery!")
        # Create the event dictionary with all info    
        event = {
            "event_id": str(uuid.uuid4()), #Unique ID for each log
            "sensor_id": sensor.sensor_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "location": sensor.location,
            "value" : sampled_value,
            "status": status,
            "battery_level": f"{current_battery}%"
        }
        if random.random() < 0.05:
            logging.warning(f"Sensor {sensor.sensor_id} ({sensor.location}): Packet loss - value field missing in transmission")
            del event["value"]
            event["status"] = "ERROR: Missing Value"        
        return event
    

    def run_simulation(self, sensors_list: list, total_seconds: int):
        # Runs the simulation for all sensors and collects all events

        interval = 5
        time_passed = 0
        all_captured_events = []

        print(f"Starting simulation for {total_seconds} seconds. Sample every {interval} seconds.")

        while time_passed <= total_seconds:
                print(F"Sampling at second: {time_passed}")
        
                for sensor in sensors_list:
                    event = self.create_event(sensor)
                    if event:
                      all_captured_events.append(event)
                if time_passed + interval <= total_seconds:        
                    time.sleep(interval)
                    time_passed += interval

                elif time_passed < total_seconds:
                    remainder = total_seconds - time_passed
                    print(f"Waiting for the remainder of {remainder} seconds...")
                    time.sleep(remainder)
                    time_passed += remainder
               
                else:
                    break
                              
           
        print(f"\nSimulation complete. Total time: {time_passed} seconds. Processed {len(all_captured_events)} events.")
        return all_captured_events        
    

    

    def export_each_sensor_to_json(self, events:list):

        sensor_ids = set(e['sensor_id'] for e in events)
        for s_id in sensor_ids:
            sensor_events = [e for e in events if e['sensor_id'] == s_id]
            filename = f"sensor_{s_id}.json"

            with open(filename, 'w') as f:
                json.dump(sensor_events, f, indent=4)
            print(f"Created standalone file: {filename}")



    def export_to_csv(self, events: list, filename: str = "sensor_data.csv"):
        # Save all event data into a CSV file 

        # If there is no data, don't do anything
        if not events:
            return    
        # Get the column names (keys) from the first event
        keys = events[0].keys()
        # Open the file and set up the CSV writer
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader() # Write the top header row
            dict_writer.writerows(events) # Write all the data rows
            
        print(f"Successfully saved to {filename}")

    def validate_event_structure(self, event: dict) -> bool:
        
        # Verify that the event dictionary contains all necessary information,
        
        # List of all keys that MUST be present in every event
        required_fields = ["event_id", "sensor_id", "timestamp", "location", "value", "status", "battery_level"]
        
        for field in required_fields:
            # Check if the key is missing or if the value is empty
            if field not in event or event[field] is None:
                return False
        
        return True # Everything is present    