# Lab Team Task Management System

A personal project designed for Nanophotonics lab team work in University of Victoria, could be used as a regular task management system, featuring real-time collaboration, Kanban-like boards, and detailed analytics.

## Features

1.JWT-based User Authentication & Authorization
2.Project Management
3.Kanban board like Task Management (The borad part needs to be optimized )
4.Analytics & Reporting
5.Calendar Integration (Calendar view needs to be optimized)
6.AWS (Needs to be integrated in the furture)

## Technology Stack

## Frontend

- React 18
- Material-UI for components
- Nivo for data visualization
- FullCalendar for calendar view
- Socket.IO client for real-time features
- React Query for state management
- Formik & Yup for form handling
- TailwindCSS for styling

### Backend

- Flask
- PostgreSQL
- SQLAlchemy ORM
- Flask-SocketIO for WebSocket
- JWT for authentication
- Celery for background tasks
- Redis for caching

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- Redis

### Backend Setup

1. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
2. Install dependencies:
   cd backend
   pip install -r requirements.txt
3. Set up environment variables (create .env file):
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   DATABASE_URL=postgresql://postgres:password@localhost/lab_tasks
   REDIS_URL=redis://localhost:6379
   AWS_ACCESS_KEY_ID=your-aws-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret
   AWS_BUCKET_NAME=your-bucket-name
4. Initialize the database:
   flask db upgrade
5. Run the development server:
   flask run

### Frontend Setup

1. Install dependencies:
   cd frontend
   npm install

2. Start the development server:
   npm start

## Testing

- Write unit tests for all new features
- Run tests before committing:

  ```bash
  # Backend tests
  pytest

  # Frontend tests
  npm test
  ```
