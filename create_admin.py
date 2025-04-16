from app import create_app, db, bcrypt
from app.models import User

app = create_app()

with app.app_context():
    email = "sonibhumit196@gmail.com"
    existing_admin = User.query.filter_by(email=email).first()

    if not existing_admin:
        hashed_password = bcrypt.generate_password_hash("admin@123").decode('utf-8')
        admin_user = User(username="admin", email=email, password=hashed_password, role="admin")

        db.session.add(admin_user)
        db.session.commit()

        print(" Admin user created successfully")
    else:
        print(" Admin user already exists!")