from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Task, db, User, Project
from datetime import datetime
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)
tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    
    try:
        current_user_id = int(get_jwt_identity())
        logger.info(f"Get tasks request received for user ID: {current_user_id}")
        
        if not current_user_id:
            logger.warning("No user ID found in JWT token")
            return jsonify({'error': 'Authentication required'}), 401

        user = User.query.get(current_user_id)
        if not user:
            logger.warning(f"User not found for ID: {current_user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        logger.info(f"User role: {user.role}")
        
        if user.role == 'admin':
            tasks = Task.query.all()
            logger.info("Fetching all tasks for admin user")
        else:
            tasks = Task.query.filter_by(assigned_to_id=current_user_id).all()
            logger.info(f"Fetching tasks for user {current_user_id}")
        
        task_list = [{
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'assigned_to': task.assigned_to.username if task.assigned_to else None,
            'project_id': task.project_id
        } for task in tasks]
        
        logger.info(f"Successfully retrieved {len(task_list)} tasks")
        return jsonify(task_list), 200
    except Exception as e:
        logger.error(f"Error in get_tasks: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    data = request.get_json()
    current_user_id = int(get_jwt_identity())
    
    # Verify project exists
    project = Project.query.get(data['project_id'])
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    task = Task(
        creator_id = current_user_id,
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'todo'),
        priority=data.get('priority', 'medium'),
        due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
        #assigned_to_id=data.get('assigned_to_id'),
        assigned_to_id=current_user_id,  # Default to the creator, but needs to be optimized in the furture
        project_id=data.get('project_id'),
        project_name = data.get('project_name')
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'assigned_to': task.assigned_to.username if task.assigned_to else None,
        'project_id': task.project_id
    }), 201

@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if user.role != 'admin' and task.assigned_to_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'assigned_to': task.assigned_to.username if task.assigned_to else None,
        'project_id': task.project_id
    }), 200

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if user.role != 'admin' and task.assigned_to_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    if 'due_date' in data:
        task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
    if 'assigned_to_id' in data:
        task.assigned_to_id = data['assigned_to_id']
    
    db.session.commit()
    
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'assigned_to': task.assigned_to.username if task.assigned_to else None,
        'project_id': task.project_id
    }), 200

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Task deleted successfully'}), 200 

@tasks_bp.route('/metrics', methods=['GET'])
@jwt_required()
def get_tasks_metrics():
    try:
        # Count all the tasks
        total_tasks = Task.query.count()
        
        # Count tasks by status
        statuses = db.session.query(Task.status, func.count(Task.id))\
                             .group_by(Task.status).all()
        status_counts = {status: count for status, count in statuses}
        
        # Calculate average estimated and actual hours
        avg_estimated_hours = db.session.query(func.avg(Task.estimated_hours)).scalar()
        avg_actual_hours = db.session.query(func.avg(Task.actual_hours)).scalar()
        
        metrics = {
            'total_tasks': total_tasks,
            'status_counts': status_counts,
            'avg_estimated_hours': float(avg_estimated_hours) if avg_estimated_hours else None,
            'avg_actual_hours': float(avg_actual_hours) if avg_actual_hours else None,
        }
        
        return jsonify(metrics), 200
    except Exception as e:
        logger.error(f"Error in metrics endpoint: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500