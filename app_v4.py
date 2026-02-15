from __future__ import annotations

import os
import secrets
import smtplib
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import psycopg2
import sqlite3
from dotenv import load_dotenv
from email_validator import EmailNotValidError, validate_email as _validate_email
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from psycopg2 import IntegrityError
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')
csrf = CSRFProtect(app)

# In production, provide a strong SECRET_KEY via environment variables.
_secret_from_env = os.getenv('SECRET_KEY')
app.secret_key = _secret_from_env or 'dev-secret-key'
if not _secret_from_env or app.secret_key == 'dev-secret-key':
    print('WARNING: SECRET_KEY is not set (or uses the default dev-secret-key); do not use this in production.')

bcrypt = Bcrypt(app)

IS_SQLITE = os.getenv('DB_DIALECT', '').lower() == 'sqlite'

def _build_db_config() -> dict:
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        parsed = urlparse(database_url)
        if parsed.scheme not in {'postgres', 'postgresql'} and not IS_SQLITE:
            raise ValueError('Only postgres/postgresql DATABASE_URL is supported (set DB_DIALECT=sqlite for SQLite)')

        query = parse_qs(parsed.query)
        if IS_SQLITE:
            return {'path': parsed.path.lstrip('/') or 'database.db'}
        else:
            cfg = {
                'dbname': (parsed.path or '').lstrip('/'),
                'user': parsed.username,
                'password': parsed.password,
                'host': parsed.hostname,
                'port': parsed.port or 5432,
            }
            sslmode = (query.get('sslmode') or [None])[0] or os.getenv('DB_SSLMODE')
            if sslmode:
                cfg['sslmode'] = sslmode
            return cfg

    if IS_SQLITE:
        return {'path': os.getenv('SQLITE_PATH', 'database.db')}

    return {
        'dbname': os.getenv('DB_NAME', 'skillswap'),
        'user': os.getenv('DB_USER', 'skilluser'),
        'password': os.getenv('DB_PASSWORD', 'change-me'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
    }


DB_CONFIG = _build_db_config()

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/avatars')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

# SMTP config (support local SMTP like Mailpit for development)
SMTP_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'smtp_username': os.getenv('SMTP_USERNAME', ''),
    'smtp_password': os.getenv('SMTP_PASSWORD', ''),
    'from_email': os.getenv('SMTP_FROM', os.getenv('SMTP_USERNAME', '') or 'noreply@localhost'),
    'use_tls': os.getenv('SMTP_USE_TLS', '1').lower() not in {'0', 'false', 'no'},
}

_SCHEMA_READY = False
_SCHEMA_LOCK = threading.Lock()


def _ensure_schema(conn) -> None:
    global _SCHEMA_READY
    if _SCHEMA_READY:
        return

    with _SCHEMA_LOCK:
        if _SCHEMA_READY:
            return

        schema_file = 'create_tables_sqlite.sql' if IS_SQLITE else 'create_tables.sql'
        schema_path = Path(__file__).with_name(schema_file)
        schema_sql = schema_path.read_text(encoding='utf-8')

        if IS_SQLITE:
            # sqlite3 cursor is not a context manager; executescript supports multiple statements.
            conn.executescript(schema_sql)
        else:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            conn.commit()

        _SCHEMA_READY = True

def get_db_connection():
    try:
        if IS_SQLITE:
            conn = sqlite3.connect(DB_CONFIG['path'], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            conn.row_factory = sqlite3.Row
        else:
            conn = psycopg2.connect(**DB_CONFIG)
        _ensure_schema(conn)
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к БД: {e}")
        raise


@contextmanager
def db_cursor():
    conn = get_db_connection()
    try:
        if IS_SQLITE:
            cur = conn.cursor()
            try:
                yield cur
                conn.commit()
            finally:
                cur.close()
        else:
            with conn:
                with conn.cursor() as cur:
                    yield cur
    finally:
        conn.close()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS and \
           len(filename) <= 255  # Добавляем проверку длины имени файла

def validate_email(email):
    if not email:
        return False
    try:
        _validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return False
    return True

def get_user_exchanges(user_id):
    with db_cursor() as cur:
        cur.execute('''
            SELECT id, title, progress, status 
            FROM exchanges 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 5
        ''', (user_id,))
        return cur.fetchall()

def send_reset_email(email, reset_link):
    msg = MIMEMultipart()
    msg['From'] = SMTP_CONFIG['from_email']
    msg['To'] = email
    msg['Subject'] = 'Восстановление пароля - Skill Exchange Platform'
    
    body = f"""
    Здравствуйте!
    
    Для сброса пароля перейдите по следующей ссылке:
    {reset_link}
    
    Ссылка действительна в течение 1 часа.
    
    Если вы не запрашивали сброс пароля, проигнорируйте это письмо.
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_CONFIG['smtp_server'], SMTP_CONFIG['smtp_port'], timeout=10)
        server.ehlo()
        if SMTP_CONFIG['use_tls']:
            server.starttls()
            server.ehlo()
        if SMTP_CONFIG['smtp_username'] and SMTP_CONFIG['smtp_password']:
            server.login(SMTP_CONFIG['smtp_username'], SMTP_CONFIG['smtp_password'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {str(e)}")
        return False

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
                    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}_{filename}"
                    save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(save_path)
                    photo_path = f'/static/avatars/{unique_filename}'

            # Хеширование пароля
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

            conn = get_db_connection()
            cur = conn.cursor()
            
            # Создаем пользователя
            if IS_SQLITE:
                cur.execute('''
                    INSERT INTO users 
                    (email, password_hash, first_name, last_name, birth_date, location, photo_path,
                     work_place, study_place, about,
                     social_vk, social_tg, social_gh)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    email, password_hash, first_name, last_name, 
                    birth_date, location, photo_path,
                    request.form.get('work_place'), 
                    request.form.get('study_place'),
                    request.form.get('about'),
                    request.form.get('social_vk'),
                    request.form.get('social_tg'),
                    request.form.get('social_gh')
                ))
                user_id = cur.lastrowid
            else:
                cur.execute('''
                    INSERT INTO users 
                    (email, password_hash, first_name, last_name, birth_date, location, photo_path,
                     work_place, study_place, about,
                     social_vk, social_tg, social_gh)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    email, password_hash, first_name, last_name, 
                    birth_date, location, photo_path,
                    request.form.get('work_place'), 
                    request.form.get('study_place'),
                    request.form.get('about'),
                    request.form.get('social_vk'),
                    request.form.get('social_tg'),
                    request.form.get('social_gh')
                ))
                user_id = cur.fetchone()[0]
            
            # Добавляем навыки
            def add_skills(skills, skill_type):
                for name in skills:
                    cur.execute('SELECT id FROM skills WHERE name = %s' if not IS_SQLITE else 'SELECT id FROM skills WHERE name = ?', (name,))
                    row = cur.fetchone()
                    if row:
                        cur.execute('''
                            INSERT INTO user_skills (user_id, skill_id, skill_type)
                            VALUES (%s, %s, %s)
                            ON CONFLICT DO NOTHING
                        ''' if not IS_SQLITE else '''
                            INSERT OR IGNORE INTO user_skills (user_id, skill_id, skill_type)
                            VALUES (?, ?, ?)
                        ''', (user_id, row[0], skill_type))
            
            add_skills(request.form.getlist('teach_skills'), 'teach')
            add_skills(request.form.getlist('learn_skills'), 'learn')
            
            conn.commit()
            session['user_id'] = user_id
            return redirect(url_for('profile', user_id=user_id))

        except (IntegrityError, sqlite3.IntegrityError):
            flash("Пользователь с таким email уже существует", 'danger')
            if 'conn' in locals():
                conn.rollback()
            return redirect(url_for('register'))
        
        except Exception as e:
            flash(f"Ошибка регистрации: {str(e)}", 'danger')
            if 'conn' in locals():
                conn.rollback()
            return redirect(url_for('register'))
        
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()

    # Получаем список всех доступных навыков для формы
    with db_cursor() as cur:
        cur.execute('SELECT name, category FROM skills ORDER BY category, name')
        skills = cur.fetchall()
    
    # Группируем навыки по категориям
    skills_by_category = {}
    for skill_name, category in skills:
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill_name)
    
    return render_template('register.html', skills_by_category=skills_by_category)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Do not wipe the whole session here (it would log the user out).
        session.pop('_flashes', None)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        with db_cursor() as cur:
            cur.execute('SELECT id, password_hash FROM users WHERE email = %s' if not IS_SQLITE else 'SELECT id, password_hash FROM users WHERE email = ?', (email,))
            user = cur.fetchone()
        
        if user and bcrypt.check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return redirect(url_for('lk', user_id=user[0]))
        else:
            flash('Неверный email или пароль', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/profile/<int:user_id>')
def profile(user_id):
    with db_cursor() as cur:
        # Получаем информацию о пользователе
        cur.execute('''
            SELECT u.id, u.first_name, u.last_name, u.birth_date, u.location, 
                   u.photo_path, u.about,
                   u.work_place, u.study_place, u.social_vk, u.social_tg, u.social_gh,
                   COUNT(DISTINCT r.id) as review_count,
                   AVG(r.rating) as avg_rating
            FROM users u
            LEFT JOIN reviews r ON u.id = r.reviewed_id
            WHERE u.id = ?
            GROUP BY u.id
        ''' if IS_SQLITE else '''
            SELECT u.id, u.first_name, u.last_name, u.birth_date, u.location, 
                   u.photo_path, u.about,
                   u.work_place, u.study_place, u.social_vk, u.social_tg, u.social_gh,
                   COUNT(DISTINCT r.id) as review_count,
            AVG(r.rating) as avg_rating
        FROM users u
        LEFT JOIN reviews r ON u.id = r.reviewed_id
        WHERE u.id = ?
        GROUP BY u.id
    ''' if IS_SQLITE else '''
        SELECT u.id, u.first_name, u.last_name, u.birth_date, u.location, 
               u.photo_path, u.about,
               u.work_place, u.study_place, u.social_vk, u.social_tg, u.social_gh,
               COUNT(DISTINCT r.id) as review_count,
               AVG(r.rating) as avg_rating
        FROM users u
        LEFT JOIN reviews r ON u.id = r.reviewed_id
        WHERE u.id = %s
        GROUP BY u.id
    ''', (user_id,))
        
        user = cur.fetchone()
        if not user:
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('search'))
        
        # Получаем навыки пользователя
        cur.execute('''
            SELECT s.name, us.skill_type
            FROM user_skills us
            JOIN skills s ON us.skill_id = s.id
            WHERE us.user_id = ?
        ''' if IS_SQLITE else '''
            SELECT s.name, us.skill_type
            FROM user_skills us
            JOIN skills s ON us.skill_id = s.id
            WHERE us.user_id = %s
        ''', (user_id,))
        
        skills = cur.fetchall()
        teach_skills = [skill[0] for skill in skills if skill[1] == 'teach']
        learn_skills = [skill[0] for skill in skills if skill[1] == 'learn']
        
        # Получаем все доступные навыки для формы
        cur.execute('SELECT name, category FROM skills ORDER BY category, name')
        all_skills = cur.fetchall()
        
        # Группируем навыки по категориям
        skills_by_category = {}
        for skill_name, category in all_skills:
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(skill_name)
        
        # Получаем отзывы о пользователе
        cur.execute('''
            SELECT r.id, r.rating, r.comment, r.created_at,
                   u.first_name, u.last_name
            FROM reviews r
            JOIN users u ON r.reviewer_id = u.id
            WHERE r.reviewed_id = ?
            ORDER BY r.created_at DESC
        ''' if IS_SQLITE else '''
            SELECT r.id, r.rating, r.comment, r.created_at,
                   u.first_name, u.last_name
            FROM reviews r
            JOIN users u ON r.reviewer_id = u.id
            WHERE r.reviewed_id = %s
            ORDER BY r.created_at DESC
        ''', (user_id,))
        
        reviews = cur.fetchall()
        
        # Получаем доступные слоты
        cur.execute(('''
            SELECT id, start_time, end_time, is_booked
            FROM available_slots
            WHERE user_id = %s AND start_time >= {now}
            ORDER BY start_time
        ''' if not IS_SQLITE else '''
            SELECT id, start_time, end_time, is_booked
            FROM available_slots
            WHERE user_id = ? AND start_time >= CURRENT_TIMESTAMP
            ORDER BY start_time
        ''').format(now='NOW()'), (user_id,))
        
        slots = cur.fetchall()
        
        # Получаем активные встречи
        cur.execute(('''
            SELECT m.id, m.platform, m.meeting_link, m.scheduled_time,
                   u.first_name, u.last_name
            FROM meetings m
            JOIN users u ON m.initiator_id = u.id
            WHERE (m.initiator_id = %s OR m.participant_id = %s)
            AND m.scheduled_time >= NOW()
            ORDER BY m.scheduled_time
        ''' if not IS_SQLITE else '''
            SELECT m.id, m.platform, m.meeting_link, m.scheduled_time,
                   u.first_name, u.last_name
            FROM meetings m
            JOIN users u ON m.initiator_id = u.id
            WHERE (m.initiator_id = ? OR m.participant_id = ?)
            AND m.scheduled_time >= CURRENT_TIMESTAMP
            ORDER BY m.scheduled_time
        '''), (user_id, user_id))
        
        meetings = cur.fetchall()
    
    user_data = {
        'id': user[0],
        'first_name': user[1],
        'last_name': user[2],
        'birth_date': user[3],
        'location': user[4],
        'photo_path': user[5],
        'about': user[6],
        'work_place': user[7],
        'study_place': user[8],
        'social_vk': user[9],
        'social_tg': user[10],
        'social_gh': user[11],
        'rating': float(user[13]) if user[13] else 0,
        'review_count': user[12] or 0,
        'teach_skills': teach_skills,
        'learn_skills': learn_skills
    }
    
    reviews_data = [{
        'id': r[0],
        'rating': r[1],
        'comment': r[2],
        'created_at': r[3],
        'reviewer_name': f"{r[4]} {r[5]}"
    } for r in reviews]
    
    slots_data = [{
        'id': s[0],
        'start_time': s[1],
        'end_time': s[2],
        'is_booked': s[3]
    } for s in slots]
    
    meetings_data = [{
        'id': m[0],
        'platform': m[1],
        'meeting_link': m[2],
        'scheduled_time': m[3],
        'initiator_name': f"{m[4]} {m[5]}"
    } for m in meetings]
    
    return render_template('profile.html', 
                         user=user_data,
                         reviews=reviews_data,
                         slots=slots_data,
                         meetings=meetings_data,
                         skills_by_category=skills_by_category,
                         is_own_profile=False)

@app.route('/profile/<int:user_id>/review', methods=['POST'])
def add_review(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session['user_id'] == user_id:
        flash('Вы не можете оставить отзыв о себе', 'danger')
        return redirect(url_for('profile', user_id=user_id))
    
    try:
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment')
        
        if not (1 <= rating <= 5):
            flash('Некорректная оценка', 'danger')
            return redirect(url_for('profile', user_id=user_id))
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверяем, не оставлял ли пользователь уже отзыв
        cur.execute('''
            SELECT id FROM reviews 
            WHERE reviewer_id = %s AND reviewed_id = %s
        ''', (session['user_id'], user_id))
        
        if cur.fetchone():
            flash('Вы уже оставляли отзыв этому пользователю', 'danger')
            return redirect(url_for('profile', user_id=user_id))
        
        # Добавляем отзыв
        cur.execute('''
            INSERT INTO reviews (reviewer_id, reviewed_id, rating, comment)
            VALUES (%s, %s, %s, %s)
        ''', (session['user_id'], user_id, rating, comment))
        
        conn.commit()
        flash('Отзыв успешно добавлен', 'success')
        
    except Exception as e:
        flash(f'Ошибка добавления отзыва: {str(e)}', 'danger')
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    
    return redirect(url_for('profile', user_id=user_id))

@app.route('/api/available-slots')
def get_available_slots():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify([])
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(('''
            SELECT start_time, end_time
            FROM available_slots
            WHERE user_id = %s AND is_booked = FALSE
            AND start_time > NOW()
            ORDER BY start_time
        ''' if not IS_SQLITE else '''
            SELECT start_time, end_time
            FROM available_slots
            WHERE user_id = ?
              AND is_booked = 0
              AND start_time > CURRENT_TIMESTAMP
            ORDER BY start_time
        '''), (user_id,))
        
        slots = [{
            'start': s[0].isoformat(),
            'end': s[1].isoformat(),
            'title': 'Доступное время'
        } for s in cur.fetchall()]
        
        return jsonify(slots)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if not validate_email(email):
            flash('Некорректный email', 'danger')
            return redirect(url_for('reset_password'))
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Проверяем существование пользователя
            cur.execute('SELECT id FROM users WHERE email = %s', (email,))
            user = cur.fetchone()
            
            if user:
                # Генерируем токен
                token = secrets.token_urlsafe(32)
                expires_at = datetime.now() + timedelta(hours=1)
                
                # Сохраняем токен в БД
                cur.execute('''
                    INSERT INTO password_reset_tokens (user_id, token, expires_at)
                    VALUES (%s, %s, %s)
                ''', (user[0], token, expires_at))
                
                conn.commit()
                
                # Отправляем email
                reset_link = url_for('reset_password_confirm', token=token, _external=True)
                if send_reset_email(email, reset_link):
                    flash('Инструкции отправлены на ваш email', 'success')
                else:
                    flash('Ошибка отправки email', 'danger')
            else:
                flash('Пользователь с таким email не найден', 'danger')
            
        except Exception as e:
            flash(f'Ошибка: {str(e)}', 'danger')
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()
        
        return redirect(url_for('login'))
    
    return render_template('reset-password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_confirm(token):
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if not new_password or len(new_password) < 6:
            flash('Пароль должен быть не короче 6 символов', 'danger')
            return redirect(url_for('reset_password_confirm', token=token))
        if new_password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return redirect(url_for('reset_password_confirm', token=token))
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Проверяем токен
            cur.execute('''
                SELECT user_id, expires_at, used 
                FROM password_reset_tokens 
                WHERE token = %s
            ''', (token,))
            
            token_data = cur.fetchone()
            
            if token_data and not token_data[2] and datetime.now() < token_data[1]:
                # Обновляем пароль
                password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
                cur.execute('''
                    UPDATE users 
                    SET password_hash = %s 
                    WHERE id = %s
                ''', (password_hash, token_data[0]))
                
                # Помечаем токен как использованный
                cur.execute('''
                    UPDATE password_reset_tokens 
                    SET used = TRUE 
                    WHERE token = %s
                ''', (token,))
                
                conn.commit()
                flash('Пароль успешно изменен', 'success')
                return redirect(url_for('login'))
            else:
                flash('Недействительная или просроченная ссылка', 'danger')
                
        except Exception as e:
            flash(f'Ошибка: {str(e)}', 'danger')
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()
    
    return render_template('reset-password-confirm.html', token=token)

@app.route('/search')
def search():
    skill = request.args.get('skill', '')
    city = request.args.get('city', '')
    
    if IS_SQLITE:
        query = """
            SELECT u.id,
                   u.first_name || ' ' || u.last_name as name,
                   u.location as city,
                   u.about as description,
                   u.photo_path as avatar,
                   u.social_tg as telegram,
                   u.social_vk as vk,
                   u.social_gh as github,
                   CAST((julianday('now') - julianday(u.birth_date))/365 AS INT) as age,
                   GROUP_CONCAT(DISTINCT s.name) as skills
            FROM users u
            LEFT JOIN user_skills us ON u.id = us.user_id
            LEFT JOIN skills s ON us.skill_id = s.id
            WHERE 1=1
        """
        params = []
        
        if skill:
            query += " AND EXISTS (SELECT 1 FROM user_skills us2 JOIN skills s2 ON us2.skill_id = s2.id WHERE us2.user_id = u.id AND s2.name = ?)"
            params.append(skill)
        
        if city:
            query += " AND u.location LIKE ?"
            params.append(f"%{city}%")
        
        query += " GROUP BY u.id"
        
        with db_cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
        
        profiles = []
        for p in rows:
            skills_list = p['skills'].split(',') if p['skills'] else []
            profiles.append({
                'id': p['id'],
                'name': p['name'],
                'city': p['city'],
                'description': p['description'],
                'avatar': p['avatar'],
                'telegram': p['telegram'],
                'vk': p['vk'],
                'github': p['github'],
                'age': int(p['age']) if p['age'] is not None else None,
                'skills': skills_list
            })
    else:
        query = """
            SELECT u.id, 
                   CONCAT(u.first_name, ' ', u.last_name) as name,
                   u.location as city,
                   u.about as description,
                   u.photo_path as avatar,
                   u.social_tg as telegram,
                   u.social_vk as vk,
                   u.social_gh as github,
                   EXTRACT(YEAR FROM age(u.birth_date)) as age,
                   array_agg(DISTINCT s.name) as skills
            FROM users u
            LEFT JOIN user_skills us ON u.id = us.user_id
            LEFT JOIN skills s ON us.skill_id = s.id
            WHERE 1=1
        """
        params = []
        
        if skill:
            query += " AND EXISTS (SELECT 1 FROM user_skills us2 JOIN skills s2 ON us2.skill_id = s2.id WHERE us2.user_id = u.id AND s2.name = %s)"
            params.append(skill)
        
        if city:
            query += " AND u.location ILIKE %s"
            params.append(f"%{city}%")
        
        query += " GROUP BY u.id"
        
        with db_cursor() as cur:
            cur.execute(query, params)
            profiles = cur.fetchall()
            
            profiles = [{
                'id': p[0],
                'name': p[1],
                'city': p[2],
                'description': p[3],
                'avatar': p[4],
                'telegram': p[5],
                'vk': p[6],
                'github': p[7],
                'age': int(p[8]) if p[8] else None,
                'skills': p[9] if p[9] else []
            } for p in profiles]
    
    # Получаем все доступные навыки для фильтра
    with db_cursor() as cur:
        cur.execute('SELECT name, category FROM skills ORDER BY category, name')
        skills = cur.fetchall()
        
        # Группируем навыки по категориям
        skills_by_category = {}
        for skill_name, category in skills:
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(skill_name)
    
    return render_template('search.html', 
                         profiles=profiles,
                         skills_by_category=skills_by_category)

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/profile/<int:user_id>/update', methods=['POST'])
def update_profile(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))

    try:
        print("=== Начало обработки обновления профиля ===")
        print(f"User ID: {user_id}")
        print("Request form:", dict(request.form))
        print("Request files:", dict(request.files))

        # Обработка файла
        photo_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(save_path)
                photo_path = f'/static/avatars/{unique_filename}'
                print(f"Фото сохранено: {photo_path}")

        # Обновление данных
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверяем существование пользователя
        cur.execute('SELECT id FROM users WHERE id = %s' if not IS_SQLITE else 'SELECT id FROM users WHERE id = ?', (user_id,))
        if not cur.fetchone():
            print(f"Пользователь {user_id} не найден")
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('index'))
        
        # Собираем данные формы
        form_data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'location': request.form.get('location'),
            'work_place': request.form.get('work_place'),
            'study_place': request.form.get('study_place'),
            'about': request.form.get('about'),
            'social_vk': request.form.get('social_vk'),
            'social_tg': request.form.get('social_tg'),
            'social_gh': request.form.get('social_gh')
        }
        
        print("Собранные данные формы:", form_data)
        
        # Обновляем основные данные
        try:
            update_query = '''
                UPDATE users SET
                    first_name = %s,
                    last_name = %s,
                    location = %s,
                    work_place = %s,
                    study_place = %s,
                    about = %s,
                    social_vk = %s,
                    social_tg = %s,
                    social_gh = %s,
                    photo_path = COALESCE(%s, photo_path)
                WHERE id = %s
            '''
            update_params = (
                form_data['first_name'],
                form_data['last_name'],
                form_data['location'],
                form_data['work_place'],
                form_data['study_place'],
                form_data['about'],
                form_data['social_vk'],
                form_data['social_tg'],
                form_data['social_gh'],
                photo_path,
                user_id
            )
            print("SQL запрос:", update_query)
            print("Параметры запроса:", update_params)
            
            cur.execute(update_query, update_params)
            print("Основные данные успешно обновлены")
        except Exception as e:
            print(f"Ошибка при обновлении основных данных: {str(e)}")
            raise
        
        # Обновляем навыки
        try:
            # Удаляем старые навыки
            cur.execute('DELETE FROM user_skills WHERE user_id = %s' if not IS_SQLITE else 'DELETE FROM user_skills WHERE user_id = ?', (user_id,))
            
            def add_skills(skills, skill_type):
                for name in skills:
                    cur.execute('SELECT id FROM skills WHERE name = %s' if not IS_SQLITE else 'SELECT id FROM skills WHERE name = ?', (name,))
                    row = cur.fetchone()
                    if row:
                        cur.execute('''
                            INSERT INTO user_skills (user_id, skill_id, skill_type)
                            VALUES (%s, %s, %s)
                            ON CONFLICT DO NOTHING
                        ''' if not IS_SQLITE else '''
                            INSERT OR IGNORE INTO user_skills (user_id, skill_id, skill_type)
                            VALUES (?, ?, ?)
                        ''', (user_id, row[0], skill_type))
            
            add_skills(request.form.getlist('teach_skills'), 'teach')
            add_skills(request.form.getlist('learn_skills'), 'learn')
            
            print("Навыки успешно обновлены")
        except Exception as e:
            print(f"Ошибка при обновлении навыков: {str(e)}")
            raise
        
        conn.commit()
        print("Транзакция успешно зафиксирована")
        flash('Профиль успешно обновлен', 'success')

    except Exception as e:
        print(f"Общая ошибка в update_profile: {str(e)}")
        flash(f'Ошибка обновления: {str(e)}', 'danger')
        if 'conn' in locals():
            conn.rollback()
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    
    print("=== Завершение обработки обновления профиля ===")
    return redirect(url_for('lk', user_id=user_id))

@app.route('/profile/<int:user_id>/add-slot', methods=['POST'])
def add_available_slot(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))

    try:
        start_time = datetime.fromisoformat(request.form.get('start_time'))
        end_time = datetime.fromisoformat(request.form.get('end_time'))
        
        # Проверяем корректность времени
        if start_time >= end_time:
            flash('Время окончания должно быть позже времени начала', 'danger')
            return redirect(url_for('profile', user_id=user_id))
            
        if start_time < datetime.now():
            flash('Нельзя добавить слот в прошлом времени', 'danger')
            return redirect(url_for('profile', user_id=user_id))
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверяем наложение слотов
        cur.execute('''
            SELECT COUNT(*) FROM available_slots 
            WHERE user_id = %s 
            AND is_booked = FALSE
            AND (
                (start_time <= %s AND end_time > %s) OR
                (start_time < %s AND end_time >= %s)
            )
        ''', (user_id, end_time, start_time, end_time, start_time))
        
        if cur.fetchone()[0] > 0:
            flash('Это время уже занято', 'danger')
            return redirect(url_for('profile', user_id=user_id))
        
        cur.execute('''
            INSERT INTO available_slots (user_id, start_time, end_time)
            VALUES (%s, %s, %s)
        ''', (user_id, start_time, end_time))
        
        conn.commit()
        flash('Слот успешно добавлен', 'success')
        
    except ValueError:
        flash('Некорректный формат времени', 'danger')
    except Exception as e:
        flash(f'Ошибка добавления слота: {str(e)}', 'danger')
        if 'conn' in locals():
            conn.rollback()
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    
    return redirect(url_for('profile', user_id=user_id))

@app.route('/lk/<int:user_id>')
def lk(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))

    with db_cursor() as cur:
        # Получаем информацию о пользователе
        cur.execute('''
            SELECT u.id, u.first_name, u.last_name, u.birth_date, u.location, 
                   u.photo_path, u.about,
                   u.work_place, u.study_place, u.social_vk, u.social_tg, u.social_gh,
                   COUNT(DISTINCT r.id) as review_count,
                   AVG(r.rating) as avg_rating
            FROM users u
            LEFT JOIN reviews r ON u.id = r.reviewed_id
            WHERE u.id = ?
            GROUP BY u.id
        ''' if IS_SQLITE else '''
            SELECT u.id, u.first_name, u.last_name, u.birth_date, u.location, 
                   u.photo_path, u.about,
                   u.work_place, u.study_place, u.social_vk, u.social_tg, u.social_gh,
                   COUNT(DISTINCT r.id) as review_count,
                   AVG(r.rating) as avg_rating
            FROM users u
            LEFT JOIN reviews r ON u.id = r.reviewed_id
            WHERE u.id = %s
            GROUP BY u.id
        ''', (user_id,))
        
        user = cur.fetchone()
        if not user:
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('search'))

        # Навыки пользователя (user_skills)
        cur.execute('''
            SELECT s.name, us.skill_type
            FROM user_skills us
            JOIN skills s ON us.skill_id = s.id
            WHERE us.user_id = ?
        ''' if IS_SQLITE else '''
            SELECT s.name, us.skill_type
            FROM user_skills us
            JOIN skills s ON us.skill_id = s.id
            WHERE us.user_id = %s
        ''', (user_id,))
        skills = cur.fetchall()
        teach_skills = [skill[0] for skill in skills if skill[1] == 'teach']
        learn_skills = [skill[0] for skill in skills if skill[1] == 'learn']

        # Все навыки для чекбоксов
        cur.execute('SELECT name FROM skills ORDER BY category, name')
        all_skills = [row[0] for row in cur.fetchall()]
        
        # Получаем отзывы о пользователе
        cur.execute('''
            SELECT r.id, r.rating, r.comment, r.created_at,
                   u.first_name, u.last_name
            FROM reviews r
            JOIN users u ON r.reviewer_id = u.id
            WHERE r.reviewed_id = ?
            ORDER BY r.created_at DESC
        ''' if IS_SQLITE else '''
            SELECT r.id, r.rating, r.comment, r.created_at,
                   u.first_name, u.last_name
            FROM reviews r
            JOIN users u ON r.reviewer_id = u.id
            WHERE r.reviewed_id = %s
            ORDER BY r.created_at DESC
        ''', (user_id,))
        
        reviews = cur.fetchall()
        
        # Получаем доступные слоты
        cur.execute(('''
            SELECT id, start_time, end_time, is_booked
            FROM available_slots
            WHERE user_id = %s AND start_time >= NOW()
            ORDER BY start_time
        ''' if not IS_SQLITE else '''
            SELECT id, start_time, end_time, is_booked
            FROM available_slots
            WHERE user_id = ? AND start_time >= CURRENT_TIMESTAMP
            ORDER BY start_time
        '''), (user_id,))
        
        slots = cur.fetchall()
        
        # Получаем статистику обменов
        cur.execute(('''
            SELECT 
                COUNT(*) FILTER (WHERE status = 'completed') as completed,
                COUNT(*) FILTER (WHERE status = 'active') as active
            FROM exchanges 
            WHERE user_id = %s
        ''' if not IS_SQLITE else '''
            SELECT 
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active
            FROM exchanges 
            WHERE user_id = ?
        '''), (user_id,))
        
        stats = cur.fetchone()
        
        # Получаем предложенные встречи
        cur.execute(('''
            SELECT m.id, m.platform, m.meeting_link, m.scheduled_time,
                   u.first_name, u.last_name
            FROM meetings m
            JOIN users u ON m.initiator_id = u.id
            WHERE m.participant_id = %s
            AND m.status = 'pending'
            AND m.scheduled_time >= NOW()
            ORDER BY m.scheduled_time
        ''' if not IS_SQLITE else '''
            SELECT m.id, m.platform, m.meeting_link, m.scheduled_time,
                   u.first_name, u.last_name
            FROM meetings m
            JOIN users u ON m.initiator_id = u.id
            WHERE m.participant_id = ?
            AND m.status = 'pending'
            AND m.scheduled_time >= CURRENT_TIMESTAMP
            ORDER BY m.scheduled_time
        '''), (user_id,))
        
        pending_meetings = cur.fetchall()
        
        # Получаем подтвержденные встречи
        cur.execute(('''
            SELECT m.id, m.platform, m.meeting_link, m.scheduled_time,
                   m.initiator_id, m.participant_id,
                   CONCAT(ui.first_name, ' ', ui.last_name) as initiator_name,
                   CONCAT(up.first_name, ' ', up.last_name) as participant_name
            FROM meetings m
            JOIN users ui ON m.initiator_id = ui.id
            JOIN users up ON m.participant_id = up.id
            WHERE (m.initiator_id = %s OR m.participant_id = %s)
            AND m.status = 'confirmed'
            AND m.scheduled_time >= NOW()
            ORDER BY m.scheduled_time
        ''' if not IS_SQLITE else '''
            SELECT m.id, m.platform, m.meeting_link, m.scheduled_time,
                   m.initiator_id, m.participant_id,
                   ui.first_name || ' ' || ui.last_name as initiator_name,
                   up.first_name || ' ' || up.last_name as participant_name
            FROM meetings m
            JOIN users ui ON m.initiator_id = ui.id
            JOIN users up ON m.participant_id = up.id
            WHERE (m.initiator_id = ? OR m.participant_id = ?)
            AND m.status = 'confirmed'
            AND m.scheduled_time >= CURRENT_TIMESTAMP
            ORDER BY m.scheduled_time
        '''), (user_id, user_id))
        
        confirmed_meetings = cur.fetchall()
    
    user_data = {
        'id': user[0],
        'first_name': user[1],
        'last_name': user[2],
        'birth_date': user[3],
        'location': user[4],
        'teach_skills': teach_skills,
        'learn_skills': learn_skills,
        'photo_path': user[5],
        'about': user[6],
        'work_place': user[7],
        'study_place': user[8],
        'social_vk': user[9],
        'social_tg': user[10],
        'social_gh': user[11],
        'rating': float(user[13]) if user[13] else 0,
        'review_count': user[12] or 0,
        'stats': {
            'completed': stats[0] if stats else 0,
            'active': stats[1] if stats else 0
        }
    }
    
    reviews_data = [{
        'id': r[0],
        'rating': r[1],
        'comment': r[2],
        'created_at': r[3],
        'reviewer_name': f"{r[4]} {r[5]}"
    } for r in reviews]
    
    slots_data = [{
        'id': s[0],
        'start_time': s[1],
        'end_time': s[2],
        'is_booked': s[3]
    } for s in slots]
    
    pending_meetings_data = [{
        'id': m[0],
        'platform': m[1],
        'meeting_link': m[2],
        'scheduled_time': m[3],
        'initiator_name': f"{m[4]} {m[5]}"
    } for m in pending_meetings]
    
    confirmed_meetings_data = [{
        'id': m[0],
        'platform': m[1],
        'meeting_link': m[2],
        'scheduled_time': m[3],
        'initiator_id': m[4],
        'participant_id': m[5],
        'initiator_name': m[6],
        'participant_name': m[7]
    } for m in confirmed_meetings]
    
    return render_template('lk.html', 
                         user=user_data,
                         reviews=reviews_data,
                         slots=slots_data,
                         pending_meetings=pending_meetings_data,
                         confirmed_meetings=confirmed_meetings_data,
                         all_skills=all_skills)

@app.route('/profile/<int:user_id>/create-meeting', methods=['POST'])
def create_meeting(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        platform = request.form.get('platform')
        meeting_link = request.form.get('meeting_link')
        scheduled_time = datetime.fromisoformat(request.form.get('scheduled_time'))
        
        if not all([platform, meeting_link, scheduled_time]):
            flash('Пожалуйста, заполните все поля', 'danger')
            return redirect(url_for('profile', user_id=user_id))
        
        if scheduled_time < datetime.now():
            flash('Нельзя создать встречу в прошлом времени', 'danger')
            return redirect(url_for('profile', user_id=user_id))
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Создаем встречу
        cur.execute('''
            INSERT INTO meetings (initiator_id, participant_id, platform, meeting_link, scheduled_time)
            VALUES (%s, %s, %s, %s, %s)
        ''', (session['user_id'], user_id, platform, meeting_link, scheduled_time))
        
        conn.commit()
        flash('Встреча успешно создана', 'success')
        
    except Exception as e:
        flash(f'Ошибка создания встречи: {str(e)}', 'danger')
        if 'conn' in locals():
            conn.rollback()
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    
    return redirect(url_for('profile', user_id=user_id))

@app.route('/meeting/<int:meeting_id>/accept', methods=['POST'])
def accept_meeting(meeting_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверяем, что пользователь является участником встречи
        cur.execute('''
            SELECT participant_id, status
            FROM meetings
            WHERE id = %s
        ''', (meeting_id,))
        
        meeting = cur.fetchone()
        if not meeting or meeting[0] != session['user_id'] or meeting[1] != 'pending':
            flash('Невозможно принять эту встречу', 'danger')
            return redirect(url_for('lk', user_id=session['user_id']))
        
        # Обновляем статус встречи
        cur.execute('''
            UPDATE meetings
            SET status = 'confirmed'
            WHERE id = %s
        ''', (meeting_id,))
        
        conn.commit()
        flash('Встреча успешно принята', 'success')
        
    except Exception as e:
        flash(f'Ошибка при принятии встречи: {str(e)}', 'danger')
        if 'conn' in locals():
            conn.rollback()
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    
    return redirect(url_for('lk', user_id=session['user_id']))

@app.route('/meeting/<int:meeting_id>/reject', methods=['POST'])
def reject_meeting(meeting_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверяем, что пользователь является участником встречи
        cur.execute('''
            SELECT participant_id, status
            FROM meetings
            WHERE id = %s
        ''', (meeting_id,))
        
        meeting = cur.fetchone()
        if not meeting or meeting[0] != session['user_id'] or meeting[1] != 'pending':
            flash('Невозможно отклонить эту встречу', 'danger')
            return redirect(url_for('lk', user_id=session['user_id']))
        
        # Обновляем статус встречи
        cur.execute('''
            UPDATE meetings
            SET status = 'rejected'
            WHERE id = %s
        ''', (meeting_id,))
        
        conn.commit()
        flash('Встреча отклонена', 'success')
        
    except Exception as e:
        flash(f'Ошибка при отклонении встречи: {str(e)}', 'danger')
        if 'conn' in locals():
            conn.rollback()
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    
    return redirect(url_for('lk', user_id=session['user_id']))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/business')
def business():
    return render_template('business.html')

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/blog')
def blog():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Получаем все статьи из базы данных
    cur.execute('''
        SELECT id, title, excerpt, author_name, article_url, created_at, views
        FROM blog_posts
        ORDER BY created_at DESC
    ''')
    posts = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('blog.html', posts=posts)

@app.route('/blog/increment-views/<int:post_id>', methods=['POST'])
def increment_views(post_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if IS_SQLITE:
            cur.execute('UPDATE blog_posts SET views = views + 1 WHERE id = ?', (post_id,))
            cur.execute('SELECT views FROM blog_posts WHERE id = ?', (post_id,))
            row = cur.fetchone()
            conn.commit()
            return jsonify({'views': row[0] if row else 0})
        else:
            cur.execute('''
                UPDATE blog_posts 
                SET views = views + 1 
                WHERE id = %s 
                RETURNING views
            ''', (post_id,))
            
            new_views = cur.fetchone()[0]
            conn.commit()
            
            return jsonify({'views': new_views})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@app.route('/join-challenge', methods=['GET'])
def join_challenge_page():
    return render_template('join-challenge.html')

@app.route('/join-challenge/<challenge_type>', methods=['POST'])
def join_challenge(challenge_type):
    if 'user_id' not in session:
        flash('Для участия в челлендже необходимо войти в систему', 'danger')
        return redirect(url_for('login'))
    
    # Здесь будет логика добавления пользователя в челлендж
    flash('Вы успешно присоединились к челленджу!', 'success')
    return redirect(url_for('community'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Здесь будет логика отправки сообщения
        flash('Сообщение успешно отправлено!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/event/python-masterclass', methods=['GET'])
def python_masterclass():
    return render_template('event/python-masterclass.html')

@app.route('/blog/python-guide', methods=['GET'])
def python_guide():
    return render_template('blog/python-guide.html')

@app.route('/blog/networking-tips', methods=['GET'])
def networking_tips():
    return render_template('blog/networking-tips.html')

@app.route('/join-random-coffee', methods=['GET', 'POST'])
def join_random_coffee():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Для создания встречи необходимо войти в систему', 'danger')
            return redirect(url_for('login'))
        
        try:
            title = request.form.get('title')
            date = request.form.get('date')
            city = request.form.get('city')
            description = request.form.get('description')
            is_online = request.form.get('is_online') == 'on'
            link = request.form.get('link')
            
            # Проверяем обязательные поля
            if not all([title, date, description, link]):
                flash('Пожалуйста, заполните все обязательные поля', 'danger')
                return redirect(url_for('join_random_coffee'))
            
            # Проверяем город только для оффлайн-встреч
            if not is_online and not city:
                flash('Для оффлайн-встречи необходимо указать город', 'danger')
                return redirect(url_for('join_random_coffee'))
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Получаем информацию о пользователе
            cur.execute('''
                SELECT first_name, last_name, birth_date
                FROM users
                WHERE id = %s
            ''', (session['user_id'],))
            
            user = cur.fetchone()
            if not user:
                flash('Пользователь не найден', 'danger')
                return redirect(url_for('join_random_coffee'))
            
            # Вычисляем возраст
            birth_date = user[2]
            if isinstance(birth_date, str):
                try:
                    birth_date = datetime.fromisoformat(birth_date).date()
                except Exception:
                    birth_date = datetime.now().date()
            age = (datetime.now().date() - birth_date).days // 365
            
            # Создаем встречу
            cur.execute('''
                INSERT INTO random_coffee_meetings 
                (organizer_id, title, date, city, description, is_online, link, organizer_name, organizer_age)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''' if IS_SQLITE else '''
                INSERT INTO random_coffee_meetings 
                (organizer_id, title, date, city, description, is_online, link, organizer_name, organizer_age)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                session['user_id'],
                date,
                title,
                city if not is_online else 'Онлайн',
                description,
                is_online,
                link,
                f"{user[0]} {user[1]}",
                age
            ))
            
            conn.commit()
            flash('Встреча успешно создана!', 'success')
            
        except Exception as e:
            flash(f'Ошибка при создании встречи: {str(e)}', 'danger')
            if 'conn' in locals():
                conn.rollback()
        
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()
        
        return redirect(url_for('join_random_coffee'))
    
    # Получаем список активных встреч
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(('''
        SELECT id, title, date, city, description, is_online, link, organizer_name, organizer_age
        FROM random_coffee_meetings
        WHERE date >= NOW()
        ORDER BY date
    ''' if not IS_SQLITE else '''
        SELECT id, title, date, city, description, is_online, link, organizer_name, organizer_age
        FROM random_coffee_meetings
        WHERE date >= CURRENT_TIMESTAMP
        ORDER BY date
    '''))
    
    meetings = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Преобразуем результаты в список словарей
    meetings_data = []
    for m in meetings:
        date_val = m[2]
        if isinstance(date_val, str):
            try:
                date_val = datetime.fromisoformat(date_val)
            except Exception:
                date_val = None
        formatted_date = date_val.strftime('%d.%m.%Y %H:%M') if date_val else ''
        meetings_data.append({
            'id': m[0],
            'title': m[1],
            'date': formatted_date,
            'city': m[3],
            'description': m[4],
            'is_online': m[5],
            'link': m[6],
            'organizer_name': m[7],
            'organizer_age': m[8]
        })
    
    return render_template('join-random-coffee.html', meetings=meetings_data)

@app.route('/join-mastermind', methods=['GET', 'POST'])
def join_mastermind():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Для участия в мастермайнде необходимо войти в систему', 'danger')
            return redirect(url_for('login'))
        
        topic = request.form.get('topic')
        experience = request.form.get('experience')
        goals = request.form.get('goals')
        
        # Здесь будет логика добавления пользователя в мастермайнд
        flash('Вы успешно присоединились к мастермайнду!', 'success')
        return redirect(url_for('community'))
    
    return render_template('join-mastermind.html')

@app.route('/event/networking-moscow', methods=['GET', 'POST'])
def networking_moscow():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Для регистрации на мероприятие необходимо войти в систему', 'danger')
            return redirect(url_for('login'))
        
        name = request.form.get('name')
        email = request.form.get('email')
        company = request.form.get('company')
        position = request.form.get('position')
        interests = request.form.get('interests')
        
        # Здесь будет логика регистрации на мероприятие
        flash('Вы успешно зарегистрировались на мероприятие!', 'success')
        return redirect(url_for('community'))
    
    return render_template('event/networking-moscow.html')

@app.route('/subscribe-newsletter', methods=['POST'])
def subscribe_newsletter():
    email = request.form.get('email')
    
    if not validate_email(email):
        flash('Пожалуйста, введите корректный email', 'danger')
        return redirect(url_for('blog'))
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверяем, не подписан ли уже этот email
        cur.execute('SELECT id FROM newsletter_subscribers WHERE email = %s', (email,))
        if cur.fetchone():
            flash('Вы уже подписаны на рассылку', 'info')
            return redirect(url_for('blog'))
        
        # Добавляем нового подписчика
        cur.execute('''
            INSERT INTO newsletter_subscribers (email)
            VALUES (%s)
        ''', (email,))
        
        conn.commit()
        flash('Спасибо за подписку!', 'success')
        
    except Exception as e:
        flash(f'Ошибка при подписке: {str(e)}', 'danger')
        if 'conn' in locals():
            conn.rollback()
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    
    return redirect(url_for('blog'))

@app.route('/blog/publish', methods=['POST'])
def publish_article():
    try:
        author_name = request.form.get('authorName')
        article_url = request.form.get('articleUrl')
        title = request.form.get('articleTitle')
        excerpt = request.form.get('articleExcerpt')
        
        if not all([author_name, article_url, title, excerpt]):
            flash('Пожалуйста, заполните все поля', 'danger')
            return redirect(url_for('blog'))
        
        # Проверяем, что URL ведет на telegra.ph
        if not article_url.startswith('https://telegra.ph/'):
            flash('Ссылка должна вести на telegra.ph', 'danger')
            return redirect(url_for('blog'))
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Добавляем статью в базу данных
        cur.execute('''
            INSERT INTO blog_posts (title, excerpt, author_name, article_url, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''' if IS_SQLITE else '''
            INSERT INTO blog_posts (title, excerpt, author_name, article_url, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        ''', (title, excerpt, author_name, article_url))
        
        conn.commit()
        flash('Статья успешно отправлена на публикацию!', 'success')
        
    except Exception as e:
        flash(f'Ошибка при публикации статьи: {str(e)}', 'danger')
        if 'conn' in locals():
            conn.rollback()
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    
    return redirect(url_for('blog'))

def main() -> None:
    Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
    debug = os.getenv('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes'}
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', '5000'))
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
