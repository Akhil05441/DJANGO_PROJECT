# 🎟️ BookMySeat: Real-Time Movie Ticketing Backend

A robust, real-time backend API architecture for a movie ticketing platform, inspired by BookMyShow. Built with **Python** and **Django**, this project focuses on handling concurrent ticketing events and preventing double-bookings using WebSocket connections.

## ✨ Core Features

* **Real-Time Seat Locking:** Utilizes Django Channels and WebSockets to instantly lock a seat across all active client sessions the moment a user selects it.
* **Concurrency Handling:** Prevents race conditions and double-booking during high-traffic checkout flows.
* **Automated Seeding:** Custom Python scripts to instantly generate hundreds of dynamically named seats (e.g., A1 to J10) linked to specific shows.
* **Relational Architecture:** Clean, optimized SQLite relational database mapping Users, Movies, Shows, Seats, and Bookings.
* **Production Ready:** Configured with Gunicorn, WhiteNoise, and automated setup scripts for seamless deployment on ephemeral file systems like Render.

## 🛠️ Tech Stack

* **Language:** Python 3.12
* **Framework:** Django 5.x
* **Real-Time Communication:** Django Channels, Daphne, WebSockets
* **Database:** SQLite (Development/Free-Tier Production)
* **Deployment:** Render, Gunicorn, WhiteNoise

## 🚀 Local Development Setup

To run this project on your local machine, follow these steps:

**1. Clone the repository**
```bash
git clone [https://github.com/yourusername/bookmyseat-clone.git](https://github.com/yourusername/bookmyseat-clone.git)
cd bookmyseat-clone
