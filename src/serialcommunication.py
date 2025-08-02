import serial
import time
import threading
from pynput.mouse import Listener

# Open serial connection to ESP32-CAM (replace COM3 if needed)
ser = serial.Serial('COM3', 115200, timeout=1)  # match baud with ESP32-CAM
time.sleep(2)  # Allow time for ESP32 to reset

# Track last mouse position
last_x = None
last_y = None

# Serial read thread
def read_serial():
    while ser.is_open:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"[ESP32] {line}")
        except Exception as e:
            print(f"Serial read error: {e}")
            break

# Start serial read in background
serial_thread = threading.Thread(target=read_serial, daemon=True)
serial_thread.start()

def on_move(x, y):
    global last_x, last_y
    if last_x is None:
        last_x = x
        return
    if last_y is None:
        last_y = y
        return

    xmoved = 0
    ymoved = 0

    if x > last_x + 5:
        xmoved = 1
        last_x = x
    elif x < last_x - 5:
        xmoved = -1
        last_x = x

    if y > last_y + 5:
        ymoved = 1
        last_y = y
    elif y < last_y - 5:
        ymoved = -1
        last_y = y

    # Map (xmoved, ymoved) to command A-I
    arr = [(0,0), (1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1)]
    data = 'A'
    for (mx, my) in arr:
        if mx == xmoved and my == ymoved:
            # data = 'B'
            print(f"[PC->ESP32] Sending: {data}")
            ser.write(data.encode('utf-8'))
            break
        data = chr(ord(data) + 1)

def on_click(x, y, button, pressed):
    pass

def on_scroll(x, y, dx, dy):
    pass

try:
    print("Move your mouse to control. Ctrl+C to stop.")
    with Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
        listener.join()
except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    if ser.is_open:
        ser.close()
    print("Serial port closed.")
