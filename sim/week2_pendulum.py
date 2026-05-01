import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray

l = 1
m = 1
g = 9.81
theta_init = 0.5
omega_init = 0
dt = 1e-2
T = 20
time = np.linspace(0, T, int(T / dt))

# FE
theta_euler = [0.0 for i in range(len(time))]
omega_euler = [0.0 for i in range(len(time))]
theta_euler[0] = theta_init
omega_euler[0] = omega_init
E_euler = [-g * l * np.cos(theta_euler[0]) + (1 / 2) * l**2 * omega_euler[0] ** 2]


# RK4
theta_rk4 = [0.0 for i in range(len(time))]
omega_rk4 = [0.0 for i in range(len(time))]
theta_rk4[0] = theta_init
omega_rk4[0] = omega_init
E_rk4 = [-g * l * np.cos(theta_rk4[0]) + (1 / 2) * l**2 * omega_rk4[0] ** 2]

def f_state(state: ndarray):
        theta, omega = state
        return np.array([omega, -(g/l)*np.sin(theta)])

def step_rk4(state, step):
    st = state
    k_1 = f_state(st)
    k_2 = f_state(st + (step/2)*k_1)
    k_3 = f_state(st + (step/2)*k_2)
    k_4 = f_state(st + step*k_3)
    return st + (step/6)*(k_1 + 2 * k_2 + 2 * k_3 + k_4)


state = np.array([theta_init, 0])
for t in range(len(time) - 1):
    # FE updates
    omega_euler[t + 1] = omega_euler[t] + dt * (-g / l) * np.sin(theta_euler[t])
    theta_euler[t + 1] = theta_euler[t] + dt * omega_euler[t]

    # FE Mass-specific Mechanical energy
    E_euler.append(-g * l * np.cos(theta_euler[t]) + (1 / 2) * l**2 * omega_euler[t] ** 2)

    # RK4 updates    
    state = step_rk4(state, dt)
    theta, omega = state
    theta_rk4[t + 1] = theta
    omega_rk4[t + 1] = omega
    E_rk4.append(-g * l * np.cos(theta_rk4[t]) + (1 / 2) * l**2 * omega_rk4[t] ** 2)


epsilon_E_cons = np.max(np.abs(E_rk4 - E_rk4[0])/np.abs(E_rk4[0]))*1000

# Plot
fig, ax = plt.subplots(3, 1, sharex=True)
fig.suptitle("Pendulum simulation: Forward Euler vs RK4")

ax[0].plot(time, theta_euler, color="red", lw=1, label="Angle - FE")
ax[0].plot(time, theta_rk4, color="black", lw=2, ls="--", label="Angle - RK4")
ax[0].set_ylabel("Angle (rad)")
ax[0].legend()

ax[1].plot(time, omega_euler, color="blue", lw=1, label="Speed - FE")
ax[1].plot(time, omega_rk4, color="black", lw=2, ls="--", label="Speed - RK4")
ax[1].set_ylabel("Angular speed (rad/s)")
ax[1].legend()

ax[2].plot(time, E_euler, color="green", lw=1, label="Energy - FE")
ax[2].plot(time, E_rk4, color="black", lw=2, label="Energy - RK4")
ax[2].text(
    0.95, 0.08,
    f"RK4 Error: {epsilon_E_cons:.10f}‰",
    transform=ax[2].transAxes,
    ha="right", va="bottom",
    bbox=dict(boxstyle="round", fc="white", alpha=0.7)
)
ax[2].set_ylabel("Mechanical Energy")
ax[2].set_xlabel("Time (s)")
ax[2].legend()

plt.show()
