from flask import Flask, request
import requests
import time
from threading import Timer

app = Flask(__name__)

# Replace with your WLED device's IP address
WLED_IP = "192.168.1.2"

bomb_planted = False  # Global variable

yellowTimer = None
redTimer = None
roundEndDefaultPresetTimer = None

server_round_phase = None

# Start timers for the bomb countdown effects
def start_yellow_timer():
    global yellowTimer
    if yellowTimer is None:
        yellowTimer = Timer(30.0, lambda: set_wled_preset(8))  # Yellow warning at 30s
        yellowTimer.start()
        print("Yellow timer started (30s)")

def start_red_timer():
    global redTimer
    if redTimer is None:
        redTimer = Timer(35.0, lambda: set_wled_preset(9))  # Red warning at 35s
        redTimer.start()
        print("Red timer started (35s)")

# Stop the timers if the round ends
def stop_yellow_timer():
    global yellowTimer
    if yellowTimer is not None:
        yellowTimer.cancel()
        yellowTimer = None
        print("Yellow timer stopped")

def stop_red_timer():
    global redTimer
    if redTimer is not None:
        redTimer.cancel()
        redTimer = None
        print("Red timer stopped")

def start_round_end_default_preset_timer():
    global roundEndDefaultPresetTimer
    stop_round_end_default_preset_timer()  # Ensure no existing timer is running
    roundEndDefaultPresetTimer = Timer(6.0, lambda: set_wled_preset(1))
    roundEndDefaultPresetTimer.start()
    print("Round end timer started (6s)")

def stop_round_end_default_preset_timer():
    global roundEndDefaultPresetTimer
    if roundEndDefaultPresetTimer is not None:
        roundEndDefaultPresetTimer.cancel()
        roundEndDefaultPresetTimer = None
        print("Round end timer stopped")

# Function to set a WLED preset
def set_wled_preset(preset_id):
    url = f"http://{WLED_IP}/json/state"
    data = {"ps": preset_id}  # Activate the preset
    headers = {"Content-type": "application/json"}
    
    max_retries = 5  # Retry up to 5 times
    retry_delay = 0.1   # Wait 2 seconds between retries

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(url, json=data, headers=headers, timeout=0.5)
            response.raise_for_status()  # Raise an error for HTTP errors (4xx, 5xx)

            print(f"WLED preset {preset_id} set successfully!")
            return True  # Success, exit function

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt} failed: {e}")

            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Failed to set WLED preset.")

    return False  # If all retries fail

# Main function to handle CS:GO round wins
@app.route('/cs2-wled', methods=['POST'])
def csgo_event():
    global bomb_planted  # Declare bomb_planted as global so we can modify it   
    global server_round_phase
    data = request.json

    print(data)

    if data:
        round_data = data.get("round", {})
        round_phase = round_data.get("phase")

        # Handle round win event
        win_team = round_data.get("win_team")        
        if win_team:  # If a team won the round
            print(f"Round won by: {win_team}")            
            print(f"server_round_phase: {server_round_phase}")
            if round_phase != server_round_phase: # Only run this is the server's last phase was not over
                server_round_phase = round_phase
                bomb_planted = False  # Reset the bomb_planted flag

                stop_yellow_timer()  # Stop countdown timers
                stop_red_timer()
                stop_round_end_default_preset_timer()
                
                # Set WLED preset based on the winning team
                if win_team == "T":  # Terrorists Win
                    set_wled_preset(5)  # Replace with your T-side preset ID
                elif win_team == "CT":  # Counter-Terrorists Win
                    set_wled_preset(6)  # Replace with your CT-side preset ID

                start_round_end_default_preset_timer()

                # Wait for 6 seconds (for effect)
                #time.sleep(6)

                # Restore the previous WLED preset
                #set_wled_preset(1)

            return "OK", 200

        server_round_phase = round_phase

        bomb_data = round_data.get("bomb")
        
        if bomb_data == "planted" and bomb_planted == False:
            print(f"Bomb planted!")
            bomb_planted = True  # Modify the global bomb_planted variable           
            
            # Start countdown timers
            start_yellow_timer()
            start_red_timer()

            # Set bomb-related WLED effects
            set_wled_preset(7)

    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)