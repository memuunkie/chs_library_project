from jinja2 import StrictUndefined

from flask import jsonify
from flask import (Flask, render_template, redirect, request, flash,
                   session, url_for)

from flask_debugtoolbar import DebugToolbarExtension

from sqlalchemy import and_, or_

from model import Book, User, Visit, VisitItem
from model import connect_to_db, db

from datetime import datetime

from json import dumps, loads


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABCItseasyas123orsimpleasDo-Re-MiABC123babyyouandmegirl"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Home"""
    return render_template("home.html")


@app.route('/library')
def library_view():
    """render the librarian view"""

    return render_template('library_view.html')


@app.route('/add-visit', methods=['GET'])
def visit_form():
    """Show visit form"""

    return render_template('visit_results.html')


@app.route('/add-visit', methods=['POST'])
def add_visit():
    """Add a Visit to the database"""

    print "Got to the POST"

    user = request.form.get('user-id')
    admin = request.form.get('admin-id')
    
    visit = Visit(user_id=user, admin_id=admin, 
                  visit_timein=datetime.now())

    db.session.add(visit)
    db.session.commit()

    return redirect('/visit')


@app.route('/visit')
def show_visits():
    """Lisit of all visitors"""

    today = datetime.now()

    visits = Visit.query.all()

    return render_template('visit_results.html', visits=visits)


@app.route('/visit/<int:visit_id>', methods=['GET'])
def show_visit(visit_id):
    """Show the visit details"""

    visit_items = VisitItem.query.filter_by(visit_id=visit_id).all()
    visit_deets = Visit.query.filter_by(visit_id=visit_id).one()

    return render_template('visit_detail.html', visit_deets=visit_deets,
                            visit_items=visit_items)


@app.route('/visit/<int:visit_id>', methods=['POST'])
def add_items(visit_id):
    """Add a book to a visit"""

    book_id = int(request.form['book-id'])

    book = VisitItem.query.filter_by(book_id=book_id).first()

    if book:
        flash("Book already in use.")
    else:
        visit_item = VisitItem(visit_id=visit_id, book_id=book_id,
                               checkout_time=datetime.now())
        flash("Book added.")
        db.session.add(visit_item)

    db.session.commit()

    return redirect('/visit/%s' % visit_id)

@app.route('/search-books', methods=['GET'])
def find_book():
    """Do a search on books and return a list of matches"""

    title = get_return_wildcard('title')
    author = get_return_wildcard('author')
    call_num = get_return_wildcard('call-num')

    books = Book.query.filter(or_(Book.title.ilike(title), 
                                 Book.author.ilike(author),
                                 Book.call_num.ilike(call_num))).all()

    return render_template('book_results.html', books=books)


@app.route('/search-users', methods=['GET'])
def search_users():
    """Do a search of user and return a list of possible matches"""

    email = get_return_wildcard('email')
    fname = get_return_wildcard('fname')
    lname = get_return_wildcard('lname')

    users = User.query.filter(or_(User.email.ilike(email), 
                                    User.fname.ilike(fname), 
                                    User.lname.ilike(lname))).all()

    return render_template('user_results.html', users=users)


@app.route('/find-users.json', methods=['GET'])
def find_user():
    """Do a search of user and return a list of possible matches"""

    email = get_return_wildcard('email')
    fname = get_return_wildcard('fname')
    lname = get_return_wildcard('lname')

    users = User.query.filter(or_(User.email.ilike(email), 
                                    User.fname.ilike(fname), 
                                    User.lname.ilike(lname))).all()

    users = [u.serialize() for u in users]

    return jsonify(users)


@app.route('/new-visit.json', methods=['POST'])
def add_new_visit():
    """Add a Visit to the database"""

    print "Adding via AJAX"

    user = request.form.get('user-id')

    print user

    return "Success to post"


@app.route('/display-visitors')
def display_visitors():
    """List of current visitors"""

    visits = Visit.query.all()

    all_visits = []

    for visit in visits:
        x = visit.user.serialize()
        x.update(visit.serialize())
        all_visits.append(x)

    print jsonify(all_visits)
    return jsonify(all_visits)


#################################################################
#Helper functions

def make_wildcard(name):
    """Formats request.args result to be wildcard-able"""

    return '%' + name + '%'


def get_return_wildcard(name):
    """Checks to see if there is a request.args and returns string"""

    if request.args.get(name):
        return make_wildcard(request.args.get(name))
    else:
        return ''

    return


def post_return_wildcard(name):
    """Checks to see if there is a request.form and returns string"""

    if request.form.get(name):
        return make_wildcard(request.form.get(name))
    else:
        return ''


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)



    app.run(port=5000, host='0.0.0.0')