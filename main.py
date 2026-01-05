import sys
import glob
import os
from sensors import Sensor
from event_manager import EventManager

def main():
    for f in glob.glob("sensor_*.json"):
        try:
            os.remove(f)
        except OSError :
            pass

    manager = EventManager()
    
    # אתחול מחדש של החיישנים עם סוללה מלאה כדי לבדוק שהכל עובד
    sensors = [
        Sensor("Temperature", 1, "Kitchen", 18.0, 25.0,4), # העליתי ל-100
        Sensor("Temperature", 2, "Living Room", 20.0, 24.0, 100),
        Sensor("Temperature", 3, "Bedroom", 16.0, 22.0, 100),
        Sensor("Temperature", 4, "Bathroom", 19.0, 26.0, 100),
        Sensor("Temperature", 5, "Child Room", 19.0, 26.0, 100),
    ]

    if len(sys.argv) < 2:
        print("Usage: python3 main.py <total_seconds>")
        return

    try:
        total_seconds = int(sys.argv[1])
        if total_seconds <= 0:
            raise ValueError("Please provide a positive number of seconds.")

        all_captured_events = manager.run_simulation(sensors, total_seconds)

                                             

        # קריאה לפונקציית השמירה הנפרדת (דרישה 2)אמ
        if all_captured_events:
            manager.export_each_sensor_to_json(all_captured_events)
            manager.export_to_csv(all_captured_events)
        else:
            print("No events were captured, skipping files export.")

    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()



