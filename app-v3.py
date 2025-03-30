from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from psycopg2 import IntegrityError
import psycopg2
import os
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__,
            static_folder='static',
            static_url_path='/static')
csrf = CSRFProtect(app)
app.secret_key = 'oneninesevensix2003'  # В продакшене используйте секрет из переменных окружения

bcrypt = Bcrypt(app)

# Конфигурация БД
DB_CONFIG = {
    'dbname': 'skillswap',
    'user': 'skilluser',
    'password': 'skillpass',
    'host': 'localhost'
}

UPLOAD_FOLDER = 'static/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Получение данных формы
            email = request.form['email']
            password = request.form['password']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            birth_date = request.form['birth_date']
            location = request.form['location']

            # Обработка файла
            photo_path = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(save_path)
                    photo_path = f'/static/avatars/{filename}'

            # Хеширование пароля
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute('''
                INSERT INTO users 
                (email, password_hash, first_name, last_name, birth_date, location, photo_path,
                 teach_skills, learn_skills, languages, interests, work_place, study_place, about)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                email, password_hash, first_name, last_name, 
                birth_date, location, photo_path,
                request.form.getlist('teach_skills'), 
                request.form.getlist('learn_skills'),
                request.form.getlist('languages'), 
                request.form.getlist('interests'),
                request.form.get('work_place'), 
                request.form.get('study_place'),
                request.form.get('about')
            ))
            
            user_id = cur.fetchone()[0]
            conn.commit()
            session['user_id'] = user_id
            return redirect(url_for('profile', user_id=user_id))

        except IntegrityError:
            flash("Пользователь с таким email уже существует", 'danger')
            if conn:
                conn.rollback()
            return redirect(url_for('register'))
        
        except Exception as e:
            flash(f"Ошибка регистрации: {str(e)}", 'danger')
            if conn:
                conn.rollback()
            return redirect(url_for('register'))
        
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT id, password_hash FROM users WHERE email = %s', (email,))
            user = cur.fetchone()

            if user and bcrypt.check_password_hash(user[1], password):
                session['user_id'] = user[0]
                return redirect(url_for('profile', user_id=user[0]))
            
            flash("Неверный email или пароль", 'danger')
            return redirect(url_for('login'))

        except Exception as e:
            flash(f"Ошибка входа: {str(e)}", 'danger')
            return redirect(url_for('login'))

        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/profile/<int:user_id>')
def profile(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cur.fetchone()

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
        
        flash("Пользователь не найден", 'danger')
        return redirect(url_for('index'))

    except Exception as e:
        flash(f"Ошибка загрузки профиля: {str(e)}", 'danger')
        return redirect(url_for('index'))

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

# Маршрут для сброса пароля
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Здесь должна быть логика отправки письма для сброса пароля
        flash('Инструкции отправлены на ваш email', 'success')
        return redirect(url_for('login'))
    
    if not validate_email(email):
        flash('Некорректный email', 'danger')
        return redirect(url_for('/reset_password'))
    return render_template('reset-password.html')

# Маршрут для поиска партнеров
@app.route('/search')
def search():
    # Пример получения пользователей из БД
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, first_name, last_name, teach_skills, learn_skills FROM users LIMIT 10')
    users = cur.fetchall()
    cur.close()
    conn.close()

    formatted_users = [{
        'id': u[0],
        'name': f"{u[1]} {u[2]}",
        'teach_skills': u[3] or [],
        'learn_skills': u[4] or [],
        'rating': 4.5  # Заглушка для примера
    } for u in users]

    return render_template('search.html', users=formatted_users)

# Маршрут для магазина
@app.route('/shop')
def shop():
    return render_template('shop.html')

# Маршрут для обновления профиля
@app.route('/profile/<int:user_id>/update', methods=['POST'])
def update_profile(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))

    # Получаем данные из формы
    teach_skills = request.form.getlist('teach_skills')
    learn_skills = request.form.getlist('learn_skills')

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            UPDATE users 
            SET teach_skills = %s, 
                learn_skills = %s 
            WHERE id = %s
        ''', (teach_skills, learn_skills, user_id))
        conn.commit()
        flash('Профиль успешно обновлен', 'success')
    except Exception as e:
        flash(f'Ошибка обновления: {str(e)}', 'danger')
    finally:
        if cur: cur.close()
        if conn: conn.close()
    
    return redirect(url_for('profile', user_id=user_id))



if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)