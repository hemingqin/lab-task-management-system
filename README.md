# Lab Team Task Management System

A comprehensive task management system designed for laboratory teams, featuring real-time collaboration, Kanban boards, and detailed analytics.

## Features

- **User Authentication & Authorization**

  - JWT-based authentication
  - Role-based access control (Admin, Team Lead, Team Member)
  - Secure password handling

- **Project Management**

  - Create and manage multiple projects
  - Assign team members to projects
  - Track project progress and deadlines

- **Task Management**

  - Kanban board for visual task tracking
  - Task assignments and priority levels
  - File attachments and comments
  - Real-time updates using WebSocket

- **Team Collaboration**

  - Real-time notifications
  - Comment system
  - File sharing
  - Team member mentions

- **Analytics & Reporting**

  - Task completion metrics
  - Team performance analytics
  - Project progress tracking
  - Custom report generation

- **Calendar Integration**
  - Task scheduling
  - Deadline tracking
  - Calendar view for tasks and projects

## Technology Stack

### Frontend

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
- AWS S3 for file storage

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- Redis

### Backend Setup

1. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up environment variables (create .env file):

   ```
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   DATABASE_URL=postgresql://postgres:password@localhost/lab_tasks
   REDIS_URL=redis://localhost:6379
   AWS_ACCESS_KEY_ID=your-aws-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret
   AWS_BUCKET_NAME=your-bucket-name
   ```

4. Initialize the database:

   ```bash
   flask db upgrade
   ```

5. Run the development server:
   ```bash
   flask run
   ```

### Frontend Setup

1. Install dependencies:

   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

## Development Guidelines

### Code Style

- Backend: Follow PEP 8 guidelines
- Frontend: Use ESLint and Prettier configurations
- Use meaningful variable and function names
- Write comprehensive documentation

### Testing

- Write unit tests for all new features
- Run tests before committing:

  ```bash
  # Backend tests
  pytest

  # Frontend tests
  npm test
  ```

### Git Workflow

1. Create feature branch from develop
2. Make changes and test
3. Submit pull request
4. Code review
5. Merge to develop

## API Documentation

### Authentication Endpoints

- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me

### Project Endpoints

- GET /api/projects
- POST /api/projects
- GET /api/projects/<id>
- PUT /api/projects/<id>
- DELETE /api/projects/<id>

### Task Endpoints

- GET /api/tasks
- POST /api/tasks
- GET /api/tasks/<id>
- PUT /api/tasks/<id>
- DELETE /api/tasks/<id>

### WebSocket Events

- task_update
- new_comment
- notification

## Deployment

### Backend Deployment

1. Set up PostgreSQL database
2. Configure environment variables
3. Run migrations
4. Start Gunicorn server
5. Configure Nginx

### Frontend Deployment

1. Build production bundle:
   ```bash
   npm run build
   ```
2. Serve static files through Nginx

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License

## Support

For support, email support@labtasks.com or create an issue in the repository.
