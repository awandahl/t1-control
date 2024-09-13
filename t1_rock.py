import time
import subprocess
import gpiod

# GPIO configuration
CHIP = 'gpiochip0'  # You might need to change this based on your setup
TUNE_PIN = 17  # Replace with actual GPIO number
DATA_PIN = 18  # Replace with actual GPIO number

# Rigctl configuration
RIG_MODEL = "2002"  # TS-440S for QRP Labs QDX. Replace with your radio's model number
RIG_PORT = "/dev/ttyACM0"  # Replace with your actual port

chip = gpiod.Chip(CHIP)
tune_line = chip.get_line(TUNE_PIN)
data_line = chip.get_line(DATA_PIN)

def gpio_setup():
    tune_line.request(consumer="T1_control", type=gpiod.LINE_REQ_DIR_OUT)
    data_line.request(consumer="T1_control", type=gpiod.LINE_REQ_DIR_IN)

def gpio_cleanup():
    tune_line.release()
    data_line.release()

def gpio_output(pin, value):
    if pin == TUNE_PIN:
        tune_line.set_value(value)

def gpio_input(pin):
    if pin == DATA_PIN:
        return data_line.get_value()

def get_frequency():
    """Get current frequency from the radio using rigctl."""
    try:
        result = subprocess.run(['rigctl', '-m', RIG_MODEL, '-r', RIG_PORT, 'f'], 
                                capture_output=True, text=True, check=True)
        return int(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error getting frequency: {e}")
        return None

def frequency_to_band(freq):
    """Convert frequency to band ID."""
    bands = [
        (1800000, 2000000, 1),   # 160m
        (3500000, 4000000, 2),   # 80m
        (5330500, 5405000, 3),   # 60m
        (7000000, 7300000, 4),   # 40m
        (10100000, 10150000, 5), # 30m
        (14000000, 14350000, 6), # 20m
        (18068000, 18168000, 7), # 17m
        (21000000, 21450000, 8), # 15m
        (24890000, 24990000, 9), # 12m
        (28000000, 29700000, 10),# 10m
        (50000000, 54000000, 11) # 6m
    ]
    for low, high, band_id in bands:
        if low <= freq <= high:
            return band_id
    return 0  # Unknown band

def send_bit(bit):
    """Send a single bit to the T1."""
    gpio_output(TUNE_PIN, 1)
    time.sleep(0.004 if bit else 0.0015)  # 4ms for '1', 1.5ms for '0'
    gpio_output(TUNE_PIN, 0)
    time.sleep(0.0015)  # 1.5ms low between bits

def send_band(band):
    """Send band information to the T1."""
    # Activate tuner
    gpio_output(TUNE_PIN, 1)
    time.sleep(0.5)
    gpio_output(TUNE_PIN, 0)

    # Wait for T1 response
    while gpio_input(DATA_PIN) == 0:
        time.sleep(0.001)
    while gpio_input(DATA_PIN) == 1:
        time.sleep(0.001)

    time.sleep(0.01)  # Wait 10ms

    # Send 4-bit band ID
    for i in range(3, -1, -1):
        send_bit((band >> i) & 1)

    gpio_output(TUNE_PIN, 0)

def main():
    gpio_setup()
    prev_band = None
    try:
        print(f"Starting T1 control for Armbian")
        print(f"Rig model: {RIG_MODEL}, Port: {RIG_PORT}")
        while True:
            freq = get_frequency()
            if freq is not None:
                band = frequency_to_band(freq)
                if band != prev_band:
                    print(f"Frequency: {freq} Hz, Band: {band}")
                    send_band(band)
                    prev_band = band
            time.sleep(5)  # Check every 5 seconds
    except KeyboardInterrupt:
        print("Program terminated by user")
    finally:
        gpio_cleanup()

if __name__ == "__main__":
    main()
