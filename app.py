from backend.app import create_app, db
from backend.app.models import User, Project, Task, Comment

app = create_app()

def init_db():
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")
            raise e

if __name__ == '__main__':
    try:
        # Initialize database
        init_db()
        # Run the application with debug mode
        app.run(debug=True, host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        raise e 