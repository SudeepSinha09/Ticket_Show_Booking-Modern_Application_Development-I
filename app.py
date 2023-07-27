from flask import Flask, render_template, redirect, request, url_for
#from flask_restful import Api, Resource, reqparse

'''SQL'''

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Venue(db.Model):
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String())
  place = db.Column(db.String())
  location = db.Column(db.String())
  capacity = db.Column(db.Integer())
  shows = db.relationship('Show', backref="venue")

class Show(db.Model):
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String())
  rating = db.Column(db.Integer())
  timing = db.Column(db.String())
  tags = db.Column(db.String())
  ticket_price = db.Column(db.Integer())
  venue_id = db.Column(db.Integer(), db.ForeignKey("venue.id"))
  bookings = db.relationship('User', backref="shows", secondary="association")

class User(db.Model):
  id = db.Column(db.Integer(), primary_key=True)
  email = db.Column(db.String(100), unique=True)
  password = db.Column(db.String(50))

class Admin(db.Model):
  id = db.Column(db.Integer(), primary_key=True)
  email = db.Column(db.String(100), unique=True)
  password = db.Column(db.String(50))

class Association(db.Model):
  show_id = db.Column(db.Integer(), db.ForeignKey("show.id"), primary_key=True)
  user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), primary_key=True)

#have to make an association table for show and user(many to many)
'''@configuration'''

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"

db.init_app(app)
app.app_context().push()

'''@controllers'''

'''USER'''

@app.route('/', methods=["GET", "POST"])
def home():
  if request.method == "GET":
    return render_template("1home.html")

@app.route('/user/new', methods=["GET", "POST"])
def new_user():
  if request.method == "GET":
    return render_template("2newuser.html")
  if request.method == "POST":
    email = request.form['email']
    password = request.form['password']
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    usr = User.query.filter_by(email=email).all()
    return render_template("3success.html", usr=usr)

@app.route('/user', methods=["GET", "POST"])
def user():
  if request.method == "GET":
    return render_template("4user.html")
  if request.method == "POST":
    email = request.form['email']
    password = request.form['password']
    try:
      usr = User.query.filter_by(email=email).all()
      if usr[0].email == email and usr[0].password == password:
        return render_template("3success.html", usr=usr)
    except:
      return render_template("5email_err.html")

@app.route("/user/profile/<id>", methods=["GET", "POST"])
def user_venue_show_details(id):
  venues = Venue.query.all()
  shows = Show.query.all()
  userid = id
  return render_template('6user_venue.html',
                         venues=venues,
                         shows=shows,
                         userid=userid)

@app.route('/user/book/<u_id>/<v_id>/<s_id>', methods=["GET", "POST"])
def book_show(v_id, u_id, s_id):
  if request.method == "GET":
    show_id = s_id
    userid = u_id
    sho = Show.query.filter_by(id=s_id).all()
    vnu = Venue.query.filter_by(id=v_id).all()
    return render_template('7book_show.html',
                           sho=sho,
                           vnu=vnu,
                           show_id=show_id,
                           userid=userid)
  if request.method == "POST":
    number = request.form['number']
    vnu = Venue.query.filter_by(id=v_id).all()
    temp = int(vnu[0].capacity) - int(number)
    if (temp < 0):
      return render_template('8cap_error.html')
    else:
      assn = Association(show_id=s_id, user_id=int(u_id))
      db.session.add(assn)
      vnu[0].capacity = temp
      usr = User.query.filter_by(id=u_id).all()
      db.session.commit()
      return render_template("3success.html", usr=usr)

@app.route("/user/bookings/<int:id>", methods=["GET", "POST"])
def user_bookings(id):
  if request.method == "GET":
    vnus = Venue.query.all()
    usr = User.query.get(id)
    bookings = usr.shows
    return render_template("9user_bookings.html", bookings=bookings, vnus=vnus)

'''ADMIN'''

'''
@app.route('/admin/new', methods=["GET", "POST"])
def new_admin():
  if request.method == "GET":
    return render_template("newadmin.html")
  if request.method == "POST":
    email = request.form['email']
    password = request.form['password']
    admin = Admin(email=email, password=password)
    db.session.add(admin)
    db.session.commit()
    usr = Admin.query.filter_by(email=email).all()
    return render_template("success.html", usr=usr)
'''

@app.route('/admin', methods=["GET", "POST"])
def admin():
  if request.method == "GET":
    return render_template("10admin.html")
  if request.method == "POST":
    email = request.form['email']
    password = request.form['password']
    admn = Admin.query.filter_by(email=email).all()
    print(admn)
    try:
      if admn[0].email == email and admn[0].password == password:
        return redirect('/admin/venue')
      else:
        return render_template("5email_err.html")
    except:
      return render_template("5email_err.html")

@app.route("/admin/venue", methods=["GET", "POST"])
def venue_show_Details():
  venues = Venue.query.all()
  shows = Show.query.all()
  return render_template('11venue.html', venues=venues, shows=shows)

@app.route("/admin/add_venue", methods=["GET", "POST"])
def add_venue():
  if request.method == "GET":
    return render_template('12add_venue.html')
  if request.method == "POST":
    venue = request.form['venue']
    place = request.form['place']
    location = request.form['location']
    capacity = request.form['capacity']
    vnu = Venue(name=venue, place=place, location=location, capacity=capacity)
    db.session.add(vnu)
    db.session.commit()
    return redirect("/admin/venue")

@app.route("/admin/venue/edit/<id>", methods=["GET", "POST"])
def edit_venue(id):
  if request.method == "GET":
    venueid = id
    return render_template("13edit_venue.html", venueid=venueid)
  if request.method == "POST":
    vnu = Venue.query.filter_by(id=int(id)).all()
    vnu[0].name = request.form['venue']
    vnu[0].place = request.form['place']
    vnu[0].location = request.form['location']
    vnu[0].capacity = request.form['capacity']
    db.session.commit()
    return redirect("/admin/venue")

@app.route("/admin/venue/delete/<id>", methods=["GET", "POST"])
def del_venue_confirmation(id):
  if request.method == "GET":
    vnu = Venue.query.filter_by(id=id).all()
    return render_template('14confirmation_venue.html', vnu=vnu)

@app.route("/admin/venue/delete/confirm/<id>", methods=["GET", "POST"])
def del_venue(id):
  Venue.query.filter_by(id=id).delete()
  db.session.flush()
  db.session.commit()
  return redirect('/admin/venue')

@app.route("/admin/actions/<id>", methods=["GET", "POST"])
def actions(id):
  if request.method == "GET":
    showid = id
    return render_template("15show_details.html", showid=showid)

@app.route('/admin/venue/show/<id>', methods=["GET", "POST"])
def add_show(id):
  if request.method == "GET":
    venueid = id
    return render_template('16add_show.html', venueid=venueid)
  if request.method == "POST":
    show = request.form['show']
    rating = request.form['rating']
    timing = request.form['timing']
    tags = request.form['tags']
    price = request.form['price']
    sho = Show(name=show,
               rating=rating,
               timing=timing,
               tags=tags,
               ticket_price=price,
               venue_id=id)
    db.session.add(sho)
    db.session.commit()
    return redirect("/admin/venue")

@app.route("/admin/show/edit/<id>", methods=["GET", "POST"])
def edit_show(id):
  if request.method == "GET":
    showid = id
    return render_template("17edit_show.html", showid=showid)
  if request.method == "POST":
    sho = Show.query.filter_by(id=int(id)).all()
    sho[0].name = request.form['show']
    sho[0].rating = request.form['rating']
    sho[0].timing = request.form['timing']
    sho[0].tags = request.form['tags']
    sho[0].ticket_price = request.form['price']
    db.session.commit()
    return redirect("/admin/venue")

@app.route("/admin/show/delete/<id>", methods=["GET", "POST"])
def delete_show_confirmation(id):
  if request.method == "GET":
    sho = Show.query.filter_by(id=id).all()
    return render_template('18confirmation_show.html', sho=sho)

@app.route("/admin/show/delete/confirm/<id>", methods=["GET", "POST"])
def delete_show(id):
  Show.query.filter_by(id=id).delete()
  db.session.flush()
  db.session.commit()
  return redirect('/admin/venue')

'''SEARCH'''

@app.route("/search", methods=["GET", "POST"])
def search():
  if request.method == "GET":
    return render_template("19search.html")

'''SEARCH VENUE'''

@app.route("/search/venue/options", methods=["GET", "POST"])
def venue_options():
  if request.method == "GET":
    return render_template("20venue_options.html")

@app.route("/search/venue/name", methods=["GET", "POST"])
def search_venue_name():
  if request.method == "GET":
    return render_template("21search_venue_name.html")
  if request.method == "POST":
    name = request.form["name"]
    vnus = Venue.query.all()
    return render_template("22search_venue_name_results.html",
                           vnus=vnus,
                           name=name)

@app.route("/search/venue/location", methods=["GET", "POST"])
def search_venue_location():
  if request.method == "GET":
    return render_template("23search_venue_location.html")
  if request.method == "POST":
    location = request.form["location"]
    vnus = Venue.query.all()
    return render_template("24search_venue_location_results.html",
                           vnus=vnus,
                           location=location)

'''SEARCH SHOW'''

@app.route("/search/show/options", methods=["GET", "POST"])
def show_options():
  if request.method == "GET":
    return render_template("25show_options.html")

@app.route("/search/show/name", methods=["GET", "POST"])
def search_show_name():
  if request.method == "GET":
    return render_template("26search_show_name.html")
  if request.method == "POST":
    name = request.form["name"]
    shos = Show.query.all()
    vnus = Venue.query.all()
    return render_template("27search_show_name_results.html",
                           shos=shos,
                           name=name,
                           vnus=vnus)

@app.route("/search/show/tags", methods=["GET", "POST"])
def search_show_tags():
  if request.method == "GET":
    return render_template("28search_show_tags.html")
  if request.method == "POST":
    tags = request.form["tags"]
    shos = Show.query.all()
    vnus = Venue.query.all()
    return render_template("29search_show_tags_results.html",
                           shos=shos,
                           tags=tags,
                           vnus=vnus)

@app.route("/search/show/rating", methods=["GET", "POST"])
def search_show_rating():
  if request.method == "GET":
    return render_template("30search_show_rating.html")
  if request.method == "POST":
    rating = int(request.form["rating"])
    shos = Show.query.all()
    vnus = Venue.query.all()
    return render_template("31search_show_rating_results.html",
                           shos=shos,
                           rating=rating,
                           vnus=vnus)
    
'''API'''
#api = Api()

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8080, debug=True)
  with app.app_context():
    db.create_all()