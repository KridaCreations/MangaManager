import socket
import numpy as np
import cv2
import threading
from collections import defaultdict
from pynput.mouse import Listener
import time

# --- Config ---
VIDEO_UDP_IP = "0.0.0.0"
VIDEO_UDP_PORT = 1234
CONTROL_UDP_IP = "192.168.1.5"  # Change to your ESP32 IP
CONTROL_UDP_PORT = 4321
PACKET_SIZE = 1024 + 4
TIMEOUT = 0.5

# --- State ---
stop_event = threading.Event()
last_x = None
last_y = None
control_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def video_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((VIDEO_UDP_IP, VIDEO_UDP_PORT))
    sock.settimeout(TIMEOUT)

    frame_buffer = defaultdict(dict)
    frame_sizes = {}
    last_frame = -1

    print("Receiving UDP stream...")

    try:
        while not stop_event.is_set():
            try:
                data, _ = sock.recvfrom(PACKET_SIZE)
                if len(data) < 4:
                    continue

                frame_id = (data[0] << 8) | data[1]
                total = data[2]
                index = data[3]
                payload = data[4:]

                frame_buffer[frame_id][index] = payload
                if frame_id not in frame_sizes:
                    frame_sizes[frame_id] = total

                if len(frame_buffer[frame_id]) == total:
                    try:
                        jpeg_data = b''.join([frame_buffer[frame_id][i] for i in range(total)])
                        img_np = np.frombuffer(jpeg_data, dtype=np.uint8)
                        frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
                        if frame is not None:
                            cv2.imshow("ESP32-CAM Stream", frame)
                            if cv2.waitKey(1) == 27:  # ESC
                                stop_event.set()
                    except:
                        pass
                    last_frame = frame_id
                    del frame_buffer[frame_id]
                    del frame_sizes[frame_id]

            except socket.timeout:
                continue
    except Exception as e:
        print("Video thread error:", e)
    finally:
        sock.close()
        cv2.destroyAllWindows()
        print("[Video] Stopped")

def on_move(x, y):
    global last_x, last_y
    if last_x is None:
        last_x = x
        last_y = y
        return

    dx = x - last_x
    dy = y - last_y
    last_x = x
    last_y = y

    if dx != 0 or dy != 0:
        try:
            control_sock.sendto(bytes([dx & 0xFF, dy & 0xFF]), (CONTROL_UDP_IP, CONTROL_UDP_PORT))
        except:
            pass

def main():
    print("Starting threads...")
    video_thread = threading.Thread(target=video_receiver, daemon=True)
    video_thread.start()

    mouse_listener = Listener(on_move=on_move)
    mouse_listener.start()

    print("Press Ctrl+C to stop...")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[INFO] Ctrl+C detected — shutting down...")
        stop_event.set()

    mouse_listener.stop()
    control_sock.close()
    print("Shutdown complete.")

if __name__ == "__main__":
    main()
