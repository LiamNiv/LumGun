![LumGun](README_title_image.png)

## Overview

LumGun is an online shooting game where players can sign in and compete against each other in a 2D map. Players move using the W, A, S, or D keys, aim with their mouse, and shoot bullets at each other. The game is developed entirely in Python and Pygame. This project is my final project for cyber in the Israeli education system.

![LumGun](README_gameplay_image.jpg)

## Features

- **Multiplayer GamePlay**: Play against other players in real-time.
- **Controls**: Move with W, A, S, or D keys and aim with your mouse.
- **Secure Sign-In**: User management with a JSON database.
- **End-to-End Encryption**: Secure communication using RSA key exchange and AES symmetric keys. Custom RSA implementation included.

## Installation

To get started with LumGun, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/LiamNiv/LumGun.git
    cd LumGun
    ```

2. **Install Required Libraries**:
    LumGun requires Pygame, Sympy, and PyCryptodome libraries. Install them using pip:
    ```bash
    pip install pygame sympy pycryptodome
    ```

## Setup

:red_circle: **Admin Password:** The admin password for opening a server is `'michal2506'`

Make sure the IP address in the network.py, is the IP of the local server you want to connect to.
```python
self.server = "192.168.10.128"
```