from flask import Flask, request, render_template, redirect, url_for, session
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'  # Necessary for session management

# Configure database connection (replace with your credentials)
DATABASE_URI = "mysql+pymysql://root:book123@0.0.0.0:3306/book_main"
engine = create_engine(DATABASE_URI)
Base = declarative_base()

# Define user model for separate database
class SeparateregisteredUser(Base):
    __tablename__ = 'registeredusers'  # Table name

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    password = Column(String(255), nullable=False)
    gender = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<SeparateUser(full_name='{self.full_name}', username='{self.username}', email='{self.email}')>"

class SeparateUser(Base):
    __tablename__ = 'users'  # Table name

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    opinion = Column(String(255))  # For limited length text (adjust as needed)

    def __repr__(self):
        return f"<SeparateUser(first_name='{self.first_name}', last_name='{self.last_name}', email='{self.email}')>"

# Create separate database tables if they don't exist
Base.metadata.create_all(engine)

# Create a session factory (represents a connection to the database)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.route('/')
def index():
    message = request.args.get('message')
    return render_template('index.html', message=message)

@app.route('/books')
def books():
    return render_template('booksample.html')

@app.route("/login", methods=['GET', 'POST'])
def login():  # Changed from loogin to login
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        session_db = SessionLocal()
        
        try:
            # Check if the user exists in the database
            user = session_db.query(SeparateregisteredUser).filter_by(username=username, password=password).first()
            
            if user:
                # User found, login successful
                session['user_id'] = user.id  # Save user ID in session
                session['username'] = user.username  # Save username in session
                session.pop('login_attempts', None)  # Reset login attempts
                return redirect(url_for('index', message="Login successful!"))
            else:
                # Increment login attempts
                session['login_attempts'] = session.get('login_attempts', 0) + 1
                if session['login_attempts'] >= 3:
                    # Redirect to register after 3 failed attempts
                    session.pop('login_attempts', None)  # Reset login attempts
                    return redirect(url_for('register', message="Invalid credentials. Please register."))
                else:
                    # Show login form again with an error message
                    return render_template('login.html', message="Invalid credentials. Please try again.")
        
        except SQLAlchemyError as err:
            message = f"Error occurred: {err}"
            return render_template('login.html', message=message)
        
        finally:
            session_db.close()

    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index', message="You have been logged out."))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        gender = request.form['gender']

        # Check if passwords match
        if password != confirm_password:
            message = "Passwords do not match"
            return render_template('registration.html', message=message)

        session_db = SessionLocal()
        # Create a new user object for the separate database
        new_user = SeparateregisteredUser(
            full_name=full_name,
            username=username,
            email=email,
            phone_number=phone_number,
            password=password,
            gender=gender
        )

        try:
            # Add user to the separate database session
            session_db.add(new_user)
            session_db.commit()  # Commit changes to the separate database

            message = "Registration successful!"

        except SQLAlchemyError as err:
            # Rollback in case of errors
            session_db.rollback()
            message = f"Error occurred: {err}"  # Handle database errors

        finally:
            # Close the separate database session
            session_db.close()

        return render_template('index.html', message=message)

    return render_template('registration.html')

@app.route('/submit', methods=['POST'])
def submit():
    first_name = request.form['fname']
    last_name = request.form['lname']
    email = request.form['ename']
    opinion = request.form['Textarea1']

    session_db = SessionLocal()
    # Create a new user object for the separate database
    new_user = SeparateUser(first_name=first_name, last_name=last_name, email=email, opinion=opinion)

    try:
        # Add user to the separate database session
        session_db.add(new_user)
        session_db.commit()  # Commit changes to the separate database

        message = "Data submitted successfully to the separate database!"

    except SQLAlchemyError as err:
        # Rollback in case of errors
        session_db.rollback()
        message = f"Error occurred: {err}"  # Handle database errors

    finally:
        # Close the separate database session
        session_db.close()

    return render_template('index.html', message=message)

@app.route('/subscriber', methods=['POST'])
def subscribe():
    email = request.form['email']  # Get email address from form

    session_db = SessionLocal()
    # Create a new subscriber object
    new_subscriber = Subscriber(email=email)

    try:
        # Add subscriber to the session
        session_db.add(new_subscriber)
        session_db.commit()  # Commit changes to the database

        message = "Your email has been successfully subscribed!"
        status = "success"

    except SQLAlchemyError as err:
        # Rollback in case of errors
        session_db.rollback()
        message = f"Error occurred: {err}"  # Handle database errors
        status = "failed"
    finally:
        session_db.close()  # Close the session

    return render_template('index.html', message=message, status=status)  # Render index page with success/error message

if __name__ == '__main__':
    app.run(debug=True)
