#  Pulse — Social Media App

A full-stack social media platform built with Django REST Framework and vanilla JavaScript.

##  Live Demo
https://socialmedia-app-pulse.onrender.com

##  Tech Stack
- **Backend:** Django, Django REST Framework, JWT Authentication
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Deployment:** Render

##  Features
- ✅ User Registration & Login (JWT)
- ✅ Create & Delete Posts
- ✅ Like / Unlike Posts
- ✅ Comment on Posts
- ✅ Follow / Unfollow Users
- ✅ Personal Feed
- ✅ User Profiles

## Screenshots
### Login Page

![Login](pulse-app-home-page-ss.png)

### Home Page

![Home](pulse-app-homepage-ss.png)

## Setup Instructions
```bash
# Clone the repo
git clone https://github.com/chandinimaa95/Socialmedia-app-pulse.git

# Install dependencies
pip install -r requirements.txt

# Run migrations
cd backend && python manage.py migrate

# Start server
python manage.py runserver


