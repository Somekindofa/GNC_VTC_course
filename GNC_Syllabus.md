# GNC Self-Taught Syllabus — Constrained Edition
*Late April 2026 → Start of October 2026 (~22 weeks). All hardware owned. ~30€ new spend.*

---

## Preamble — What changed and why

This is a re-scoped plan. The earlier 32-week, free-hover, ~200€ version assumed you'd pursue Phase 6 (untethered hover) outdoors with a vehicle you'd build, crash, and rebuild. With twins arriving in October, that scope is incompatible with the time, money, and cognitive bandwidth available.

**The new shape**:

- **No free flight.** The vehicle never leaves a clamped test rig.
- **No new microcontroller, IMU, ESC, or LiPo.** You use what you own.
- **5 phases instead of 6.** The deferred Phase 6 (free hover) is replaced by a polished 6-DoF simulation as the final deliverable.
- **22 weeks instead of 32.** Faster pace, fewer side quests, less slack.

**What's preserved**: the entire core of GNC theory. PID, state-space, LQR, Kalman filtering, MPC. You'll learn what a GNC engineer learns. You won't fly a vehicle in October. You'll know how to.

**Phase 6 deferred, not deleted.** When the twins sleep through the night and your bandwidth returns (~summer 2027), the test rig and codebase you built this summer will still be there. Free hover becomes a 4-week project on top of an already-validated stack instead of a from-scratch build.

---

## Hardware — final inventory

**Owned, used in syllabus**:
- Arduino Nano 33 BLE Sense Rev2 (BMI270 IMU + BMM150 mag + BMP280 baro onboard)
- A2212 2200KV brushless motor + propeller
- Yellow stock ESC (standard PWM, 50 Hz, fine for this scope)
- 2× SG90 hobby servos (sufficient for non-flying rig at modest thrust)
- 3S 5200mAh 50C LiPo (oversized but free)
- Bambulab P1S 3D printer
- Hand tools, soldering iron, breadboards, wire stash

**To buy** (~30-40€ total, end of Phase 1):

| Item | Qty | ~€ | Use |
|---|---|---|---|
| MR105ZZ ball bearings (5mm bore, 10mm OD) | 4 | 4 | Gimbal pivots |
| M3 hex bolts + nuts + washers assortment | 1 | 8 | Rig assembly |
| Aluminum extrusion 2020 or steel rod ~30cm | 1 | 8 | Vertical column |
| Heavy F-clamps (table-clamping the rig) | 2 | 10 | Safety |
| Full-face shield | 1 | 15 | Safety |
| Class B/D fire extinguisher (1kg) | 1 | 30 | Safety, if not already owned |

**Bench power supply**: highly recommended (~60€) but listed as optional. If you have one already, use it. If not, you can do early thrust tests on the LiPo with current-limited care.

---

## Toolchain

| Layer | Tool |
|---|---|
| Simulation | Python 3.11+, numpy, scipy, matplotlib, `python-control`, `casadi`, `do-mpc` |
| Embedded | Arduino IDE OR PlatformIO with the Arduino-mbed core (PlatformIO preferred for anything beyond Phase 1) |
| IMU library | `Arduino_BMI270_BMM150`, official Arduino lib |
| Live plotting | Python script reading USB-CDC serial, matplotlib FuncAnimation |
| Version control | Git, single repo `tvc-rig/` with `sim/` and `firmware/` subdirs |

---

## Time budget reality check

22 weeks × 6 hrs/week (midpoint) = **132 hours**. The plan below targets ~125 hours, leaving ~7 hours of slack. That's one missed week. If two weeks slip, something has to drop, most likely the embedded port of MPC in Phase 5.

Phases are tight. Treat the weekly deliverable as a contract: if Sunday evening arrives without a demonstrable artifact, repeat the week before pushing forward. A cracked foundation in Phase 2 will eat a week of debugging in Phase 4.

---

# PHASE 1 — Foundations & Sensor Stack
**Weeks 1–4 (~22 hrs).** No rig yet. Get the toolchain, sensors, and math fundamentals working.

### Objectives
- Python sim environment producing trustworthy plots
- Nano streaming live IMU + barometer data over USB at >100 Hz
- Mass-spring-damper as your mental model for every linear system to come

### Weekly breakdown

**Week 1 — Sim env, git, "rocket in a vacuum"**
- VS Code workspace, Python venv, repo skeleton (`sim/`, `firmware/`, `notes/`, `hardware/`)
- Forward Euler integration of `m·ẍ = T(t) − m·g`
- Plot vertical altitude under a constant 10N thrust
- Verify analytically against `h = ½(T/m − g)t²`
- **Deliverable**: ballistic plot matching analytical solution to <1% error

**Week 2 — RK4, realistic thrust curves, sensor models**
- Show why Euler fails on oscillatory systems: simulate a frictionless pendulum at dt=0.1s with Euler, watch energy explode
- Implement RK4, re-run, watch energy conserve
- Add Gaussian noise + bias to a fake barometer signal in Python
- Plot noisy vs true altitude
- **Deliverable**: 1D thrust simulator with noisy barometer model, comparison plot

**Week 3 — Live IMU on Nano**
- Install `Arduino_BMI270_BMM150` library
- Read gyro + accel at 100 Hz (mbed core caps practical rates here, more later)
- Stream as CSV over USB serial
- Python script on laptop plots live with matplotlib FuncAnimation
- Physical check: what does the accelerometer read stationary? During rotation? Build the intuition.
- **Deliverable**: Nano streams IMU data, Python plots it live at 100 Hz

**Week 4 — Mass-spring-damper as Rosetta Stone**
- Solve `m·ẍ + b·ẋ + k·x = 0` analytically. Re-derive every step in `notes/msd.md`. This is the math you self-assessed as rusty; rebuild it now.
- Identify damping ratio ζ and natural frequency ω_n in terms of m, b, k
- Python: plot underdamped / critically damped / overdamped step responses
- **Why this matters**: every linear system you'll meet in Phases 2-5 looks like a mass-spring-damper. Lock this mental model now.
- **Deliverable**: interactive plot (matplotlib widgets) where you drag ζ and ω_n and see step response update

### Math topics
Euler vs RK4 (truncation error, stability), 2nd-order linear ODEs, damping ratio, natural frequency, Gaussian noise model

### Reading
- Åström & Murray, *Feedback Systems* (free PDF), Chapter 2
- Brian Douglas YouTube: "System Dynamics" playlist, first 3 videos

### Phase 1 milestone
Demo notebook + video: 1D rocket sim with realistic thrust + noisy baro, live IMU streaming from Nano, interactive mass-spring-damper explorer. Order the bearings, hardware, and safety gear at the start of Week 4. Tag `phase-1-done`.

---

# PHASE 2 — Build the Rig + Closed-Loop PID
**Weeks 5–10 (~36 hrs).** First closed-loop control on physical hardware.

### Objectives
- 2-DoF gimbal MVP rig assembled, table-clamped, motor running under safe conditions
- Read a block diagram, predict stability from pole locations
- Tuned PID stabilizing the gimbal against hand disturbances on both axes

### Weekly breakdown

**Week 5 — Laplace + classical control refresh**
- 3Blue1Brown "Differential Equations" Ep.1 + Brian Douglas Laplace intro
- Solve mass-spring-damper in Laplace domain, compare to time-domain
- Transfer function `H(s) = output(s)/input(s)`. Don't over-mystify it.
- Plot Bode of `1/(s²+2ζω_n s+ω_n²)` in `python-control`
- **Deliverable**: given a transfer function, predict step response shape correctly, verify in sim

**Week 6 — Feedback, P, I, D each in isolation**
- Closed-loop vs open-loop: why open-loop fails (disturbances, model mismatch)
- P alone on 1st-order plant: steady-state error, time-constant reduction
- D as brake; D on noisy signal as catastrophe
- I as anti-drift; integrator windup demonstrated
- Barnard's parking-lot analogy revisited with the math underneath
- **Deliverable**: PID in `python-control` driving mass-spring-damper to setpoint, <5% overshoot, <1s settling

**Week 7 — Design the rig in Fusion 360**
- 2-DoF gimbal: outer yoke (pitch axis) + inner ring (roll axis)
- Pivot points designed for ball bearing press-fits (MR105ZZ, 5mm bore)
- Inverted pendulum geometry: pivots BELOW the motor + battery mass, confirmed earlier
- Mount points for 2× SG90 servos with simple horn-and-link arms
- Vertical column (aluminum extrusion or steel rod) clamps to desk via F-clamps
- Battery on the gimbaled head (mass-honest dynamics)
- Umbilical channel for power + USB cable
- **Deliverable**: CAD assembly, exploded view, BOM committed to `hardware/`

**Week 8 — Print + assemble + complementary filter**
- Print parts overnight on the P1S
- Assemble gimbal, test free rotation by hand (should be smooth, no stiction)
- Wire Nano + servos + ESC on a breadboard mounted to the rig column
- **Software side this week**: implement complementary filter on Nano in C++
  - Gyro integration high-pass + accelerometer low-pass = pitch and roll
  - Run at the highest rate you can get out of the BMI270 driver (target 100-200 Hz)
- Hand-rotate the assembled rig (motor OFF), watch angles track on Python plotter
- **Deliverable**: assembled rig, complementary filter outputs ±1° accurate when hand-rotated

**Week 9 — First closed loop on one axis (motor OFF)**
- Wire only one servo. Lock the second axis mechanically.
- Implement PID on the Nano: `pitch_error → servo_angle`
- Tune by hand: increase Kp until oscillation, then add Kd to damp, then small Ki for steady-state
- Test by pushing the gimbal head, motor still off — the servo should counter your push
- Log error, command, and angle to serial; analyze step responses in Python
- **Deliverable**: video of single-axis disturbance rejection, motor-off

**Week 10 — Both axes, motor ON, low throttle**
- Unlock the second axis, wire the second servo
- Tune the second axis PID
- **Safety preamble**:
  - Rig clamped with 2× F-clamps to a heavy table
  - Face shield ON
  - Fire extinguisher within reach
  - LiPo on a fire-safe surface
  - Kill switch: a physical XT60 disconnect within arm's reach (no firmware kill switch yet)
  - Run at 20-30% throttle MAX
  - Test on the balcony if indoor noise/wash is an issue
- Apply small disturbances by hand, log, video
- **Deliverable**: video of 2-axis disturbance rejection under thrust, 20-30% throttle, recovering to upright in <1s

### Math topics
Laplace transforms (working level), transfer functions, poles, stability from poles, PID gains

### Reading
- Åström & Murray, Chapters 5–6
- Brian Douglas, "Classical Control" playlist
- Joe Barnard NARCON 2020 talk (the PID walkthrough)

### Phase 2 milestone
Video matching the reference photos: gimbal stand under thrust, hand pushes the head, controller corrects on both axes. Tag `phase-2-done`. **This is the visceral proof point.**

---

# PHASE 3 — State-Space and LQR
**Weeks 11–15 (~30 hrs).** Move beyond hand-tuned PID to model-based control.

### Objectives
- Move from "transfer function" to "state vector" mindset
- Derive the rig's equations of motion from first principles
- Design and implement LQR, observe why it beats hand-tuned PID for coupled dynamics

### Weekly breakdown

**Week 11 — State-space mechanics**
- Rewrite mass-spring-damper as `ẋ = Ax + Bu, y = Cx`
- Why state-space wins: MIMO is trivial, modern tools assume it
- Hand-compute 2×2 eigenvalues for 5 matrices, verify in numpy
- The bridge: eigenvalues of A = poles of transfer function
- **Deliverable**: notes/state_space.md with worked examples and the eigenvalue ↔ pole connection explained in your own words

**Week 12 — Equations of motion for the rig**
- Derive from Newton + Euler: gravity, gimballed thrust vector at angle δ, pitch angle θ, moment of inertia I (estimate from CAD mass properties in Fusion 360)
- 2D first (pitch only): inverted pendulum with thrust-vectored base
- Linearize around upright equilibrium → A, B matrices for your physical rig
- Simulate in Python, verify open-loop instability (right-half-plane eigenvalues)
- **Deliverable**: validated 2D pitch sim of YOUR rig, with measured/estimated I, m, l parameters

**Week 13 — Controllability, observability, full 4-state model**
- Controllability matrix `[B AB A²B …]`, full rank means you can drive any state
- Observability matrix, full rank means you can reconstruct any state
- Extend model to 2D (pitch + roll), 4 states `[θ, θ̇, φ, φ̇]`, 2 inputs `[δ_pitch, δ_roll]`
- **Deliverable**: rank tests passing on your rig's A, B, C matrices

**Week 14 — LQR design in simulation**
- LQR minimizes `∫(x'Qx + u'Ru) dt`. Q penalizes bad states, R penalizes aggressive servos.
- Bryson's rule for initial Q, R: normalize by max acceptable deviation squared
- `scipy.linalg.solve_continuous_are` solves the Riccati equation; don't solve by hand
- Sweep Q/R, plot trajectories, pick a setting that feels right
- **Deliverable**: LQR on 2D pitch+roll sim, stabilizes to ±2° in <0.5s

**Week 15 — LQR on the rig**
- Compute K matrix in Python from rig parameters
- Hand-copy the 2×4 K matrix into Nano C++ (yes, literally — refactor later if you want)
- Run `u = -K*x` at the rate the Nano can sustain (target 100 Hz on mbed core)
- Capture step response, compare side-by-side with Phase 2 PID video
- **Deliverable**: video showing LQR vs PID side-by-side, plot showing smoother/faster recovery

### Math topics
Eigenvalues + matrix exponentials, linearization (Jacobians), controllability/observability, algebraic Riccati equation (used, not derived)

### Reading
- Tedrake, *Underactuated Robotics* (MIT, free), Chapters 1-3 — gold
- Brian Douglas, "State Space" playlist
- Nise, *Control Systems Engineering*, Chapter 12 (reference for mechanics)

### Phase 3 milestone
Video of rig under LQR, smoother than PID, with both axes coupled handled correctly. Step response plots overlaid. Tag `phase-3-done`.

---

# PHASE 4 — Kalman Filtering
**Weeks 16–19 (~25 hrs).** Proper state estimation.

### Objectives
- Understand why complementary filters hit a ceiling
- Derive and implement a linear Kalman filter, then extend to EKF for attitude
- Run LQR + EKF together (LQG) on the rig

### Weekly breakdown

**Week 16 — Probability and the linear KF**
- Gaussian: mean, variance, covariance matrix
- Bayes' rule applied to recursive estimation
- The 5-line algorithm: predict, update, repeat
- 1D Kalman for constant-velocity tracking, Python sim, tune Q/R, watch behavior
- **Deliverable**: 1D KF tracking a noisy 1D rocket altitude with RMSE <0.1m vs truth

**Week 17 — EKF for quaternion attitude (sim only)**
- Why quaternions: gimbal lock, numerical issues near ±90°
- Quaternion math: multiplication, conjugate, vector rotation
- EKF: gyro propagates state, accel corrects tilt, mag corrects yaw (use BMM150 onboard)
- All in Python this week
- **Deliverable**: Python EKF, yaw drift <2°/min under realistic noise

**Week 18 — EKF on Nano**
- Port the EKF to Nano C++. The mbed core has limited matrix libraries; you'll write yours or use a single-header lib like TinyEKF or BasicLinearAlgebra
- Honest expectation: BMI270 + Nano + EKF will run at ~50 Hz, not 200 Hz. That's fine for this rig.
- Verify against tilt table or known angles
- **Deliverable**: Nano outputs EKF attitude estimate, drift bounded, runs ≥50 Hz

**Week 19 — LQG on the rig**
- Replace complementary filter with EKF in the control loop
- Run LQR using EKF-estimated state instead of raw filter output
- Observe robustness to disturbances and IMU noise
- **Deliverable**: video and plots showing LQG performance vs Phase 3 LQR; if LQG is worse, debug noise covariance tuning

### Math topics
Multivariate Gaussians, linear KF derivation, EKF (Jacobians), quaternion algebra

### Reading
- Labbe, *Kalman and Bayesian Filters in Python* (free GitHub book) — single best Kalman resource ever written
- Madgwick's original filter paper (alternative, simpler, worth knowing exists)

### Phase 4 milestone
Rig running LQG on Nano. Logs showing EKF performance. Tag `phase-4-done`.

---

# PHASE 5 — Optimal Control & 6-DoF Sim Hover
**Weeks 20–22 (~17 hrs).** Final stretch. MPC concept + the simulation deliverable that stands in for a real hover.

### Objectives
- Understand MPC formulation, run it in sim
- Build a 6-DoF Python hover simulator with realistic noise, motor lag, gimbal limits
- Produce a polished simulation that hovers a virtual TVC vehicle at 1m for 10+ seconds

### Weekly breakdown

**Week 20 — MPC concept + tooling**
- At each timestep, solve a finite-horizon optimal control problem, apply first input, shift, repeat
- Why MPC > LQR: hard constraints (motor saturation, gimbal limits) are first-class
- `do-mpc` library, set up MPC for your rig's 2D model
- **Deliverable**: MPC stabilizes 2D rig sim with hard ±15° gimbal limits that LQR violates

**Week 21 — Build the 6-DoF simulator**
- Extend the rig model to a free-flying 6-DoF vehicle: 3D position, 3D attitude (quaternion), 2D gimbal
- Add gravity, motor dynamics (1st-order lag), gimbal servo dynamics, IMU + baro noise
- Use your existing LQR or LQG controller (from Phase 4) wrapped with an outer altitude loop
- Visualize with matplotlib 3D or `plotly` for a clean side-view animation
- **Deliverable**: 6-DoF sim, vehicle hovers at 1m with realistic noise, visualized in 3D

**Week 22 — Polish + final video**
- Tune the simulated controller until hover is rock-solid (this is the unconstrained you, no hardware to fight)
- Record: split-screen of (a) physical rig under LQG from Phase 4, (b) simulated 6-DoF hover from Week 21
- 2-minute highlight reel, one technical writeup blog post, README polish on both repos
- Push to GitHub Pages or similar
- **Deliverable**: public portfolio piece. Tag `phase-5-done`.

### Math topics
Convex optimization basics, MPC formulation (no embedded port at this scope)

### Reading
- Borrelli, Bemporad, Morari, *Predictive Control for Linear and Hybrid Systems* (free), Chapters 1-4 (skim)
- Açıkmeşe & Ploen, "Convex Programming Approach to Powered Descent Guidance" — for context on what real rocket landing actually does

### Phase 5 milestone — and end of the syllabus
**Final video**: physical 2-DoF rig demonstrating LQG attitude stabilization under thrust + simulated 6-DoF vehicle hovering at 1m for 10+ seconds. Public GitHub repo, blog post, portfolio-ready.

---

## Risk register

**Risk 1: Math bridge in Phase 3.**
Linear algebra (eigenvalues, matrix exponentials, controllability) is where self-taught GNC stalls. If Week 11 feels impossible, slow down. Take an extra week. Cut Phase 5 polish if you have to.

**Risk 2: Nano bandwidth ceiling in Phase 4.**
nRF52840 + mbed core + EKF will be tight. Mitigation: drop control rate to 50 Hz, simplify EKF to 6-state (no mag), or fall back to complementary filter + LQR if EKF won't fit. The lesson is the same.

**Risk 3: Workshop time disappears before October.**
Twins arrive end of September. Final 2-3 weeks of pregnancy may eat your evenings. Treat the syllabus as front-loaded: try to be at end of Phase 4 by Week 18, leaving Phase 5 (which is 100% software) doable from a couch with a laptop.

**Risk 4: Mechanical iteration on the rig.**
First print of the gimbal will probably have stiction, alignment issues, or servo linkage slop. Budget 1 reprint cycle in Week 8. If 2+ reprints are needed, eat into Phase 2 slack.

**Risk 5: Motivation dip around Phase 3.**
State-space feels abstract. Counter: Week 12 is when you derive YOUR rig's equations. Make it personal. Plot YOUR pitch axis, with YOUR moment of inertia, and watch YOUR system go unstable open-loop in sim. That's the hook.

---

## After October

The syllabus completes. Twins arrive. Most of life pauses.

When bandwidth returns, several paths exist on top of what you'll have built:

| Path | Effort | What it adds |
|---|---|---|
| Free hover (deferred Phase 6) | 4-6 weeks | The original goal. Buy a smaller LiPo (~20€), build flight legs and a parachute, use the same firmware. |
| Vision-based landing | 2-3 months | Raspberry Pi + camera + ArUco markers. Resurrects the shelved Pi. |
| Custom flight controller PCB | 2-3 months | KiCad, PCBWay. Replaces the Nano with a proper 5g board. The portfolio piece. |
| Nothing | 0 weeks | A fully respectable outcome. You learned GNC. |

---

*Last revised: 22-week scope, Nano-only, sim-final.*
