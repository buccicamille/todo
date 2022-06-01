from asyncio import tasks
import os
from datetime import datetime, time

from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
Bootstrap(app)

# database setup.
basedir = os.path.dirname(__file__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'todo.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()

# application models.
class Task(db.Model):
    """model to store a task data"""

    id = db.Column(db.Integer, primary_key=True)
    """:type : int"""

    description = db.Column(db.String(200), nullable=False)
    """:type : str"""

    date_created = db.Column(db.DateTime, default=datetime.now)
    """:type : datetime"""

    status = db.Column(db.String(200), nullable=False)
    """:type : str"""
    
    category = db.Column(db.String(200), nullable=False)
    """:type : str"""
    
    total_time = db.Column(db.Time, default=time(0, 0))
    """:type : time"""

    def __repr__(self):
        """override __repr__ method"""
        return f"Task: #{self.id}, content: {self.description}"

class User(db.Model, UserMixin):
    """model to store user data"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    """:type : int"""

    name = db.Column(db.String(200), nullable=False)
    """:type : str"""

    email = db.Column(db.String(200), nullable=False, unique=True)
    """:type : str"""

    password = db.Column(db.String(200), nullable=False)
    """:type : str"""
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
    
    def __repr__(self):
        """override __repr__ method"""
        return f"User: #{self.email}"  

# routes and handlers.
@app.route('/', methods=['GET'])
def index():
    """root route"""
    return render_template('home.html')

@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    
    if request.method == 'POST':
        task = Task(description=request.form['description'],status='A fazer',category=request.form['category'])
        try:
            db.session.add(task)
            db.session.commit()
            return redirect('/')
        except:
            return "Houve um erro ao inserir a tarefa"
    else:
        tasks = Task.query.order_by(Task.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(name=request.form['name'],email=request.form['email'],password=request.form['password'])
        
        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        except:
            return "Houve um erro ao cadastrar usuário"
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.password == pwd:
            login_user(user)
                
            return redirect('/tasks')
        
    else:
        return render_template('login.html')
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    """delete a task"""
    task = Task.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect('/tasks')
    except:
        return "Houve um erro ao excluir a tarefa"


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    """update route"""
    task = Task.query.get_or_404(id)
    
    if request.method == 'POST':
        task.description = request.form['description']
        task.status = request.form['status']
        task.category = request.form['category']
        
        if not (task.status == 'A fazer' or task.status == 'Fazendo' or task.status == 'Feita'):
            raise Exception("Status inválido")
        
        try:
            db.session.commit()
            return redirect('/tasks')
        except:
            return "Houve um erro ao atualizar a tarefa"
    else:
        return render_template('update.html', task=task)