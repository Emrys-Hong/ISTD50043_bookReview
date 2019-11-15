from flask import send_from_directory,url_for, redirect, Flask, render_template, request, session
from flask_session import Session
import SQLservice
import SQLservice_User
import mongoService
import numpy as np
import pandas as pd
import string
import json

app = Flask(__name__)
app.config['DEBUG'] = True

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

mg = mongoService.Mg()

with open('categories.json') as f:
    data = json.load(f)
#############yy edits#################################
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)
@app.route('/font-awesome-4.7.0/<path:path>')
def send_node(path):
    return send_from_directory('font-awesome-4.7.0', path)
@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('img', path)
###################################################
@app.route("/home_page")
def home_page():
    cats = ["Mystery, Thriller & Suspense","Science Fiction & Fantasy","Action & Adventure","Love & Romance","Business & Money"
,"Health, Fitness & Dieting","Professional & Technical","Administration & Policy","Dictionaries & Thesauruses","Biographies & Memoirs"]

    book_list = mongoService.Mg().get_bestsellers()

    cat_book_list = []
    for cat in cats:
        top_in_cat = mongoService.Mg().get_highest_rank_books(cat)
        cat_book_list.append(top_in_cat)
    #mg.insert_query
    print("\n\n\n\n")
    print(book_list[0])
    return render_template("home_page.html",results=book_list[:-3], catbook_list = cat_book_list)


#############################################

@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/bookinfo")
def book_list():
    return str(mg.get_all())


@app.route("/bookinfo/<page_num>/<category>")
def book_list_page(page_num, category):
    if 'user' not in session:
        return redirect(url_for('login'))
    page_num = int(page_num)
    book_list = mongoService.Mg().get_all_books(page_num, category)
    page_numbers = list(range(1, 4000))
    mg.insert_query({'results': book_list, 'page_numbers': page_numbers, 'categories': data})
    return render_template("booklist.html", results=book_list, page_numbers=page_numbers, categories=data)


@app.route("/book/<asin>", methods=["GET", "POST"])
def info(asin):
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        comment = request.form.get("comment")
        my_rating = request.form.get("rating")
        SQLservice.SQL_db().add_review(asin=asin, overall=my_rating, reviewerName=session['user'], summary=comment)

    book_info = mongoService.Mg().get_all_info(asin)[0]
    results = SQLservice.SQL_db().get_review(asin)
    rating = np.mean([review[2] for review in results])
    mg.insert_query({'book_info': book_info, 'reviews': results, 'rating': rating})
    return render_template("info.html", book_info=book_info, reviews=results, rating=rating)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))

    message = None

    if request.method == "POST":
        usern = request.form.get("username")
        passw = request.form.get("password").encode('utf-8')
        verify_passw = SQLservice_User.SQL_User_db().get_password(usern).encode('utf-8')
        print(passw, verify_passw, type(verify_passw))
        if passw == verify_passw:
            session['user'] = usern
            return redirect(url_for('dashboard'))
        else:
            message = "Username or password is incorrect."
    return render_template("login.html", message=message)


@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if 'user' in session:
        return redirect(url_for('dashboard'))

    message = None

    if request.method == "POST":
        usern = request.form.get("username")
        passw = request.form.get("password")
        result = SQLservice_User.SQL_User_db().add_user(usern, passw)
        # TODO: save HASH(pwd) instead of pwd in database

        if result:
            session['user'] = usern
            return redirect(url_for('dashboard'))
        # TODO: Save reviewerID in session so that can be added to review DB
        else:
            message = "Username already exists."

    return render_template("registration.html", message=message)


@app.route("/search", methods=["POST"])
def search():
    if 'user' not in session:
        return redirect(url_for('login'))
    keyword = request.form.get("searchbox")
    keyword = ''.join([o for o in keyword if o not in string.punctuation])
    results = mg.search_book(keyword)
    return render_template("search.html", results=results)


@app.route("/addbook", methods=['POST', 'GET'])
def addBook():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Submit':
            asin = request.form['field1']
            title = request.form['field2']
            brand = request.form['field3']
            price = float(request.form['field4'])
            url = request.form['field5']
            alsoBought = request.form['field6'].strip().split(" ")
            alsoViewed = request.form['field7'].strip().split(" ")
            buyAfterViewing = request.form['field8'].strip().split(" ")
            boughtTogether = request.form['field9'].strip().split(" ")
            category = [request.form['field10'].strip().split(" ")]
            mg.add_book(asin, title=title, price=price, imUrl=url, category=category, brand=brand,
                        also_bought=alsoBought, also_viewed=alsoViewed, buy_after_viewing=buyAfterViewing,
                        bought_together=boughtTogether)
            return render_template("addsuccess.html")
    else:
        return render_template("addbook.html")

@app.route("/addsuccess", methods=['POST', 'GET'])
def addsuccess():
    return render_template("addsuccess.html")


if __name__ == "__main__":
    app.run()
