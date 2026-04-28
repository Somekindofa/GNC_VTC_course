from ast import List
from functools import total_ordering
import math
import numpy as np
import matplotlib.pyplot as plt
import mplcursors

T = 15  # Newton
cutoff_t = 5  # cutoff time
m = 1  # kilogram
g = 9.81  # m/s²
tot_time = 15  # seconds
dt = 1e-3
time = np.linspace(0, tot_time, int(tot_time / dt))
print(len(time))
h = []
v = []
h_euler = [0.0 for i in range(len(time))]
v_euler = [0.0 for i in range(len(time))]

# Analytical solution
for t in time:
    if t < 5:
        v.append(5.19 * t)
        h.append((1 / 2) * 5.19 * t**2)
    else:
        t = t - 5
        v.append(25.95 - g * t)
        h.append(64.875 + 25.95 * t - (1 / 2) * g * t**2)

# Forward Euler
for t in range(len(time) - 1):
    if time[t] >= cutoff_t:
        T = 0
    v_euler[t + 1] = v_euler[t] + dt * (T - m * g) / m
    h_euler[t + 1] = h_euler[t] + dt * v_euler[t]

# Speed
fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True, tight_layout=True, dpi=100)
ax[0].plot(time, v, color="red", lw=2, label="Speed Analytical")
ax[0].plot(time, v_euler, color="blue", lw=1, ls="--", label="Speed Euler")

ax[0].set_xlabel("Time (s)")
ax[0].set_ylabel("Speed")
ax[0].legend(loc="upper left")

# Height
ax[1].plot(time, h, color="red", lw=2, label="Height Analytical")
ax[1].plot(time, h_euler, color="blue", lw=1, ls="--", label="Height Euler")

ax[1].set_xlabel("Time (s)")
ax[1].set_ylabel("Height")
ax[1].legend(loc="upper left")
mplcursors.cursor(hover=True)
plt.show()

error_height = abs(np.nanmean((np.array(h) - np.array(h_euler))/np.array(h)))*100
error_speed = abs(np.nanmean((np.array(v) - np.array(v_euler))/np.array(v)))*100

print("Error% Height:", error_height)
print("Error% Speed:", error_speed)