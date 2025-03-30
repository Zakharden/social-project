from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
import psycopg2
import os
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, 
            static_folder='images',
            static_url_path='/images')
csrf = CSRFProtect(app)
app.secret_key = 'oneninesevensix2003'

bcrypt = Bcrypt(app)

# Конфигурация БД
DB_CONFIG = {
    'dbname': 'skillswap',
    'user': 'skilluser',
    'password': 'skillpass',
    'host': 'localhost'
}

UPLOAD_FOLDER = 'images/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ... остальные маршруты ...

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Получаем данные формы
        if not request.form.get('csrf_token'):
            return "CSRF токен отсутствует", 400
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        birth_date = request.form.get('birth_date')
        location = request.form.get('location')
        
        # Обработка файла
        photo_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                photo_path = f'avatars/{filename}'

        # Хеширование пароля
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO users 
                (email, password_hash, first_name, last_name, birth_date, location, photo_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (email, password_hash, first_name, last_name, birth_date, location, photo_path))
            user_id = cur.fetchone()[0]
            conn.commit()
            session['user_id'] = user_id
            return redirect(url_for('profile', user_id=user_id))
        except psycopg2.IntegrityError:
            return "Пользователь с таким email уже существует"
        finally:
            cur.close()
            conn.close()
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, password_hash FROM users WHERE email = %s', (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and bcrypt.check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return redirect(url_for('profile', user_id=user[0]))
        else:
            return "Неверный email или пароль"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

# Обновленный профиль
@app.route('/profile/<int:user_id>')
def profile(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        user_dict = {
            'id': user[0],
            'name': f"{user[3]} {user[4]}",
            'photo': user[7],
            'teach_skills': user[8] or [],
            'learn_skills': user[9] or [],
            'rating': 4.5
        }
        return render_template('profile.html', user=user_dict)
    
    return "Пользователь не найден"

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)