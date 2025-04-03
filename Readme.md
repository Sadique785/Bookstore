# Historia Bookstore

## 📖 Overview
Historia is a modern and user-friendly online bookstore built using Django's MVT architecture. It offers a seamless shopping experience with a secure payment gateway, efficient cart management, and session-based authentication. The platform is designed to provide a smooth and intuitive browsing and purchasing experience for book lovers.

## 🌐 Live Demo
[Historia Bookstore](https://historia.devque.live)

## 🛠 Tech Stack
- **Backend**: Django (MVT Pattern), PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Session-based authentication
- **Payment Integration**: Razorpay
- **Hosting**: EC2 Instance

## 🚀 Features
- 📚 Browse & search books
- 🛒 Add to cart & manage orders
- 💳 Secure payments via Razorpay
- 🔐 User authentication & session management
- 📊 Admin dashboard for managing sales

## 🛠 Setup Guide
### 1️⃣ Clone the repository
```bash
git clone <repo-url>
cd historia
```

### 2️⃣ Create & activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate  # For Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Apply migrations & start the server
```bash
python manage.py migrate
python manage.py runserver
```

### 5️⃣ Open the project in the browser
```
http://127.0.0.1:8000/
```

## 📄 API Documentation
The API documentation can be found [here](https://docs.google.com/document/d/1re5zwn_tY2OS_tQJ79IY5XTp3k02ebRk/edit?usp=drive_link&ouid=115696148399597572925&rtpof=true&sd=true).

## 🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📜 License
This project is open-source. Feel free to use and modify it as per your needs.

---
🚀 **Happy Coding!**
