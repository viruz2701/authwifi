from app import create_app, db
from app.models import AdminUser

app = create_app()

@app.cli.command("initdb")
def init_db():
    """Initialize the database."""
    db.create_all()
    
    # Create admin user if not exists
    if not AdminUser.query.filter_by(username='admin').first():
        admin = AdminUser(
            username='admin',
            password_hash=generate_password_hash('securepassword'),
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Database initialized with admin user.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')