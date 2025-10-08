# 📡 D2D Channel Simulation using Python

This project simulates **Device-to-Device (D2D)** and **Cellular User (CU)** communication under various power control and interference scenarios.  
It includes models for **path loss**, **fading**, **SINR calculation**, and **reward computation** for reinforcement learning or optimization frameworks.

---

## 🧠 Overview

The simulation models a cellular network region with randomly distributed:
- Cellular Users (CUs)
- D2D transmitter-receiver pairs

It computes:
- SINR values for each CU and D2D pair
- Channel fading (exponential + lognormal)
- Path loss and distance matrices
- Reward function for D2D communication
- Collision detection between D2D nodes accessing the same CU

Plots are generated to visualize:
- CU positions
- D2D positions
- Collisions between D2D users

---

## ⚙️ Features

✅ Pathloss and fading models  
✅ SINR computation for CU and D2D  
✅ Collision detection mechanism  
✅ Reward calculation  
✅ Visualization of node positions and collisions  

---

## 🧩 Requirements

You can install dependencies using:

```bash
pip install -r requirements.txt
