from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from pymongo import MongoClient

app = Flask(__name__, static_folder="templates/static")
app.secret_key = 'your_secret_key'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Conexión a MongoDB
client = MongoClient("mongodb://35.180.31.99:27017/?directConnection=true&appName=mongosh+2.0.0")
db = client["ServiceWeb"]
col = db["Userslol"]
msj_col = db["Messages"]

class User(UserMixin):
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    user = col.find_one({"username": user_id})
    if user:
        return User(id=user["username"], name=user.get('name', ''), email=user.get('email', ''))
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = col.find_one({'username': username})

        if user and check_password_hash(user["password_hash"],password):
            user_obj = User(id=username, name=user.get("name"), email=user.get("email"))
            login_user(user_obj)
            flash("Login exitoso", 'success')
            print("Usuario autenticado con éxito")
            return redirect(url_for('home'))
        else:
            flash("Error en la autenticación. Verifica tu usuario y contraseña.", 'danger')
            print("Error de autenticación")

    return render_template("login.html")

@app.route('/forgot_password', methods=["GET", "POST"])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        flash("Se ha enviado un enlace de contraseña a tu correo electrónico.", 'info')
        print(f"Solicitud de restablecimiento de contraseña para: {email}")
        return redirect(url_for('login'))

    return render_template("forgot.html")

@app.route("/")
@login_required
def home():
    print("Accediendo a la página de inicio")
    return render_template("home.html")

@app.route('/profile/<username>', methods=["GET","POST"])
@login_required
def profile(username):
    user = col.find_one({'username': current_user.id})
    if not user:
        flash("Usuario no encontrado", 'danger')
        return redirect(url_for('home'))

    if request.method == "POST":

        flash("Datos del perfil actualizados.", 'success')
        print("Datos del perfil actualizados")
        return redirect(url_for('profile', username=username))

    return render_template('profile.html', user=user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión", 'success')
    print("Usuario cerró sesión")
    return redirect(url_for('login'))

@app.route("/static2/<path:filename>")
def serve_static2(filename):
    directory = os.path.join(app.root_path, "templates/static2")
    return send_from_directory(directory, filename)

@app.route("/profile/static3/<path:filename>")
def serve_static3(filename):
    directory = os.path.join(app.root_path, "templates/static3")
    return send_from_directory(directory, filename)

@app.route("/static4/<path:filename>")
def serve_static4(filename):
    directory = os.path.join(app.root_path, "templates/static4")
    return send_from_directory(directory, filename)

@app.route('/chat')
@login_required
def chat():
    return render_template("chat.html")

@app.route("/messages",methods= ["GET","POST"])
@login_required
def messages():
    if request.method == "POST":
        content = request.json
        message = {
            "user": current_user.id,
            "message": content["message"]
        }
        msj_col.insert_one(message)
        return jsonify(message)
    elif request.method == "GET":
        messages = list(msj_col.find().sort("_id",-1).limit(50))
        for message in messages:
            message ["_id"] = str(message["_id"])
        messages.reverse()
        return jsonify(messages)



if __name__ == "__main__":
    app.run(debug=True)
    app.run(host='0.0.0.0', port=80)



