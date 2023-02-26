import os
from functools import wraps
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import re
import random
from queries import (INSERT_NEW_USER, SELECT_CURRENT_USER, GET_READING_LIST, GET_HAVEREAD_LIST,
    GET_CURRENT_LIST, ADDTO_READING_LIST, SEARCH_DB, DEL_FROM_RL, GET_RL_BOOKID, GET_CLIST,
    DEL_FROM_CL, HAVE_READ, FIND_BOOK, GET_REVIEWS, BOOKS_BY_AUTHOR, FIND_AUTHOR, MY_REVIEWS,
    GET_TITLE, TOP_25, GET_HAVEREAD_NOLIMIT, ADD_REVIEW, LATEST_REVIEWS, GET_USERNAME, ADDTO_CLIST,
    TOP_5, NEWEST_REVIEW, INCREMENT_REVIEWS, INCREMENT_RATINGS, SELECT_SIMILAR, ADD_BOOK, NEW_BOOK,
    PICK_QUOTE, REVIEW_AND_RATING, THIS_REVIEW, NEW_AVERAGE)

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///leggi.db")

# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def after_request(response):
    # Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    if session.get("user_id"):
        return redirect("/home")
    else:
        num = random.randint(1, 14)
        quote = db.execute(PICK_QUOTE, num)
        return render_template("index.html", quote=quote[0])

@app.route("/register", methods=['POST', 'GET'])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # check for reqistration errors
        usernames = db.execute("SELECT username FROM users")
        users = []
        for row in usernames:
            users.append(row["username"])
        if len(password) < 8:
            error = "Password must be at least 8 characters long"
        elif username in users:
            error = "That username is already taken"
        elif confirmation != password:
            error = "Passwords must match"
        else:
            # generate password hash
            hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            # remember registrant
            db.execute(INSERT_NEW_USER, username, hash)
            #redirect to login page
            flash('Successful registration')
            return redirect("/login")
        return render_template("register.html", error=error)
    else:
        return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    session.clear()
    error = None
    if request.method == "POST":
        # check for login errors
        if not request.form.get("username"):
            error = "Must provide username"
            return render_template("login.html", error=error)
        if not request.form.get("password"):
            error = "Must enter password"
            return render_template("login.html", error=error)

        rows = db.execute(SELECT_CURRENT_USER, request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            error = "Invalid credentials"
            return render_template("login.html", error=error)

        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        return redirect("/home")

    else:
        return render_template("login.html")


@app.route("/home")
@login_required
def home():
    reading_list = db.execute(GET_READING_LIST, session.get("user_id"))
    read_list = db.execute(GET_HAVEREAD_LIST, session.get("user_id"))
    current_list = db.execute(GET_CURRENT_LIST, session.get("user_id"))
    new_review = db.execute(NEWEST_REVIEW)
    for row in new_review:
        row["time"] = row["time"][:10]
        user = db.execute(GET_USERNAME, row["user_id"])
        row["username"] = user[0]["username"]
    top = db.execute(TOP_5)
    num = random.randint(1, 14)
    quote = db.execute(PICK_QUOTE, num)
    # books = db.execute("SELECT title FROM books")
    return render_template("home.html", name = session.get("username"), quote=quote[0], list=reading_list, rlist=read_list, clist=current_list, new_review=new_review, top=top)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/addtolist/<int:id>", methods=["GET", "POST"])
@login_required
def addtolist(id):
    db.execute(ADDTO_READING_LIST, session.get("user_id"), id)
    return redirect("/mybooks")


@app.route("/search", methods=["POST", "GET"])
@login_required
def search():
    if request.method == "POST":
        search = request.form.get("search")
        results = db.execute(SEARCH_DB, rf"%{search}%", rf"%{search}%")
        return render_template("search.html", results=results)
    else:
        return render_template("searchpage.html")


@app.route("/delete/<int:id>")
@login_required
def delete(id):
    db.execute(DEL_FROM_RL, session.get("user_id"), id)
    return redirect("/mybooks")


@app.route("/haveread/<int:id>")
@login_required
def haveread(id):
    to_read = db.execute(GET_RL_BOOKID, session.get("user_id"))
    for book in to_read:
        if id == book["book_id"]:
            db.execute(DEL_FROM_RL, session.get("user_id"), id)
    current_list = db.execute(GET_CLIST, session.get("user_id"))
    for book in current_list:
        if id == book["book_id"]:
            db.execute(DEL_FROM_CL, session.get("user_id"), id)
    db.execute(HAVE_READ, session.get("user_id"), id)
    return redirect("/mybooks")


@app.route("/open_book/<int:id>")
@login_required
def open_book(id):
    book = db.execute(FIND_BOOK, id)
    reviews = db.execute(GET_REVIEWS, id)
    for review in reviews:
        user = db.execute(GET_USERNAME, review["user_id"])
        review["username"] = user[0]["username"]
        review["time"] = review["time"][:10]
    more = db.execute(BOOKS_BY_AUTHOR, book[0]["author"])
    return render_template("book.html", book=book, reviews=reviews, more=more)


@app.route("/search_author/<int:id>")
@login_required
def search_author(id):
    author = db.execute(FIND_AUTHOR, id)
    books = db.execute(BOOKS_BY_AUTHOR, author[0]["author"])
    return render_template("author.html", author=author[0]["author"], books=books)


@app.route("/myreviews")
@login_required
def myreviews():
    reviews = db.execute(MY_REVIEWS, session.get("user_id"))
    for row in reviews:
        author =  db.execute(FIND_AUTHOR, row["book_id"])
        row["book_author"] = author[0]["author"]
        title = db.execute(GET_TITLE, row["book_id"])
        row["book_title"] = title[0]["title"]
        row["time"] = row["time"][:10]
    return render_template("myreviews.html", reviews=reviews)

@app.route("/top")
@login_required
def top():
    toplist = db.execute(TOP_25)
    return render_template("toprated.html", top=toplist)

@app.route("/mybooks")
@login_required
def mybooks():
    list = db.execute(GET_READING_LIST, session.get("user_id"))
    read = db.execute(GET_HAVEREAD_NOLIMIT, session.get("user_id"))
    for row in read:
        row["time"] = row["time"][:10]
    clist = db.execute(GET_CURRENT_LIST, session.get("user_id"))

    return render_template("mybooks.html", list=list, read=read, clist=clist)


@app.route("/reviews", methods=["POST", "GET"])
@login_required
def reviews():
    error = None
    if request.method == "POST":
        content = request.form.get("content")
        bookid = request.form.get("bookid")
        rating = request.form.get("rating")
        if rating:
            rating = float(rating)
        else:
            rating = None
        if not content:
            error = "Review content must be provided"
            return redirect(url_for("open_book", id=int(bookid),  error=error))
        if request.form.get("spoiler"):
            spoiler = 1
        else:
            spoiler = 0
        if rating == 0:
            db.execute(ADD_REVIEW, content, spoiler, bookid, session.get("user_id"))
        else:
            db.execute(REVIEW_AND_RATING, content, rating, spoiler, bookid, session.get("user_id"))
            # getid = db.execute(THIS_REVIEW)
            # review_id = getid[0]["id"]
            db.execute(NEW_AVERAGE, rating, bookid)
            db.execute(INCREMENT_RATINGS, bookid)
        db.execute(INCREMENT_REVIEWS, bookid)
        return redirect(url_for("open_book", id=int(bookid)))
    else:
        latest = db.execute(LATEST_REVIEWS)
        for row in latest:
            user = db.execute(GET_USERNAME, row["user_id"])
            row["author"] = user[0]["username"]
            author =  db.execute(FIND_AUTHOR, row["book_id"])
            row["book_author"] = author[0]["author"]
            title = db.execute(GET_TITLE, row["book_id"])
            row["book_title"] = title[0]["title"]
            row["time"] = row["time"][:10]
        return render_template("reviews.html", latest=latest)


@app.route("/currently_reading/<int:id>")
@login_required
def current(id):
    current_list = db.execute(GET_CLIST, session.get("user_id"))
    if current_list == None:
        db.execute(ADDTO_CLIST, session.get("user_id"), id)
    else:
        for l in current_list:
            if id == l["book_id"]:
                return redirect("/home")
        db.execute(ADDTO_CLIST, session.get("user_id"), id)
        db.execute(DEL_FROM_RL, session.get("user_id"), id)
    return redirect("/mybooks")


@app.route("/deletefromc/<int:id>")
@login_required
def deletefromc(id):
    db.execute(DEL_FROM_CL, session.get("user_id"), id)
    return redirect("/mybooks")


@app.route("/user/<int:id>")
@login_required
def user(id):
    if id == session.get("user_id"):
        return redirect("/home")
    else:
        reviews = db.execute(MY_REVIEWS, id)
        for row in reviews:
            author= db.execute(FIND_AUTHOR, row["book_id"])
            row["book_author"] = author[0]["author"]
            title = db.execute(GET_TITLE, row["book_id"])
            row["book_title"] = title[0]["title"]
            row["time"] = row["time"][:10]
        username = db.execute(GET_USERNAME, id)
        thisuser = db.execute(SELECT_CURRENT_USER, username[0]["username"])
        for row in thisuser:
            row["registration_time"] = row["registration_time"][:10]
        clist = db.execute(GET_CURRENT_LIST, id)
        read = db.execute(GET_HAVEREAD_NOLIMIT, id)
        return render_template("user.html", reviews=reviews, user=thisuser, clist=clist, read=read)


@app.route("/add_book", methods=["POST", "GET"])
@login_required
def add_book():
    error = None
    if request.method == "POST":
        if not request.form.get("author") or not request.form.get("title"):
            error = "Missing author or title"
            return render_template("addbook.html", error=error)
        author = request.form.get("author")
        author = author.title()
        title = request.form.get("title")
        title = title.title()
        similar = db.execute(SELECT_SIMILAR, title)
        if len(similar) > 0:
            for s in range(len(similar)):
                if similar[s]["author"] == author:
                    error = "This book exists in the database already. Try searching for the author or title."
                    return render_template("addbook.html", error=error)
        db.execute(ADD_BOOK, author, title)
        new = db.execute(NEW_BOOK, author, title)
        new_id = new[0]["id"]
        return redirect("/open_book/{}".format(new_id))
    else:
        return render_template("addbook.html")
