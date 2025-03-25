from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False, default='team_member')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    tasks_assigned = db.relationship('Task', backref='assigned_to', lazy=True, foreign_keys='Task.assigned_to_id')
    tasks_created = db.relationship('Task', backref='created_by', lazy=True, foreign_keys='Task.creator_id')
    projects = db.relationship('Project', backref='created_by', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    tasks = db.relationship('Task', backref='project', lazy=True)
    team_members = db.relationship('ProjectMember', backref='project', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'status': self.status,
            'creator': self.created_by.username,
            'task_count': len(self.tasks)
        }

class ProjectMember(db.Model):
    __tablename__ = 'project_members'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='todo')  # todo, in_progress, review, completed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float)
    
    # Foreign Keys
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='task', lazy=True)
    attachments = db.relationship('TaskAttachment', backref='task', lazy=True)
    tags = db.relationship('TaskTag', backref='task', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'assigned_to': self.assigned_to.username if self.assigned_to else None,
            'creator': self.created_by.username,
            'project_id': self.project_id,
            'project_name': self.project.name
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'author': self.author.username,
            'task_id': self.task_id
        }

class TaskAttachment(db.Model):
    __tablename__ = 'task_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(50))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class TaskTag(db.Model):
    __tablename__ = 'task_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#000000')  # Hex color code
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # task_update, mention, deadline, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    related_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    related_project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'created_at': self.created_at.isoformat(),
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'related_task_id': self.related_task_id,
            'related_project_id': self.related_project_id
        } 