from flask import Flask, request
import requests
import time

app = Flask(__name__)

# Replace with your WLED device's IP address
WLED_IP = "192.168.1.2"

bomb_planted = False  # Global variable

# Function to set a WLED preset
def set_wled_preset(preset_id):
    url = f"http://{WLED_IP}/json/state"
    data = {
        "ps": preset_id  # Activate the preset
    }
    requests.post(url, json=data)

# Function to set a new WLED effect
def set_wled_effect(effect_id, color):
    url = f"http://{WLED_IP}/json/state"
    data = {
        "on": True,
        "seg": [{"fx": effect_id, "col": [color]}],  # Apply effect and color
        "bri": 255
    }
    requests.post(url, json=data)

# Function to restore the previous WLED state
def restore_wled_state(previous_state):
    if previous_state:
        url = f"http://{WLED_IP}/json/state"
        requests.post(url, json=previous_state)

# Main function to handle CS:GO round wins
@app.route('/cs2-wled', methods=['POST'])
def csgo_event():
    global bomb_planted  # Declare bomb_planted as global so we can modify it    
    data = request.json

    print(data)

    if data:
        round_data = data.get("round", {})

        # Handle round win event
        win_team = round_data.get("win_team")        
        if win_team:  # If a team won the round
            print(f"Round won by: {win_team}")
            bomb_planted = False  # Reset the bomb_planted flag
            # Set WLED preset based on the winning team
            if win_team == "T":  # Terrorists Win
                set_wled_preset(5)  # Replace with your T-side preset ID
            elif win_team == "CT":  # Counter-Terrorists Win
                set_wled_preset(6)  # Replace with your CT-side preset ID

            # Wait for 6 seconds (for effect)
            time.sleep(6)

            # Restore the previous WLED preset
            set_wled_preset(1)
            return "OK", 200

        bomb_data = round_data.get("bomb")
        
        if bomb_data == "planted" and bomb_planted == False:
            print(f"Bomb planted!")
            bomb_planted = True  # Modify the global bomb_planted variable

            # Set bomb-related WLED effects
            set_wled_preset(7)  # Replace with your bomb planting preset ID
            time.sleep(30)

            if bomb_planted == True:
                set_wled_preset(8)  # Effect for the bomb ticking down
                time.sleep(5)
            if bomb_planted == True:
                set_wled_preset(9)  # Different effect when nearing end
                time.sleep(5)
            if bomb_planted == True:
                set_wled_preset(10)  # Final countdown effect
                time.sleep(5)

    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)