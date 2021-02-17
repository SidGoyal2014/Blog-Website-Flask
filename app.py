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
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://eurek8d7_common:common#123?@md-in-30.webhostbox.net:2083/eurek8d7_techblogflask'
app.config["UPLOAD_FOLDER"] = params_1["upload_location"]

SQLALCHEMY_POOL_RECYCLE=90

# app.config['SQLALCHEMY_POOL_RECYCLE'] = app.config['SQLALCHEMY_POOL_TIMEOUT'] - 1

# app.config.from_object(os.environ['APP_SETTINGS'])
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    # print("last : ",last)
    page = request.args.get("page")

    if(not str(page).isnumeric()):
        page = 1
    
    page = int(page)

    posts = posts[((page-1)*int(params_1["no_of_posts"])) : ((page-1)*int(params_1["no_of_posts"])+int(params_1["no_of_posts"]))]

    # print("print : ",page)

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
            title = request.form.get("title")
            subheading = request.form.get("subheading")
            slug = request.form.get("slug")
            content = request.form.get("content")
            date = datetime.now()

            post2 = Posts.query.filter_by(slug = slug).all()

            if(len(post2) > 0):
                return render_template("notify.html", params=params)
        
            # Save the file
            f = request.files["file1"]

            flag = True

            if(f.filename == ""):
                flag = False  # No file uploaded    
                img_filename = "netaji"

                print("title : ",title)
                print("subheading : ",subheading)

                # Create the entry
                entry = Posts(title=title, Subheading=subheading, slug=slug, content=content,img_filename=img_filename, date=date)

                # Add the session in the database
                db.session.add(entry)
                # Commit the changes to the database
                db.session.commit()
            else:
                flag = True  # File uploaded

                f.save(os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(f.filename)))

                img_filename = "netaji"

                print("title : ",title)
                print("subheading : ",subheading)

                # Create the entry
                entry = Posts(title=title, Subheading=subheading, slug=slug, content=content,img_filename=img_filename, date=date)

                # Add the session in the database
                db.session.add(entry)
                # Commit the changes to the database
                db.session.commit()

                posts = Posts.query.filter_by().all()
                x = len(posts)
                # print("x : ",x)
                sno1 = posts[x-1].sno
                # print("sno1 : ",sno1)
                # print("f.name : ",f.name)
                # print("Filename : ",f.filename)

                extension = f.filename.split(".")

                os.rename((params_1["upload_location"] + "\\" +f.filename) , (params_1["upload_location"] + "\\" + str(sno1) + "." + str(extension[1])))

                name_of_new_image = str(sno1) + "."  + extension[1]

                post1 = Posts.query.filter_by(sno = sno1).first()
                post1.img_filename = name_of_new_image
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

            # Load the row from the database
            post1 = Posts.query.filter_by(sno = sno).first()

            # Store the current row values in auxiliary memory
            prev_sno = post1.sno
            prev_title = post1.title
            prev_subheading = post1.Subheading
            prev_slug = post1.slug
            prev_content = post1.content
            prev_img_filename = post1.img_filename
            prev_date = post1.date

            # Delete the current row from the database
            post2 = Posts.query.filter_by(sno=sno).first()
            db.session.delete(post2)
            db.session.commit()

            # Now, we have to check if the slug is unique or not
            post = Posts.query.filter_by(slug = slug).all()

            # Check if the current row slug is unique or not
            if(len(post) > 0):
                # print("NO")
                # If not
                entry = Posts(title = prev_title, Subheading=prev_subheading, slug=prev_slug, content=prev_content, img_filename = prev_img_filename, date=prev_date)
                db.session.add(entry)
                db.session.commit()

                # Change the filename & reflect the changes in the database
                post3 = Posts.query.filter_by().all()

                x = len(post3)

                new_sno = post3[x-1].sno

                extension = prev_img_filename.split(".")

                os.rename((params_1["upload_location"] + "\\" +prev_img_filename) , (params_1["upload_location"] + "\\" + str(new_sno) + "." + str(extension[1])))

                # Reflect the changes in the database

                post3[x-1].img_filename = str(new_sno) + "." + str(extension[1])

                db.session.commit()

                return render_template("edit.html", params=params, post=post1)
            else:
                # Add the new post in the database
                entry = Posts(title=title, Subheading=subheading, slug=slug, content=content,img_filename=prev_img_filename, date=datetime.now())
                db.session.add(entry)
                db.session.commit()

                # Change the filename & reflect the changes in the database
                post3 = Posts.query.filter_by().all()

                x = len(post3)

                new_sno = post3[x-1].sno

                extension = prev_img_filename.split(".")

                os.rename((params_1["upload_location"] + "\\" +prev_img_filename) , (params_1["upload_location"] + "\\" + str(new_sno) + "." + str(extension[1])))

                post3[x-1].img_filename = str(new_sno) + "." + str(extension[1])

                db.session.commit()
            
                # Return to Dashboard
                post4 = Posts.query.filter_by().all()

                return render_template("dashboard.html", params=params,posts=post4)

        post3 = Posts.query.filter_by(sno=sno).first()
        return render_template("edit.html", sno=sno, params=params,post=post3)
    else:
        return redirect("/login")

@app.route("/login",methods=["GET","POST"])
def login():
    if("user" in session):
        return redirect("/dashboard")
    if(request.method == "POST"):
        username = request.form.get("username")
        password = request.form.get("password")

        # Making the object of the the table credetials
        credentials = Admin_panel_credentials.query.filter_by().all()

        for i in range(0,len(credentials)):
            if((username in credentials[i].username) and (password in credentials[i].password)):
                print("Password matched")
                session["user"] = username
                return redirect("/dashboard")
                # return render_template("dashboard.html",params=params,posts=posts)
    return render_template("login.html", params=params)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    posts = Posts.query.all()
    # To check if the admin is already logged in
    if ("user" in session):
        posts = Posts.query.all()
        # posts = Posts.query.all()
        return render_template("dashboard.html", params=params,posts=posts)
    return redirect("/login")

@app.route("/logout")
def logout():
    session["user"] = None
    session.pop("user")
    return redirect("/login")

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
