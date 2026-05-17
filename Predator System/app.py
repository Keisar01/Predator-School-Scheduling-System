from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import time

app = Flask(__name__)
app.secret_key = "school_secret"
DB_NAME = "school_schedule.db"
MAX_LOGIN_ATTEMPTS = 3
LOCK_DURATION_SECONDS = 30


# =====================================
# DATABASE CONNECTION
# =====================================
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_status(raw_status):
    status_map = {
        "ongoing": "Ongoing",
        "delayed": "Delayed",
        "cancelled": "Cancelled",
        "done": "Done",
        "completed": "Done"
    }
    return status_map.get((raw_status or "").strip().lower())


# =====================================
# CREATE TABLES
# =====================================
def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    # USERS TABLE
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')

    # EVENTS TABLE
    cur.execute('''
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_name TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL,
            location TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()
    conn.close()


# =====================================
# LOGIN PAGE
# =====================================
@app.route('/')
def login_page():
    lockout_until = session.get('lockout_until', 0)
    now = time.time()
    remaining_lock_seconds = 0

    if lockout_until > now:
        remaining_lock_seconds = int(lockout_until - now)
    else:
        session.pop('lockout_until', None)

    return render_template('login.html', remaining_lock_seconds=remaining_lock_seconds)


# =====================================
# REGISTER PAGE
# =====================================
@app.route('/register')
def register_page():
    return render_template('register.html')


# =====================================
# DASHBOARD (USER / REDIRECT ADMIN)
# =====================================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    role = session.get('role')

    if role == 'superadmin':
        return redirect(url_for('superadmin_dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin_dashboard'))
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM events
        WHERE user_id = ?
        ORDER BY date ASC, time ASC
    """, (session['user_id'],))
    events = cur.fetchall()
    conn.close()

    return render_template('dashboard.html', events=events)


# =====================================
# REGISTER
# =====================================
@app.route('/api/register', methods=['POST'])
def register():
    username = request.form['username'].strip()
    name = request.form['name'].strip()
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if not username or not name or not password or not confirm_password:
        flash("All registration fields are required")
        return redirect(url_for('register_page'))

    if password != confirm_password:
        flash("Passwords do not match")
        return redirect(url_for('register_page'))

    conn = connect_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (username, name, password) VALUES (?, ?, ?)",
            (username, name, password)
        )
        conn.commit()
        flash("Registration successful")
        return redirect(url_for('login_page'))

    except sqlite3.IntegrityError:
        flash("Username already exists")
        return redirect(url_for('register_page'))

    finally:
        conn.close()


# =====================================
# LOGIN
# =====================================
@app.route('/api/login', methods=['POST'])
def login():
    username = request.form['username'].strip()
    password = request.form['password']
    current_time = time.time()
    lockout_until = session.get('lockout_until', 0)

    if lockout_until > current_time:
        remaining = int(lockout_until - current_time)
        flash(f"Too many attempts. Try again in {remaining} seconds")
        return redirect(url_for('login_page'))

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cur.fetchone()
    conn.close()

    if user:
        session.pop('failed_attempts', None)
        session.pop('lockout_until', None)
        session['user_id'] = user['user_id']
        session['name'] = user['name']
        session['role'] = user['role']
        return redirect(url_for('dashboard'))
    else:
        failed_attempts = session.get('failed_attempts', 0) + 1
        if failed_attempts >= MAX_LOGIN_ATTEMPTS:
            session['failed_attempts'] = 0
            session['lockout_until'] = current_time + LOCK_DURATION_SECONDS
            flash("Cannot login now. Wait 30 seconds then try again")
        else:
            session['failed_attempts'] = failed_attempts
            remaining = MAX_LOGIN_ATTEMPTS - failed_attempts
            flash(f"Invalid username or password. {remaining} attempt(s) left")
        return redirect(url_for('login_page'))


# =====================================
# CREATE EVENT
# =====================================
@app.route('/api/create_event', methods=['POST'])
def create_event():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    event_name = request.form['event_name'].strip()
    description = request.form.get('description', '').strip()
    date = request.form['date'].strip()
    time_value = request.form['time'].strip()
    status = normalize_status(request.form['status'])
    location = request.form['location'].strip()

    if not event_name or not date or not time_value or not status or not location:
        flash("Please complete all required event fields")
        return redirect(url_for('dashboard'))

    conn = connect_db()
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO events (user_id, event_name, description, date, time, status, location)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        session['user_id'],
        event_name,
        description,
        date,
        time_value,
        status,
        location
    ))

    conn.commit()
    conn.close()

    flash("Event created successfully")
    return redirect(url_for('dashboard'))


# =====================================
# VIEW EVENTS (USER)
# =====================================
@app.route('/api/view_events')
def view_events():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM events")

    events = cur.fetchall()
    conn.close()

    return render_template('view_events.html', events=events)

@app.route('/api/update_event/<int:event_id>', methods=['POST'])
def update_event(event_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE events
        SET event_name=?, description=?, date=?, time=?, status=?, location=?
        WHERE event_id=?
    """, (
        request.form['event_name'],
        request.form['description'],
        request.form['date'],
        request.form['time'],
        request.form['status'],
        request.form['location'],
        event_id
    ))

    conn.commit()
    conn.close()

    flash("Event updated successfully")
    return redirect(url_for('view_events'))

@app.route('/update_event/<int:event_id>')
def user_update_event_page(event_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
    event = cur.fetchone()

    conn.close()

    if not event:
        flash("Event not found")
        return redirect(url_for('view_events'))

    return render_template('user_update_event.html', event=event)

# UPDATE EVENT (USER ONLY THEIR OWN)
@app.route('/api/user_update_event/<int:event_id>', methods=['POST'])
def user_update_event(event_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    conn = connect_db()
    cur = conn.cursor()

    # check ownership
    cur.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
    event = cur.fetchone()

    if not event:
        conn.close()
        flash("Event not found")
        return redirect(url_for('view_events'))

    if event["user_id"] != session["user_id"]:
        conn.close()
        flash("Not allowed")
        return redirect(url_for('view_events'))

    new_date = request.form['date'].strip()
    new_time = request.form['time'].strip()
    new_location = request.form['location'].strip()

    if not new_date or not new_time or not new_location:
        conn.close()
        flash("Date, time, and location are required")
        return redirect(url_for('view_events'))

    # auto status logic
    cur.execute("""
        UPDATE events
        SET date = ?, time = ?, location = ?,
            status = CASE
                WHEN date < ? THEN 'delayed'
                ELSE status
            END
        WHERE event_id = ?
    """, (new_date, new_time, new_location, new_date, event_id))

    conn.commit()
    conn.close()

    flash("Event updated")
    return redirect(url_for('view_events'))

# =====================================
# ADMIN DASHBOARD
# =====================================
@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login_page'))

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM events")
    events = cur.fetchall()

    cur.execute("SELECT username, name, role FROM users")
    users = cur.fetchall()

    conn.close()

    return render_template('admin_dashboard.html', events=events, users=users)

@app.route('/admin/update_event/<int:event_id>')
def admin_update_event_page(event_id):
    if session.get('role') not in ['admin', 'superadmin']:
        return redirect(url_for('login_page'))

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
    event = cur.fetchone()

    conn.close()

    if not event:
        flash("Event not found")
        return redirect(url_for('superadmin_dashboard'))

    return render_template('admin_update_event.html', event=event)

# ADMIN / SUPERADMIN UPDATE ANY EVENT
@app.route('/api/admin_update_event/<int:event_id>', methods=['POST'])
def admin_update_event(event_id):
    if session.get('role') not in ['admin', 'superadmin']:
        return redirect(url_for('login_page'))

    conn = connect_db()
    cur = conn.cursor()

    event_name = request.form['event_name'].strip()
    description = request.form.get('description', '').strip()
    date = request.form['date'].strip()
    time_value = request.form['time'].strip()
    status = normalize_status(request.form['status'])
    location = request.form['location'].strip()

    if not event_name or not date or not time_value or not status or not location:
        conn.close()
        flash("Please complete all required fields with valid status")
        return redirect(url_for('admin_update_event_page', event_id=event_id))

    cur.execute("""
        UPDATE events
        SET event_name = ?, description = ?, date = ?, time = ?, status = ?, location = ?
        WHERE event_id = ?
    """, (event_name, description, date, time_value, status, location, event_id))

    conn.commit()
    conn.close()

    flash("Event updated by admin")
    if session.get('role') == 'superadmin':
        return redirect(url_for('superadmin_dashboard'))
    return redirect(url_for('admin_dashboard'))

# =====================================
# MAKE ADMIN (SUPER ADMIN ONLY)
# =====================================
@app.route('/superadmin')
def superadmin_dashboard():
    if session.get('role') != 'superadmin':
        return redirect(url_for('login_page'))

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    cur.execute("SELECT * FROM events")
    events = cur.fetchall()

    conn.close()

    return render_template('superadmin_dashboard.html', users=users, events=events)

@app.route('/create_admin', methods=['POST'])
def create_admin():
    if session.get('role') != 'superadmin':
        return redirect(url_for('login_page'))

    username = request.form['username']
    name = request.form['name']
    password = request.form['password']

    conn = connect_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO users (username, name, password, role)
            VALUES (?, ?, ?, 'admin')
        """, (username, name, password))

        conn.commit()
        flash("New admin created successfully")

    except sqlite3.IntegrityError:
        flash("Username already exists")

    finally:
        conn.close()

    return redirect(url_for('superadmin_dashboard'))


@app.route('/make_admin/<int:user_id>')
def make_admin(user_id):
    if session.get('role') != 'superadmin':
        return redirect(url_for('login_page'))

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("UPDATE users SET role = 'admin' WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()

    flash("User promoted to admin")
    return redirect(url_for('superadmin_dashboard')) 


# =====================================
# DELETE USER (SUPER ADMIN ONLY)
# =====================================
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get('role') != 'superadmin':
        return redirect(url_for('login_page'))

    conn = connect_db()
    cur = conn.cursor()

    #  GET THE USER FIRST
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_to_delete = cur.fetchone()

    #  PROTECTION CHECK (PUT IT HERE)
    if user_to_delete and user_to_delete["role"] == 'superadmin':
        flash("Cannot delete superadmin")
        conn.close()
        return redirect(url_for('superadmin_dashboard'))

    #  DELETE IF NOT SUPERADMIN
    cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()

    flash("User deleted")
    return redirect(url_for('superadmin_dashboard'))

# =====================================
# DELETE EVENT (ADMIN / SUPER ADMIN)
# =====================================
@app.route('/api/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
    event = cur.fetchone()

    if not event:
        conn.close()
        flash("Event not found")
        return redirect(url_for('dashboard'))

    role = session.get('role')
    is_owner = event["user_id"] == session.get("user_id")
    is_privileged = role in ['admin', 'superadmin']

    if not (is_owner or is_privileged):
        conn.close()
        flash("Not allowed")
        return redirect(url_for('dashboard'))

    cur.execute("DELETE FROM events WHERE event_id = ?", (event_id,))

    conn.commit()
    conn.close()

    flash("Event deleted successfully")
    if role == 'superadmin':
        return redirect(url_for('superadmin_dashboard'))
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('dashboard'))

@app.route('/fix_superadmin')
def fix_superadmin():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO users (user_id, username, name, password, role)
        VALUES (1, 'superadmin', 'Super Admin', '1234', 'superadmin')
    """)

    conn.commit()
    conn.close()

    return "Superadmin restored"


# =====================================
# LOGOUT
# =====================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))


# =====================================
# RUN APP
# =====================================
if __name__ == '__main__':
    create_tables()
    fix_superadmin()
    app.run(debug=True)