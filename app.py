"""
app.py

PURPOSE:
    This is the main Flask application for BeautyBot. It handles user authentication,
    the quiz logic, result processing, and product browsing functionality.

USAGE:
    Run with: python app.py

NOTES:
    Ensure the SQLite database is initialized beforehand using setup_users.py and populate_database.py.
    Flask-Login handles user sessions. Passwords are hashed using Werkzeug.
    Quiz results are matched against product attributes stored in the database.
"""

from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

# Initialize the Flask application
app = Flask(__name__)
# Set a secret key for session encryption and security
app.secret_key = 'simsim'  

# Configure Flask-Login
login_manager = LoginManager()

# Attach the login manager to the app
login_manager.init_app(app)

# Set the default login view when a login is required
login_manager.login_view = 'login'


"""
NAME
    load_user - loads the user from the database by ID for Flask-Login session management

SYNOPSIS
    load_user(user_id)
        user_id --> the unique ID of the user in the database

DESCRIPTION
    Retrieves user information from the database based on the provided user ID
    and returns a User object if found. This is required by Flask-Login to track
    the logged-in session.

RETURNS
    User object if the user is found, None otherwise.
"""
@login_manager.user_loader
def load_user(user_id):
    # Open a connection to the SQLite database
    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()

    # Look up the user by ID
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    # Return a User object if found, otherwise return None
    if user:
        return User(id=user[0], username=user[1])
    return None
# End of load_user(user_id)


"""
User - a class representing a logged-in user for the Flask session.

ATTRIBUTES
    id        --> the user's database ID
    username  --> the user's username (used for login)

DESCRIPTION
    This class extends Flask-Login's UserMixin and allows integration with
    Flask-Login's session management.
"""
class User(UserMixin):
    # Store user ID and username for session reference
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Skin Concern Content to display on the "My Account" page
SKIN_CONCERN_INFO = {
    "Acne": {
        "description": "Acne occurs when pores become clogged with oil and dead skin. It's often caused by "
        "hormones, diet, or bacteria. Remedies include gentle cleansers, non-comedogenic products, and salicylic acid treatments.",
        "image": "https://st3.depositphotos.com/12982378/33424/i/450/depositphotos_334246094-stock"
        "-photo-young-woman-closed-eyes-touching.jpg"
    },
    "Redness": {
        "description": "Redness is often caused by sensitivity, rosacea, or irritation. It's important to use soothing ingredients "
        "like aloe, green tea, and avoid harsh exfoliants.",
        "image": "https://static.vecteezy.com/system/resources/thumbnails/057/211/203/small_2x/close-up-of-a-woman-s-face-showing-"
        "rosacea-symptoms-including-redness-and-visible-blood-vessels-on-cheeks-and-nose-with-fine-wrinkles-visible-free-photo.jpg"
    },
    "Dryness": {
        "description": "Dryness can result from weather, dehydration, or over-cleansing. Remedies include moisturizing with hyaluronic"
        " acid, using rich creams, and avoiding hot showers.",
        "image": "https://media.istockphoto.com/id/869378648/photo/young-beautiful-woman-with-dry-irritated-skin.jpg?"
        "s=612x612&w=0&k=20&c=fWlB68zgIpBQN0m2aClcdPG0l6aq-L0JJPjqBXMn21I="
    },
    "Oiliness": {
        "description": "Oily skin produces excess sebum, often leading to shine and clogged pores. Use lightweight, oil-free "
        "products and mattifying primers.",
        "image": "https://media.istockphoto.com/id/1985853351/photo/young-woman-with-greasy-skin-touching-the-face-with-her-hand-"
        "oily-skin-shine-on-the-face.jpg?s=612x612&w=0&k=20&c=JS5vlkTHr1iRhlwhQZdAWZCDHliDp9haCbeP1hhTVGw="
    }
}

"""
NAME
    home - renders the landing page for BeautyBot

SYNOPSIS
    home()

DESCRIPTION
    Returns the homepage of the BeautyBot app where users can learn more
    about the app and navigate to other sections such as login, quiz, or browse.

RETURNS
    Renders 'home.html'.
"""
@app.route('/')
def home():
    # Render the landing page template
    return render_template('home.html')
# End of home()

"""
NAME
    signup - handles user registration

SYNOPSIS
    signup()

DESCRIPTION
    Displays a form for new user sign-up and processes the form on submission.
    Hashes the password, saves user details to the database, and redirects to the login page.
    Prevents duplicate usernames using a UNIQUE constraint.

RETURNS
    Renders 'signup.html' on GET or redirects to 'login' on successful POST.
"""
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    
    if request.method == 'POST':
        # Collect form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']

        # Hash the password before storing
        hashed_pw = generate_password_hash(password)

        # Insert new user into the database
        conn = sqlite3.connect('beauty_products.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (first_name, last_name, username, password) VALUES (?, ?, ?, ?)",
                           (first_name, last_name, username, hashed_pw))
            conn.commit()
        except sqlite3.IntegrityError:
            # Handle case where username is already taken
            return "Username already taken!"
        conn.close()

        # Clear any existing quiz session data
        session.pop('quiz_data', None)

        # Redirect new user to login page
        return redirect(url_for('login'))
    
    # Render the sign-up form
    return render_template('signup.html')
# End of signup()

"""
NAME
    login - handles user login authentication

SYNOPSIS
    login()

DESCRIPTION
    Verifies the user's credentials by checking the entered username and hashed password
    against the database. On success, initiates a user session. On failure, returns an error.

RETURNS
    Renders 'login.html' on GET, redirects to 'home' on successful POST.
"""
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form input from user
        username = request.form['username']
        password = request.form['password']

        # Query the database for the user's hashed password
        conn = sqlite3.connect('beauty_products.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        # If user exists and password matches, log them in
        if user and check_password_hash(user[1], password):
            user_obj = User(id=user[0], username=username)
            login_user(user_obj)
            session.pop('quiz_data', None)
            return redirect(url_for('home'))
        else:
            # Return an error message if authentication fails
            return "Invalid credentials."

    # Render the login form
    return render_template('login.html')
# End of login()

"""
NAME
    logout - logs the current user out of the session

SYNOPSIS
    logout()

DESCRIPTION
    Logs out the user using Flask-Login's logout_user() method and
    redirects them to the login page.

RETURNS
    Redirects to the login route.
"""
@app.route('/logout')
def logout():
    # Clear the current user session and log them out
    logout_user()
    # Redirect to the login page after logout
    return redirect(url_for('login'))
# End of logout()

"""
NAME
    delete_account - deletes a user's account and all associated data

SYNOPSIS
    delete_account()

DESCRIPTION
    Deletes the logged-in user's record from the users, results, and favorites
    tables. Also logs the user out of the session and displays a confirmation.

RETURNS
    Redirects to the home page after deletion.
"""
@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    # Connect to the SQLite database
    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()

    # Delete user's data from all relevant tables
    cursor.execute('DELETE FROM users WHERE id = ?', (current_user.id,))
    cursor.execute('DELETE FROM results WHERE user_id = ?', (current_user.id,))
    cursor.execute('DELETE FROM favorites WHERE user_id = ?', (current_user.id,))
    conn.commit()
    conn.close()

    # End the user session
    logout_user()

    # Show a flash message confirming account deletion
    flash('Your account has been deleted.', 'danger')

    # Redirect to homepage
    return redirect(url_for('home'))
# End of delete_account()

"""
NAME
    quiz - renders and processes the beauty quiz form

SYNOPSIS
    quiz()

DESCRIPTION
    Displays the quiz form on GET. On POST, stores the answers in the session or database
    depending on login state. Previously saved answers are pre-filled for logged-in users.

RETURNS
    Renders 'quiz.html' or redirects to 'results' after submission.
"""
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    previous_answers = {}

    if current_user.is_authenticated:
        # If user is logged in, attempt to retrieve their previous quiz answers
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

        # Populate form with previously saved answers if they exist
        if row:
            previous_answers = {
                'skin_type': row[0],
                'makeup_pref': row[1],
                'finish': row[2],
                'concerns': row[3].split(',') if row[3] else [],
                'price_range': row[4]
            }

    if request.method == 'POST':
        # Collect user quiz inputs from the form
        skin_type = request.form.get('skin_type')
        makeup_pref = request.form.get('makeup_pref')
        finish = request.form.get('finish')
        concerns = request.form.getlist('concerns')
        price_range = request.form.get('price_range')

        # Store quiz responses in session for non-logged-in users
        session['quiz_data'] = {
            'skin_type': skin_type,
            'makeup_pref': makeup_pref,
            'finish': finish,
            'concerns': concerns,
            'price_range': price_range
        }

        # If logged in, save or update the responses in the results table
        if current_user.is_authenticated:
            conn = sqlite3.connect('beauty_products.db')
            cursor = conn.cursor()

            # Check if result entry already exists for this user
            cursor.execute('SELECT id FROM results WHERE user_id = ?', (current_user.id,))
            existing = cursor.fetchone()

            if existing:
                # Update existing entry with new answers
                cursor.execute('''
                    UPDATE results
                    SET skin_type = ?, makeup_pref = ?, finish = ?, concerns = ?, price_range = ?
                    WHERE user_id = ?
                ''', (skin_type, makeup_pref, finish, ','.join(concerns), price_range, current_user.id))
            else:
                # Insert new record for this user
                cursor.execute('''
                    INSERT INTO results (user_id, skin_type, makeup_pref, finish, concerns, price_range)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (current_user.id, skin_type, makeup_pref, finish, ','.join(concerns), price_range))

            conn.commit()
            conn.close()

        # # Redirect to the results page after submission
        return redirect(url_for('results'))
    
    # Render quiz form with any previous answers pre-filled
    return render_template('quiz.html', previous_answers=previous_answers)
# End of quiz()


"""
NAME
    get_matching_products - retrieves a list of products matching the user's quiz results

SYNOPSIS
    get_matching_products(skin_type, finish, price_range, concerns, makeup_pref)
        skin_type    --> selected skin type
        finish       --> preferred makeup finish
        price_range  --> price range ('Drugstore', 'High-end', or 'Both')
        concerns     --> list of skin concerns
        makeup_pref  --> preferred makeup look

DESCRIPTION
    Queries the SQLite product database for products that match the user’s quiz selections.
    It handles logic for inclusive categories like 'All' and 'Both' and filters by the
    first concern if multiple are selected.

RETURNS
    A list of product records that match the criteria.
"""
def get_matching_products(skin_type, finish, price_range, concerns, makeup_pref):
    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()

    # Start building SQL query with conditionals for match logic
    query = '''
    SELECT brand_name, product_name, category, skin_type_match, makeup_finish, price_range, 
           concern_match, makeup_pref_match, image_url, purchase_link 
    FROM products
    WHERE 
        (skin_type_match = ? OR skin_type_match = 'All')
        AND (makeup_finish = ? OR makeup_finish = 'All')
        AND (makeup_pref_match = ? OR makeup_pref_match = 'Both')
    '''
    values = [skin_type, finish, makeup_pref]

    # Add skin concern filter: only filter by the first selected concern
    if concerns:
        query += ' AND (concern_match = ? OR concern_match = "None" OR concern_match = "All")'
        values.append(concerns[0])
    else:
        # Match only general/unconcerned products if no concerns selected
        query += ' AND (concern_match = "None" OR concern_match = "All")'

    # Execute query and fetch matching products
    cursor.execute(query, values)
    results = cursor.fetchall()
    conn.close()
    return results
# End of get_matching_products(skin_type, finish, price_range, concerns, makeup_pref)


"""
NAME
    results - displays product recommendations based on quiz results

SYNOPSIS
    results()

DESCRIPTION
    Retrieves the most recent quiz answers (from database if logged in or session if anonymous),
    and uses those to generate and filter recommended products. Also shows any items
    favorited by the user.

RETURNS
    Renders the 'results.html' template with recommendations and any selected filters.
"""
@app.route('/results', methods=['GET'])
def results():
    previous_answers = {}

    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()

    favorited_products = []

    # If user is logged in, fetch their favorited products
    if current_user.is_authenticated:
        cursor.execute('''
            SELECT product_name, brand_name FROM favorites
            WHERE user_id = ?
        ''', (current_user.id,))
        favorited_products = cursor.fetchall()

    # Retrieve the latest quiz answers from DB or session
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

    # Redirect if no quiz data found
    if not previous_answers:
        flash('Please take the quiz first!', 'warning')
        return redirect(url_for('quiz'))

    # Get optional filters from request
    selected_filters = request.args.getlist('filters')

    recommendations = get_matching_products(
        previous_answers['skin_type'],
        previous_answers['finish'],
        previous_answers['price_range'],
        previous_answers['concerns'],
        previous_answers['makeup_pref']
    )

    # Apply additional user-selected filters on top of quiz-matched results
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

    # Render the results page with recommended products and applied filters
    return render_template('results.html',
        recommendations=recommendations,
        favorited_products=favorited_products,
        selected_filters=selected_filters,
    )
# End of results()

"""
NAME
    browse_products - displays all products with optional filtering

SYNOPSIS
    browse_products()

DESCRIPTION
    Retrieves products from the database and optionally filters them
    by selected categories or price range. Also retrieves the current
    user's favorited products if logged in.

RETURNS
    Renders the 'browse.html' template with products and filters.
"""
@app.route('/browse')
def browse_products():
    # Connect to the database
    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()

    # Get any filters submitted from query parameters
    selected_filters = request.args.getlist('filters')

    # Query to fetch all products
    query = "SELECT brand_name, product_name, category, image_url, purchase_link FROM products WHERE 1=1"
    values = []

    # Split filters into category and price-based
    if selected_filters:
        category_filters = [f for f in selected_filters if f not in ['High-end', 'Drugstore']]
        price_filters = [f for f in selected_filters if f in ['High-end', 'Drugstore']]

        # Add category filters to the SQL query
        if category_filters:
            placeholders = ','.join(['?'] * len(category_filters))
            query += f" AND category IN ({placeholders})"
            values.extend(category_filters)

        # Add price range filters to the SQL query
        if price_filters:
            placeholders = ','.join(['?'] * len(price_filters))
            query += f" AND price_range IN ({placeholders})"
            values.extend(price_filters)

    # Execute the filtered query
    cursor.execute(query, values)
    products = cursor.fetchall()

    # Fetch wishlist products if user is logged in
    favorited_products = []
    if current_user.is_authenticated:
        cursor.execute("SELECT product_name, brand_name FROM favorites WHERE user_id = ?", (current_user.id,))
        favorited_products = cursor.fetchall()

    # Render browse page with products and filter state
    conn.close()
    return render_template('browse.html',
        products=products,
        favorited_products=favorited_products,
        selected_filters=selected_filters
    )
# End of browse_products()


"""
NAME
    add_favorite - adds a product to the logged-in user's wishlist

SYNOPSIS
    add_favorite()

DESCRIPTION
    Handles POST requests to add a selected product to the current user's favorites list.
    Avoids duplicate entries and stores product details in the 'favorites' table.

RETURNS
    Redirects back to the previous page or the browse page after adding.
"""
@app.route('/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    # Retrieve product info from the form
    product_name = request.form['product_name']
    brand_name = request.form['brand_name']
    category = request.form['category']
    image_url = request.form['image_url']
    purchase_link = request.form['purchase_link']

    # Connect to the database
    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()

    # Check if the selected product is already in the user's favorites
    cursor.execute('''
        SELECT id FROM favorites 
        WHERE user_id = ? AND product_name = ? AND brand_name = ?
    ''', (current_user.id, product_name, brand_name))
    existing = cursor.fetchone()

    # Add to favorites if not already added
    if not existing:
        cursor.execute('''
            INSERT INTO favorites (user_id, product_name, brand_name, category, image_url, purchase_link)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (current_user.id, product_name, brand_name, category, image_url, purchase_link))
        conn.commit()
        flash('Added to Wishlist! 💖', 'success')

    conn.close()

    # Return to browse products
    return redirect(request.referrer or url_for('browse_products'))
# End of add_favorite()

"""
NAME
    remove_favorite - removes a product from the user's wishlist

SYNOPSIS
    remove_favorite()

DESCRIPTION
    Deletes a selected product from the current user's favorites list based on the product
    name and brand. Triggered by a POST request.

RETURNS
    Redirects back to the referring page.
"""
@app.route('/remove_favorite', methods=['POST'])
@login_required
def remove_favorite():
    # Get product details from the form
    product_name = request.form['product_name']
    brand_name = request.form['brand_name']

    # Connect and remove the product from the favorites table
    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM favorites
        WHERE user_id = ? AND product_name = ? AND brand_name = ?
    ''', (current_user.id, product_name, brand_name))
    conn.commit()
    conn.close()

    flash('Removed from Wishlist ❤️‍🔥', 'danger')

    # Notify and redirect
    return redirect(request.referrer or url_for('browse_products'))
# End of remove_favorite()

"""
NAME
    wishlist - displays the current user's saved products (Loves list)

SYNOPSIS
    wishlist()

DESCRIPTION
    Retrieves all favorite products saved by the logged-in user. Optionally filters
    the results by selected filters (e.g., category or price).

RETURNS
    Renders the 'wishlist.html' page with the filtered or full list of favorites.
"""
@app.route('/wishlist')
def wishlist():
    # Require login to access wishlist
    if not current_user.is_authenticated:
        flash('You must sign in to view your Loves list!')
        return redirect(url_for('login'))

    # Connect to DB and fetch all favorites for the user
    conn = sqlite3.connect('beauty_products.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT product_name, brand_name, category, image_url, purchase_link
        FROM favorites
        WHERE user_id = ?
    ''', (current_user.id,))
    all_favorites = cursor.fetchall()

    # Apply filters if specified
    selected_filters = request.args.getlist('filters')

    # Include only if it matches category or price filter
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

    # Render wishlist page with favorites and filters
    return render_template('wishlist.html',
        favorites=favorites,
        selected_filters=selected_filters
    )
# End of wishlist()

"""
NAME
    my_account - displays user's account information, quiz history, and wishlist

SYNOPSIS
    my_account()

DESCRIPTION
    Shows profile info, last quiz results, matched skin concern data, and favorited items
    for the logged-in user.

RETURNS
    Renders 'my_account.html' with all relevant user data.
"""
@app.route('/my_account')
@login_required
def my_account():
    # Connect to DB and retrieve user's profile information
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

    # Prepare detailed skin concern descriptions based on stored result
    skin_concerns = {}
    if quiz_data and quiz_data[3]:
        concerns_list = quiz_data[3].split(',')
        for concern in concerns_list:
            concern = concern.strip()
            if concern in SKIN_CONCERN_INFO:
                skin_concerns[concern] = SKIN_CONCERN_INFO[concern]

    # Retrieve favorited products for the account page
    cursor.execute('''
        SELECT product_name, brand_name, category, image_url, purchase_link
        FROM favorites
        WHERE user_id = ?
    ''', (current_user.id,))
    favorites = cursor.fetchall()

    conn.close()

    # Render the My Account page with all data passed to the template
    return render_template('my_account.html',
        user_info=user_info,
        quiz_data=quiz_data,
        skin_concerns=skin_concerns,
        favorites=favorites
    )
# End of my_account()

"""
NAME
    reset_password - allows the user to change their password

SYNOPSIS
    reset_password()

DESCRIPTION
    Displays a form to reset password. If current password matches what's stored,
    replaces it with the new hashed password.

RETURNS
    Redirects to 'my_account' on success or reloads form with error.
"""
@app.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    # Get input from the reset form
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
            # If current password is correct, update to new password
            new_hashed_pw = generate_password_hash(new_password)

            cursor.execute('''
                UPDATE users
                SET password = ?
                WHERE id = ?
            ''', (new_hashed_pw, current_user.id))
            conn.commit()
            conn.close()

            flash('Password updated successfully!', 'success')
            return redirect(url_for('my_account'))
        else:
            conn.close()
            # Show error message if password check fails
            flash('Current password is incorrect. Please try again.', 'danger')
            return redirect(url_for('reset_password'))
    # Render the password reset form
    return render_template('reset_password.html')
# End of reset_password()

"""
NAME
    beauty_tips - displays general beauty tips page

SYNOPSIS
    beauty_tips()

DESCRIPTION
    Static route for rendering general beauty tips or advice to users.

RETURNS
    Renders the 'beauty_tips.html' template.
"""
@app.route('/beauty_tips')
def beauty_tips():
    # Render the beauty tips static page
    return render_template('beauty_tips.html')
# End of beauty_tips()

if __name__ == '__main__':
    app.run(debug=True)


