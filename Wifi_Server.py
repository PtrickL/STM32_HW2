# gyro_server_plot.py
import socket, threading, queue, time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from IPython.display import display, clear_output


HOST = '192.168.50.210'
PORT = 8002

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

print(f"Listening on {HOST}:{PORT} ...")
conn, addr = s.accept()
print("Connected by", addr)

# --- Plot setup ---
plt.ion()
fig, ax = plt.subplots(figsize=(8,4))

WINDOW_SIZE = 50  # number of points in the sliding window

time_vals = deque(maxlen=WINDOW_SIZE)
x_vals = deque(maxlen=WINDOW_SIZE)
y_vals = deque(maxlen=WINDOW_SIZE)
z_vals = deque(maxlen=WINDOW_SIZE)

line_x, = ax.plot([], [], label="X")
line_y, = ax.plot([], [], label="Y")
line_z, = ax.plot([], [], label="Z")

ax.legend()
ax.set_xlabel("Time (s)")
ax.set_ylabel("Acceleration")
ax.set_title("Live Accelerometer Data")
ax.grid(True)
fig.show()
fig.canvas.draw()

# --- Main loop ---
while True:
    data = conn.recv(1024)
    if not data:
        break

    for line in data.decode(errors="ignore").splitlines():
        try:
            t, x, y, z = line.split(",")
            t = int(t)
            x, y, z = float(x), float(y), float(z)

            # append to sliding window
            time_vals.append(t/1000.0)
            x_vals.append(x)
            y_vals.append(y)
            z_vals.append(z-1024)

            # update line data
            line_x.set_data(time_vals, x_vals)
            line_y.set_data(time_vals, y_vals)
            line_z.set_data(time_vals, z_vals)

            # adjust x-axis to show only sliding window
            if len(time_vals) > 1:
                ax.set_xlim(time_vals[0], time_vals[-1])
            ax.relim()
            ax.autoscale_view(scalex=False, scaley=True)  # only y-axis auto-scale

            # redraw plot
            fig.canvas.draw()
            fig.canvas.flush_events()
        except ValueError:
            pass