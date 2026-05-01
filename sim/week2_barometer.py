import numpy as np
import matplotlib.pyplot as plt

T = 15  # Newton
cutoff_t = 5  # cutoff time
m = 1  # kilogram
g = 9.81  # m/s²
tot_time = 15  # seconds
dt = 1e-3
time = np.linspace(0, tot_time, int(tot_time / dt), retstep=False)
print(len(time))
h = []
v = []
h_euler = [0.0 for i in range(len(time))]
v_euler = [0.0 for i in range(len(time))]
sigma = 0.5 # cheap baro
bias = 1.5 # meters for baro
noise = np.random.normal(0, sigma, len(time))

# Analytical solution
for t in time:
    if t < 5:
        v.append(5.19 * t)
        h.append((1 / 2) * 5.19 * t**2)
    else:
        tau = t - 5
        v.append(25.95 - g * tau)
        h.append(64.875 + 25.95 * tau - (1 / 2) * g * tau**2)

h_baro = np.array(h) + np.array([bias]*len(time)) + noise

### Plots

fig, ax = plt.subplots(figsize=(10, 6), sharex=True, tight_layout=True, dpi=100)

# Height
ax.plot(time, h, color="red", lw=2, label="Height Analytical")
ax.plot(time, h_baro, color="green", lw=1, label="Height Barometer")

ax.set_xlabel("Time (s)")
ax.set_ylabel("Height")
ax.set_ylim(bottom=0)
ax.legend(loc="upper left")

plt.show()
