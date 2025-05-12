from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3



app = Flask(__name__)
app.secret_key = 'simsim'  

# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load user by ID
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user[0], username=user[1])
    return None

# User class 
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Skin Concern Content
SKIN_CONCERN_INFO = {
    "Acne": {
        "description": "Acne occurs when pores become clogged with oil and dead skin. It's often caused by hormones, diet, or bacteria. Remedies include gentle cleansers, non-comedogenic products, and salicylic acid treatments.",
        "image": "https://st3.depositphotos.com/12982378/33424/i/450/depositphotos_334246094-stock-photo-young-woman-closed-eyes-touching.jpg"
    },
    "Redness": {
        "description": "Redness is often caused by sensitivity, rosacea, or irritation. It's important to use soothing ingredients like aloe, green tea, and avoid harsh exfoliants.",
        "image": "https://static.vecteezy.com/system/resources/thumbnails/057/211/203/small_2x/close-up-of-a-woman-s-face-showing-rosacea-symptoms-including-redness-and-visible-blood-vessels-on-cheeks-and-nose-with-fine-wrinkles-visible-free-photo.jpg"
    },
    "Dryness": {
        "description": "Dryness can result from weather, dehydration, or over-cleansing. Remedies include moisturizing with hyaluronic acid, using rich creams, and avoiding hot showers.",
        "image": "https://media.istockphoto.com/id/869378648/photo/young-beautiful-woman-with-dry-irritated-skin.jpg?s=612x612&w=0&k=20&c=fWlB68zgIpBQN0m2aClcdPG0l6aq-L0JJPjqBXMn21I="
    },
    "Oiliness": {
        "description": "Oily skin produces excess sebum, often leading to shine and clogged pores. Use lightweight, oil-free products and mattifying primers.",
        "image": "https://media.istockphoto.com/id/1985853351/photo/young-woman-with-greasy-skin-touching-the-face-with-her-hand-oily-skin-shine-on-the-face.jpg?s=612x612&w=0&k=20&c=JS5vlkTHr1iRhlwhQZdAWZCDHliDp9haCbeP1hhTVGw="
    }
}


# Home
@app.route('/')
def home():
    return render_template('home.html')

# Sign Up Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        conn = sqlite3.connect('beauty_products.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (first_name, last_name, username, password) VALUES (?, ?, ?, ?)",
                           (first_name, last_name, username, hashed_pw))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username already taken!"
        conn.close()
        session.pop('quiz_data', None)
        return redirect(url_for('login'))

    return render_template('signup.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('beauty_products.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            user_obj = User(id=user[0], username=username)
            login_user(user_obj)
            session.pop('quiz_data', None)
            return redirect(url_for('home'))
        else:
            return "Invalid credentials."

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()

    # Delete user's data
    cursor.execute('DELETE FROM users WHERE id = ?', (current_user.id,))
    cursor.execute('DELETE FROM results WHERE user_id = ?', (current_user.id,))
    cursor.execute('DELETE FROM favorites WHERE user_id = ?', (current_user.id,))
    conn.commit()
    conn.close()

    # Log out the user
    logout_user()
    flash('Your account has been deleted.', 'danger')

    return redirect(url_for('home'))


# Quiz Route
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    previous_answers = {}

    if current_user.is_authenticated:
        conn = sqlite3.connect('beauty_products.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT skin_type, makeup_pref, finish, concerns, price_range
            FROM results
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
        ''', (current_user.id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            previous_answers = {
                'skin_type': row[0],
                'makeup_pref': row[1],
                'finish': row[2],
                'concerns': row[3].split(',') if row[3] else [],
                'price_range': row[4]
            }

    if request.method == 'POST':
        skin_type = request.form.get('skin_type')
        makeup_pref = request.form.get('makeup_pref')
        finish = request.form.get('finish')
        concerns = request.form.getlist('concerns')
        price_range = request.form.get('price_range')

        # Save quiz answers to session (for non-logged in users)
        session['quiz_data'] = {
            'skin_type': skin_type,
            'makeup_pref': makeup_pref,
            'finish': finish,
            'concerns': concerns,
            'price_range': price_range
        }

        if current_user.is_authenticated:
            conn = sqlite3.connect('beauty_products.db')
            cursor = conn.cursor()

            cursor.execute('SELECT id FROM results WHERE user_id = ?', (current_user.id,))
            existing = cursor.fetchone()

            if existing:
                cursor.execute('''
                    UPDATE results
                    SET skin_type = ?, makeup_pref = ?, finish = ?, concerns = ?, price_range = ?
                    WHERE user_id = ?
                ''', (skin_type, makeup_pref, finish, ','.join(concerns), price_range, current_user.id))
            else:
                cursor.execute('''
                    INSERT INTO results (user_id, skin_type, makeup_pref, finish, concerns, price_range)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (current_user.id, skin_type, makeup_pref, finish, ','.join(concerns), price_range))

            conn.commit()
            conn.close()

        # Redirect to results page instead of rendering results directly
        return redirect(url_for('results'))

    return render_template('quiz.html', previous_answers=previous_answers)

# Matching function
def get_matching_products(skin_type, finish, price_range, concerns, makeup_pref):
    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()

    # Start building query
    query = '''
    SELECT brand_name, product_name, category, skin_type_match, makeup_finish, price_range, 
           concern_match, makeup_pref_match, image_url, purchase_link 
    FROM products
    WHERE 
        (skin_type_match = ? OR skin_type_match = 'All')
        AND (makeup_finish = ? OR makeup_finish = 'All')
        AND (price_range = ? OR price_range = 'Both')
        AND (makeup_pref_match = ? OR makeup_pref_match = 'Both')
    '''
    values = [skin_type, finish, price_range, makeup_pref]

    # Add concern filtering (if any)
    if concerns:
        # This will only match one concern at a time, but you could expand this for multiple concerns
        query += ' AND (concern_match = ? OR concern_match = "None" OR concern_match = "All")'
        values.append(concerns[0])  # Only using the first concern for now
    else:
        query += ' AND (concern_match = "None" OR concern_match = "All")'

    print("Query values:", values)

    cursor.execute(query, values)
    results = cursor.fetchall()
    conn.close()
    return results




# Results route
@app.route('/results', methods=['GET'])
def results():
    previous_answers = {}

    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()

    favorited_products = []
    if current_user.is_authenticated:
        cursor.execute('''
            SELECT product_name, brand_name FROM favorites
            WHERE user_id = ?
        ''', (current_user.id,))
        favorited_products = cursor.fetchall()

    if current_user.is_authenticated:
        cursor.execute('''
            SELECT skin_type, makeup_pref, finish, concerns, price_range
            FROM results
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
        ''', (current_user.id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            previous_answers = {
                'skin_type': row[0],
                'makeup_pref': row[1],
                'finish': row[2],
                'concerns': row[3].split(',') if row[3] else [],
                'price_range': row[4]
            }
        else:
            previous_answers = session.get('quiz_data', {})
    else:
        conn.close()
        previous_answers = session.get('quiz_data', {})

    if not previous_answers:
        flash('Please take the quiz first!', 'warning')
        return redirect(url_for('quiz'))

    # Filters from user selection
    selected_filters = request.args.getlist('filters')

    recommendations = get_matching_products(
        previous_answers['skin_type'],
        previous_answers['finish'],
        previous_answers['price_range'],
        previous_answers['concerns'],
        previous_answers['makeup_pref']
    )

    # If any filters selected, filter the recommendations manually
    if selected_filters:
        filtered_recommendations = []
        for rec in recommendations:
            brand_name, product_name, category, skin_type_match, makeup_finish, price_range, concern_match, makeup_pref_match, image_url, purchase_link = rec

            match_category = category in selected_filters
            match_price = price_range in selected_filters
            match_makeup_pref = makeup_pref_match in selected_filters

            if match_category or match_price or match_makeup_pref:
                filtered_recommendations.append(rec)

        recommendations = filtered_recommendations


    return render_template('results.html',
        recommendations=recommendations,
        favorited_products=favorited_products,
        selected_filters=selected_filters,
    )


@app.route('/browse')
def browse_products():
    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()

    selected_filters = request.args.getlist('filters')

    query = "SELECT brand_name, product_name, category, image_url, purchase_link FROM products WHERE 1=1"
    values = []

    if selected_filters:
        category_filters = [f for f in selected_filters if f not in ['High-end', 'Drugstore']]
        price_filters = [f for f in selected_filters if f in ['High-end', 'Drugstore']]

        if category_filters:
            placeholders = ','.join(['?'] * len(category_filters))
            query += f" AND category IN ({placeholders})"
            values.extend(category_filters)

        if price_filters:
            placeholders = ','.join(['?'] * len(price_filters))
            query += f" AND price_range IN ({placeholders})"
            values.extend(price_filters)

    cursor.execute(query, values)
    products = cursor.fetchall()

    favorited_products = []
    if current_user.is_authenticated:
        cursor.execute("SELECT product_name, brand_name FROM favorites WHERE user_id = ?", (current_user.id,))
        favorited_products = cursor.fetchall()

    conn.close()
    return render_template('browse.html',
        products=products,
        favorited_products=favorited_products,
        selected_filters=selected_filters
    )

@app.route('/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    product_name = request.form['product_name']
    brand_name = request.form['brand_name']
    category = request.form['category']
    image_url = request.form['image_url']
    purchase_link = request.form['purchase_link']

    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id FROM favorites 
        WHERE user_id = ? AND product_name = ? AND brand_name = ?
    ''', (current_user.id, product_name, brand_name))
    existing = cursor.fetchone()

    if not existing:
        cursor.execute('''
            INSERT INTO favorites (user_id, product_name, brand_name, category, image_url, purchase_link)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (current_user.id, product_name, brand_name, category, image_url, purchase_link))
        conn.commit()
        flash('Added to Wishlist! 💖', 'success')

    conn.close()

    return redirect(request.referrer or url_for('browse_products'))

@app.route('/remove_favorite', methods=['POST'])
@login_required
def remove_favorite():
    product_name = request.form['product_name']
    brand_name = request.form['brand_name']

    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM favorites
        WHERE user_id = ? AND product_name = ? AND brand_name = ?
    ''', (current_user.id, product_name, brand_name))
    conn.commit()
    conn.close()

    flash('Removed from Wishlist ❤️‍🔥', 'danger')

    return redirect(request.referrer or url_for('browse_products'))

@app.route('/wishlist')
def wishlist():
    if not current_user.is_authenticated:
        flash('You must sign in to view your Loves list! ❤️')
        return redirect(url_for('login'))

    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT product_name, brand_name, category, image_url, purchase_link
        FROM favorites
        WHERE user_id = ?
    ''', (current_user.id,))
    all_favorites = cursor.fetchall()

    selected_filters = request.args.getlist('filters')

    if selected_filters:
        filtered_favorites = []
        for fav in all_favorites:
            product_name, brand_name, category, image_url, purchase_link = fav
            match_category = category in selected_filters
            match_price = any(price in selected_filters for price in ['High-end', 'Drugstore'] if price in category or price in brand_name)
            # Keep if matches either category or price range
            if match_category or match_price:
                filtered_favorites.append(fav)
        favorites = filtered_favorites
    else:
        favorites = all_favorites

    conn.close()

    return render_template('wishlist.html',
        favorites=favorites,
        selected_filters=selected_filters
    )


@app.route('/my_account')
@login_required
def my_account():
    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()

    # Profile Info
    cursor.execute('''
        SELECT first_name, last_name, username
        FROM users
        WHERE id = ?
    ''', (current_user.id,))
    user = cursor.fetchone()
    user_info = {
        'first_name': user[0],
        'last_name': user[1],
        'username': user[2]
    }

    # Quiz Info
    cursor.execute('''
        SELECT skin_type, makeup_pref, finish, concerns, price_range
        FROM results
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    ''', (current_user.id,))
    quiz_data = cursor.fetchone()

    skin_concerns = {}

    if quiz_data and quiz_data[3]:
        concerns_list = quiz_data[3].split(',')
        for concern in concerns_list:
            concern = concern.strip()
            if concern in SKIN_CONCERN_INFO:
                skin_concerns[concern] = SKIN_CONCERN_INFO[concern]

    # Wishlist
    cursor.execute('''
        SELECT product_name, brand_name, category, image_url, purchase_link
        FROM favorites
        WHERE user_id = ?
    ''', (current_user.id,))
    favorites = cursor.fetchall()

    conn.close()

    return render_template('my_account.html',
        user_info=user_info,
        quiz_data=quiz_data,
        skin_concerns=skin_concerns,
        favorites=favorites
    )


@app.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        conn = sqlite3.connect('beauty_products.db')
        cursor = conn.cursor()

        # Get user's current password hash from database
        cursor.execute('''
            SELECT password
            FROM users
            WHERE id = ?
        ''', (current_user.id,))
        user = cursor.fetchone()

        if user and check_password_hash(user[0], current_password):
            # Current password is correct → update to new password
            new_hashed_pw = generate_password_hash(new_password)

            cursor.execute('''
                UPDATE users
                SET password = ?
                WHERE id = ?
            ''', (new_hashed_pw, current_user.id))
            conn.commit()
            conn.close()

            flash('Password updated successfully! 🔒', 'success')
            return redirect(url_for('my_account'))
        else:
            conn.close()
            flash('Current password is incorrect. Please try again. 🚫', 'danger')
            return redirect(url_for('reset_password'))

    return render_template('reset_password.html')



if __name__ == '__main__':
    app.run(debug=True)


