import time
import subprocess
import gpiod
import socket
import logging

# Define the GPIO chip and pin numbers
CHIP = 'gpiochip4'
TUNE_PIN = 18  # GPIO4_C2, physical pin 11
DATA_PIN = 22  # GPIO4_C6, physical pin 13

# Set up logging
logging.basicConfig(filename='/home/aw/t1-control/rigctld_errors.log', level=logging.ERROR)

chip = gpiod.Chip(CHIP)
tune_line = chip.get_line(TUNE_PIN)
data_line = chip.get_line(DATA_PIN)

def gpio_setup():
    tune_line.request(consumer="T1_control", type=gpiod.LINE_REQ_DIR_OUT)
    data_line.request(consumer="T1_control", type=gpiod.LINE_REQ_DIR_OUT)

def gpio_cleanup():
    tune_line.release()
    data_line.release()

def gpio_output(pin, value):
    if pin == TUNE_PIN:
        tune_line.set_value(value)
    elif pin == DATA_PIN:
        data_line.set_value(value)

def get_frequency(max_retries=3, retry_delay=1):
    for attempt in range(max_retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)  # Increase timeout to 10 seconds
                s.connect(('localhost', 4532))
                s.sendall(b'f\n')
                response = s.recv(1024).decode().strip()
                if response.startswith('RPRT'):
                    raise ValueError(f"Rigctld returned an error: {response}")
                return int(response)
        except (socket.error, ValueError) as e:
            logging.error(f"Error getting frequency (attempt {attempt+1}/{max_retries}): {e}")
            print(f"Error getting frequency (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
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

def band_to_binary(band):
    return f'{band:04b}'  # Convert the band to a 4-bit binary string

def send_bit(bit):
    """Send a single bit to the T1."""
    gpio_output(DATA_PIN, 1)
    time.sleep(0.004 if bit else 0.0015)  # 4ms for '1', 1.5ms for '0'
    gpio_output(DATA_PIN, 0)
    time.sleep(0.0015)  # 1.5ms low between bits

def send_band(band):
    """Send band information to the T1."""
    binary_representation = band_to_binary(band)
    print(f"Sending band: {band}, Binary: {binary_representation}")

    # Activate tuner
    gpio_output(TUNE_PIN, 1)
    time.sleep(0.5)
    gpio_output(TUNE_PIN, 0)

    # Wait 60ms instead of waiting for T1 response
    time.sleep(0.06)

    # Send 4-bit band ID
    for bit in binary_representation:
        send_bit(int(bit))

    # Final 1.5ms high pulse
    gpio_output(DATA_PIN, 1)
    time.sleep(0.0015)
    gpio_output(DATA_PIN, 0)

    print("Finished sending band information.")

def restart_rigctld():
    print("Attempting to restart rigctld...")
    subprocess.run(['killall', 'rigctld'], check=False)
    time.sleep(1)
    subprocess.Popen(['rigctld', '-m', '2002', '-r', '/dev/ttyACM0', '-t', '4532'])
    time.sleep(2)  # Give rigctld time to start

def main():
    gpio_setup()
    prev_band = None
    consecutive_errors = 0
    try:
        print(f"Starting T1 control for Armbian")
        while True:
            freq = get_frequency()
            if freq is not None:
                consecutive_errors = 0
                band = frequency_to_band(freq)
                if band != prev_band:
                    print(f"Frequency: {freq} Hz, Band: {band}")
                    send_band(band)
                    prev_band = band
            else:
                consecutive_errors += 1
                print(f"Failed to get frequency. Consecutive errors: {consecutive_errors}")
                if consecutive_errors >= 10:
                    restart_rigctld()
                    consecutive_errors = 0
            time.sleep(5)  # Check every 5 seconds
    except KeyboardInterrupt:
        print("Program terminated by user")
    finally:
        gpio_cleanup()

if __name__ == "__main__":
    main()
