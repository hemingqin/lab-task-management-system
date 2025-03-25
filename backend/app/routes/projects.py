from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Project, db, User, Task
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/', methods=['GET'])
@jwt_required()
def get_projects():
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Authentication required'}), 401

        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role == 'admin':
            projects = Project.query.all()
        else:
            # Get projects where user is either creator or has assigned tasks
            projects = Project.query.join(Task).filter(
                (Project.creator_id == current_user_id) |
                (Task.assigned_to_id == current_user_id)
            ).distinct().all()
        
        return jsonify([{
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'created_at': project.created_at.isoformat(),
            'deadline': project.deadline.isoformat() if project.deadline else None,
            'creator': project.created_by.username,
            'task_count': len(project.tasks)
        } for project in projects]), 200
    except Exception as e:
        logger.error(f"Error in get_projects: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@projects_bp.route('/', methods=['POST'])
@jwt_required()
def create_project():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    project = Project(
        name=data['name'],
        description=data.get('description', ''),
        deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
        creator_id=current_user_id
    )
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'created_at': project.created_at.isoformat(),
        'deadline': project.deadline.isoformat() if project.deadline else None,
        'creator': project.created_by.username,
        'task_count': 0
    }), 201

@projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role != 'admin' and project.creator_id != current_user_id:
        # Check if user has any tasks in this project
        has_tasks = Task.query.filter_by(
            project_id=project_id,
            assigned_to_id=current_user_id
        ).first() is not None
        
        if not has_tasks:
            return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'created_at': project.created_at.isoformat(),
        'deadline': project.deadline.isoformat() if project.deadline else None,
        'creator': project.created_by.username,
        'tasks': [{
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'assigned_to': task.assigned_to.username if task.assigned_to else None
        } for task in project.tasks]
    }), 200

@projects_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role != 'admin' and project.creator_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'deadline' in data:
        project.deadline = datetime.fromisoformat(data['deadline']) if data['deadline'] else None
    
    db.session.commit()
    
    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'created_at': project.created_at.isoformat(),
        'deadline': project.deadline.isoformat() if project.deadline else None,
        'creator': project.created_by.username,
        'task_count': len(project.tasks)
    }), 200

@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role != 'admin' and project.creator_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete all tasks associated with the project
    Task.query.filter_by(project_id=project_id).delete()
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'message': 'Project deleted successfully'}), 200 