from flask import Flask,render_template,request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_mail import Mail, Message
import json
import os
import math

with open('config.json', 'r') as c:
    params = json.load(c)["social_media_links"]

with open('config.json', 'r') as c:
    creds = json.load(c)["credential_details"]

with open('config.json', 'r') as c:
    params_1 = json.load(c)["params"]

app = Flask(__name__)

app.secret_key = "super_secret_key"
app.config["UPLOAD_FOLDER"] = params_1["upload_location"]

#  Config the flask mail
app.config.update(
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_PORT = "465",
    MAIL_USE_SSL = True,
    MAIL_USERNAME = creds["gmail_username"],
    MAIL_PASSWORD = creds["gmail_password"]
)

mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/tech blog- flask'
db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_num = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(1200), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    Subheading = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(30), nullable=False)
    content = db.Column(db.String(5000), nullable=False)
    img_filename = db.Column(db.String(25), nullable=True)
    date = db.Column(db.String(12), nullable=True)

class Admin_panel_credentials(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    rights = db.Column(db.String(30), nullable=False)

@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params_1["no_of_posts"]))
    print("last : ",last)
    page = request.args.get("page")

    if(not str(page).isnumeric()):
        page = 1
    
    page = int(page)

    posts = posts[((page-1)*int(params_1["no_of_posts"])) : ((page-1)*int(params_1["no_of_posts"])+int(params_1["no_of_posts"]))]

    print("print : ",page)

    if(page == 1 and last == 1):
        prev = "#"
        next = "#"
    elif (page == 1):
        prev = "#"
        next = "/?page="+str(page+1)
    elif(page == last):
        prev = "/?page="+str(page-1)
        next = "#"
    else:
        prev = "/?page="+str(page-1)
        next = "/?page="+str(page+1)

    return render_template("index.html", params=params, posts=posts, prev=prev, next=next)
    
    """
    posts = Posts.query.filter_by().all()[0:params_1["no_of_posts"]]
    return render_template('index.html',params=params, posts=posts)
    """

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", params=params, post=post)

@app.route("/about")
def about():
    return render_template('about.html',params=params)

@app.route("/add", methods=["GET", "POST"])
def add():
    if ("user" in session and session["user"]!=None):
        print("Session is there")
        if(request.method == "POST"):
            # print("title : ",title)
            # print("subheading : ",subheading)
            title = request.form.get("title")
            subheading = request.form.get("subheading")
            slug = request.form.get("slug")
            content = request.form.get("content")
            date = datetime.now()
            img_filename = "netaji"

            print("title : ",title)
            print("subheading : ",subheading)

            entry = Posts(title=title, Subheading=subheading, slug=slug, content=content,img_filename=img_filename, date=date)

            db.session.add(entry)
            db.session.commit()
        return render_template("add.html", params=params)
    return render_template("login.html", params=params)

# To edit the post
@app.route("/edit/<string:sno>", methods=["GET","POST"])
def edit(sno):
    if ("user" in session and session["user"]!=None):
        print("The session is there")
        if (request.method == "POST"):
            title = request.form.get('title')
            subheading = request.form.get('subheading')
            slug = request.form.get('slug')
            content = request.form.get('content')
            # print("title: ",title)
            # print("subheading: ",subheading)
            """
            if (sno == '0'):
                post = Posts(title=title, subheading=subheading, slug=slug, content=content)
                db.session.add(post)
                db.session.commit()
            """
            # else:
            # print("sno : ",sno)
            # print("title : ",title)
            post = Posts.query.filter_by(sno = sno).first()
            post.title = title
            post.Subheading = subheading
            post.slug = slug
            post.content = content
            db.session.commit()
        post = Posts.query.filter_by(sno=sno).first()
        return render_template("edit.html", sno=sno, params=params,post=post)
    else:
        print("The session is not there")
        return render_template("login.html", params=params)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    posts = Posts.query.all()

    if "user" in session:
        return render_template("dashboard.html", params=params,posts=posts)

    # the below if block is for letting the admin in the dashboard after succesful login
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        print("username ",username)
        print("password ",password)

        # Making the object of the the table credetials
        credentials = Admin_panel_credentials.query.filter_by().all()
        # CORRECT print(credentials[0].username)

        for i in range(0,len(credentials)):
            if((username in credentials[i].username) and (password in credentials[i].password)):
                session["user"] = username
                return render_template("dashboard.html",params=params,posts=posts)

    return render_template('login.html',params=params)

@app.route("/logout")
def logout():
    session["user"] = None
    session.pop("user")
    return redirect("/dashboard")

@app.route("/uploader", methods=["GET","POST"])
def uploader():
    if ("user" in session and session["user"]!=None):
        if request.method == "POST":
            f = request.files["file1"]
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(f.filename)))
            return "Uploded Successfully"

@app.route("/delete/<string:sno>", methods=["GET","POST"])
def detete(sno):
    if ("user" in session and session["user"]!=None):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, email=email, phone_num=phone, message=message)
        db.session.add(entry)
        db.session.commit()
        mail.send_message("New Message from "+name,
                            sender = email,
                            recipients=[creds['gmail_username']],
                            body=message+"\n"+phone)
    return render_template('contact.html',params=params)

if __name__ == "__main__":
    app.run(debug=True)