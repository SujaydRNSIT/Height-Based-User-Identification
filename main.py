import network
import time
from hcsr04 import HCSR04
from config import WIFI_SSID, WIFI_PASSWORD
from database import find_person_by_height
from machine import Pin
import urequests as requests

# Firebase Configuration
FIREBASE_URL = "https://esp-32-9c449-default-rtdb.asia-southeast1.firebasedatabase.app/data.json"

def connect_to_wifi(ssid, password):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)

    while not station.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)

    print("Connected to WiFi!")
    print("Network config:", station.ifconfig())

def send_data_to_firebase(height, person):
    data = {
        "Height": height,
        "Person": person,
        "Timestamp": time.time()
    }
    try:
        response = requests.post(FIREBASE_URL, json=data)
        print("Data sent to Firebase:", response.json())
        response.close()
    except OSError as e:
        print("Failed to send data to Firebase:", e)

    # Adding a delay after sending data to Firebase
    time.sleep(2)

def decision_tree(values):
    # Basic decision tree to choose one value out of the top 6
    # Criteria for selection can be modified as needed
    # Here we choose the median value as an example
    sorted_values = sorted(values, reverse=True)
    top_values = sorted_values[:6]
    
    # Example criteria: choose the median of the top 6 values
    median_index = len(top_values) // 2
    selected_value = top_values[median_index]
    
    return selected_value

def main():
    # Connect to WiFi
    connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)

    # Initialize the sensor
    sensor = HCSR04()

    # Get the initial distance measurement
    initial_distance = sensor.distance_cm()
    print("Initial Distance:", initial_distance, "cm")

    previous_distance = initial_distance
    distance_points = [] # Array to store current series of height measurements
    all_data_points = [] # List of lists to store all series of height measurements
    last_trigger_time = time.time()

    while True:
        # Get the current distance reading
        current_distance = sensor.distance_cm()

        # Calculate the height
        Height = initial_distance - current_distance

        # Check if the height is less than 100 cm and ignore the trigger if so
        if Height < 100:
            previous_distance = current_distance
            continue # Skip further processing if height is less than 100 cm

        # Check if the distance has changed by more than 15 cm from the initial reading
        # and the change from the previous reading is greater than 1 cm
        if abs(current_distance - initial_distance) > 15 and abs(current_distance - previous_distance) > 1:
            person = find_person_by_height(Height)

            if person != "Unknown":
                print("Triggered! Height:", Height, "cm", "| Identified as:", person)
            else:
                print("Triggered! Height:", Height, "cm")

            # Send data to Firebase
            send_data_to_firebase(Height, person)

            # Update the previous distance and store the height measurement
            previous_distance = current_distance
            distance_points.append(Height) # Store height in the array
            last_trigger_time = time.time() # Update the time of last trigger

        # Check if no trigger detected for more than 5 seconds
        if time.time() - last_trigger_time > 5:
            if distance_points:
                # Add the current series of height measurements to the list of all data points
                all_data_points.append(distance_points)
                
                # Run decision tree to select one value from the top 6 height measurements
                selected_value = decision_tree(distance_points)
                print("Selected Value from top 6 height measurements:", selected_value)
                
                distance_points = [] # Start a new series
                print("New series of height measurements collected:", all_data_points)

            last_trigger_time = time.time() # Reset the last trigger time

        time.sleep(0.1) # Small delay to avoid too frequent polling

if __name__ == "__main__":
    main()