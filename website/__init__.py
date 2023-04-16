from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate



db = SQLAlchemy()
DB_NAME = 'database.db'



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "helloworld"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    migrate = Migrate(app, db)

    
    
    from .views import views
    from .auth  import auth 
    from .models import User, Post, Comment
    
    # create_database(app)
    with app.app_context():
        db.create_all()
        print("Database Created")
        
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    
    # basically storing your session credential, so when logged in again, no need to sign in. Just straight log in.
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    app.register_blueprint(views,url_prefix='/')
    app.register_blueprint(auth,url_prefix='/')
    
    # @app.route("/")
    # def home():
    #     return "<h1>hello world</h1>"
    
    # @app.route("/profile")
    # def profile():
    #     return "<h1>profile</h1>"
    
    
    return app 


# def create_database(app):
#     if not path.exists("website/" + DB_NAME):
#         db.create_all(app=app)
#         print("Created Database")