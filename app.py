from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__, 
            static_folder='images',
            static_url_path='/images')

# Заглушки данных
users = [{
    'id': 1,
    'name': 'Анна',
    'teach_skills': ['Английский B2', 'Python Basics'],
    'learn_skills': ['Испанский A1', 'Data Science'],
    'rating': 4.5
}]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print(request.form)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Здесь должна быть логика аутентификации
        print(request.form)
    return render_template('login.html')

@app.route('/search')
def search():
    return render_template('search.html', users=users)


@app.route('/profile/<int:user_id>')
def profile(user_id):
    return render_template('profile.html', user=users[0])

@app.route('/images/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/process_payment', methods=['POST'])
def process_payment():
    print("Payment processed (stub)")
    return redirect(url_for('shop'))  # Убедитесь что url_for ссылается на имя функции shop

@app.route('/reset-password')
def reset_password():
    return render_template('reset-password.html')

if __name__ == '__main__':
    app.run(debug=True)