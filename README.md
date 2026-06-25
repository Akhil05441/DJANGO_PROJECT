# 🎬 BookMySeat - Enterprise-Grade Ticketing Backend

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery)
![Stripe](https://img.shields.io/badge/Stripe-626CD9?style=for-the-badge&logo=stripe)

A highly scalable, concurrency-safe movie ticketing backend (BookMyShow clone) engineered to handle heavy traffic, prevent race conditions, and process idempotent payments. 

> **🟢 Live API & Server:** [https://django-project-qx0n.onrender.com](https://django-project-qx0n.onrender.com)

---

## ⚡ System Architecture & Key Features

This project was built focusing on production-grade database optimization and backend reliability.

* **Concurrency-Safe Seat Reservations (No Double-Booking):** Utilizes pessimistic database locking (`transaction.atomic()` and `select_for_update()`) to ensure absolute row-level data integrity during peak traffic seat selection. Features a dynamic 2-minute expiration lifecycle.
* **Idempotent Payment Webhooks:** Integrated with Stripe's API. Verifies cryptographic signatures (`stripe.Webhook.construct_event`) to prevent spoofing and uses database constraints (`unique=True` on `payment_id`) to mathematically guarantee users are never double-charged.
* **Asynchronous Task Queues:** Decouples heavy network operations (like sending ticket confirmation emails) from the main request thread using **Redis** as a message broker and **Celery** as a background worker.
* **Highly Optimized Queries:** Prevents the $N+1$ query problem across 5,000+ movie records using `prefetch_related`. Eliminates full-table scans via strategic `db_index` assignments.
* **Aggregated Analytics Dashboard:** Pushes all heavy mathematical computations (total revenue, cancellation rates) directly to the PostgreSQL engine via Django ORM aggregations (`Sum`, `Count`). The endpoint is secured and optimized with a 15-minute Redis cache layer.

---

## 🛠️ Tech Stack

* **Core Framework:** Python 3.12, Django 5.0
* **Database:** PostgreSQL (Production), SQLite (Local Dev)
* **Message Broker / Cache:** Redis
* **Task Queue:** Celery
* **Payment Gateway:** Stripe API
* **Production Servers:** Gunicorn, Daphne
* **Hosting:** Render

---

## 🚀 Local Setup & Installation

If you wish to run this project locally, follow these steps:

### 1. Clone the repository
```bash
git clone [https://github.com/Akhil05441/DJANGO_PROJECT.git](https://github.com/Akhil05441/DJANGO_PROJECT.git)
cd DJANGO_PROJECT
