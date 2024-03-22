from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = "krabbypattysecretformula"

def createDBConnection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def closeDBConnection(exception=None):
    conn = sqlite3.connection.pop()
    if conn is not None:
        conn.close()


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/generator', methods=['GET'])
def generatePassword():
    return render_template('passwordgenerator.html')

@app.route('/add-password', methods=['POST'])
def addPassword():
    # Extracting the password entry elements from HTML
    entryTitle = request.form['title']
    entryUsername = request.form['username']
    entryPassword = request.form['password']
    entryDescription = request.form['description']
    # Avoid adding password entry if it has an empty username or password
    if len(entryUsername) == 0 or len(entryPassword) == 0:
        print("Possible empty password entry. Ignoring")
        return redirect(url_for('dashboard'))
    else:
        print("Adding password entry...")
        userID = session['id'] # Extract user ID from session
        # Insert password entry into database
        conn = createDBConnection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO passwordEntries (user_id, title, username, password, description) VALUES (?, ?, ?, ?, ?)', (userID, entryTitle, entryUsername, entryPassword, entryDescription))
        conn.commit()
        conn.close()
        # Return with succeess message
        #return render_template('vault.html', success_message='Password entry added!', username=entryUsername, email=session['email'])
        return redirect(url_for('dashboard')) # No success message, we just refresh the page essentially

# For some reason, when deleting password entries, it adds a blank/empty one, so may want to remove/disable this feature for now
@app.route('/delete-password', methods=['POST'])
def deletePassword():
    try:
        entryID = int(request.form['entryID'])
        print('Attempting to delete {0}'.format(entryID))
        conn = createDBConnection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM passwordEntries WHERE id=?', (entryID,))
    
        conn.commit()
        conn.close()
    
        return redirect(url_for('dashboard'))
    except Exception as e:
        print("Error encountered while deleting password entry ID {0}".format(entryID))
        return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    # Technically if a user changes their username in the session storage of the browser, they would be able to retrieve the email of any user registered
    if 'username' in session:
        username = session['username']
        conn = createDBConnection()
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user:
            email = user['email']
            #return render_template('vault.html', username=username, email=email) # Render the dashboard template with the user's username and email

        # Retrieving stored passwords
        cursor.execute('SELECT title, username, password, description, id FROM passwordEntries WHERE user_id=?', (session['id'],))
        passEntries = cursor.fetchall()
        conn.close()
        print('rendering template...')
        return render_template('vault.html', username=username, email=email, passEntries=passEntries) # pass the username & email to render on template

    
    else:
        #return redirect(url_for('login'))
        return render_template('login.html')
    return render_template('login.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = createDBConnection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()
        # User entered correct credentials
        if user:
            # We assign the user ID & username to the user's session
            session['id'] = user[0]
            session['username'] = username # We assign the username to the user's session cookie
            session['email'] = user[1] # Not 100% sure if the 1 index is the user's email address, ngl
            return redirect(url_for('dashboard')) # Redirect to dashboard if the user authenticates successfully
        # Credentials were incorrect
        else:
            return render_template('login.html', error_message='Username or password incorrect! Try again!')
    else:
        if request.method == 'GET':
            # Check if user is authenticated
            if 'username' in session:
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html')
@app.route("/profile", methods=['GET'])
def profile():
    if request.method == 'GET':
        #return render_template('profile.html', username=session['username'], email=session['email'])
        return render_template('profile.html', user=session)
        #return render_template('profile.html')


@app.route("/settings", methods=['GET'])
def settings():
    if request.method == 'GET':
        return render_template('settings.html')

@app.route("/register", methods=['GET', 'POST'])
# Function isn't properly registering users & inserting them into sqlite3 database for some reason.
def register():
    if request.method == 'POST':
        print("request is posting data")
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        conn = createDBConnection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
        existingUser = cursor.fetchone() # Check for any existing users

        # User already exists in database
        if existingUser:
            print('[!] User already exists!')
            conn.close()
            return render_template('register.html', error_message='Username or email address already exists!')
        # User doesn't exist, create it
        else:
            print('[+] Creating user with following info: {0}:{1}:{2}'.format(username, email, password))
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
            conn.commit()
            conn.close()
            print('[+] Created user!')
            return render_template('register.html', success_message='Successfully registered! You may now login. Redirecting...'), {'Refresh':'1; url=/login'}
    else:
        return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    conn = createDBConnection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )''')

    # Create the passwordEntries table
    cursor.execute('''CREATE TABLE IF NOT EXISTS passwordEntries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    description TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )''')
    conn.commit()
    conn.close()

    app.run(debug=True)
