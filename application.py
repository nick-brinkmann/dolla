import os
import datetime
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd
from credit import verify
import re

# Configure application
app = Flask(__name__)

# Adds secret key
app.secret_key = b'\xbe\xe9\x8c\xca\x88}dG\x82C"\x83\x92\xb3\xf6\x7f'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///data.db")
db = SQL("postgres://qxoohwegzhpiry:2000cce701ee5c30d6dbd66dbe0b76e21dc456acd4064c0687fe16aff63c5733@ec2-54-225-95-183.compute-1.amazonaws.com:5432/d32v5o8mbggho1")


# INDEX
@app.route("/")
@login_required
def index():
    """Homepage of website"""
    #User's cash balance
    cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = session["user_id"])
    balance = usd(float(cash[0]["cash"]))
    # List of user's friends, ordered alphabetically
    friends = findfriends()
    # Get conversation id for user and friend
    for friend in friends:
        convo = db.execute("SELECT * FROM convos WHERE (user1_id = :user_id AND user2_id = :friend_id) OR (user1_id = :friend_id AND user2_id = :user_id)", user_id = session["user_id"],
                            friend_id = friend["id"])
        friend["convo_id"] = convo[0]["id"]
    # Query for (money) requests. Most recent requests first, max. of 15 requests loaded
    requests = db.execute("SELECT * FROM transactions WHERE sender_id = :user_id AND confirmed IS NULL ORDER BY id DESC LIMIT 15", user_id = session["user_id"])
    # Gets username of (money) request sender
    for request in requests:
        username = db.execute("SELECT username FROM users WHERE id = :request_sender_id", request_sender_id = request["recipient_id"])
        # Sender indicates person that sent the request
        request["sender"] = username[0]["username"]
        request["amount"] = usd(float(request["amount"]))

    # Query for friend requests. Most recent requests first, max. of 15.
    friend_requests = db.execute("SELECT * FROM friends WHERE recipient_id = :user_id AND confirmed IS NULL ORDER BY id DESC LIMIT 15", user_id = session["user_id"])
    # Gets username of person sending friend request
    for request in friend_requests:
        username = db.execute("SELECT username FROm users WHERE id = :sender_id", sender_id = request["sender_id"])
        request["sender"] = username[0]["username"]
    amount_friend_requests = len(friend_requests)

    #Query to see if user has card on file
    cof = db.execute("SELECT cof FROM users WHERE id = :user_id", user_id = session["user_id"])
    cof = cof[0]["cof"]


    return render_template("index.html", friends = friends, requests = requests, balance = balance, amount_requests = len(requests),
                            amount_friends = len(friends), friend_requests = friend_requests, amount_friend_requests = amount_friend_requests, cof = cof)


# ACCEPT (MONEY REQUEST)
@app.route("/accept", methods=["POST"])
@login_required
def accept_request():
    # Gets transaction ID
    transaction_id = list(request.form.keys())[0].strip()
    # Gets amount requested
    data = db.execute("SELECT amount FROM transactions WHERE id = :transaction", transaction = int(transaction_id))
    amount = data[0]["amount"]
    # Gets users current balance
    balance = get_balance()
    # Queries for data from requester
    requester_data = db.execute("SELECT * FROM users WHERE id = (SELECT recipient_id FROM transactions WHERE id = :transaction)", transaction = transaction_id)
    requester_balance = requester_data[0]["cash"]

    # Checks if user can afford transaction with balance on account
    if balance < amount:

        # If user has card on file transaction goes through
        if len(db.execute("SELECT * FROM users WHERE id = :user_id AND NOT cof = 0", user_id = session["user_id"])) == 1:
            now = datetime.datetime.now()
            db.execute("UPDATE users SET cash = :new_balance WHERE id = :user_id", new_balance = 0, user_id = session["user_id"])
            db.execute("UPDATE users SET cash = :new_balance WHERE id = :recipient_id", new_balance = requester_balance + amount, recipient_id = requester_data[0]["id"])
            db.execute("UPDATE transactions SET confirmed = 1 WHERE id = :transaction", transaction = int(transaction_id))
            return redirect("/")

        # If user cannot afford and no card on file then
        else:
            return apology("Sorry, this transaction could not go through. Add funds or link a card.")

    else:
        now = datetime.datetime.now()
        db.execute("UPDATE users SET cash = :new_balance WHERE id = :user_id", new_balance = balance - amount, user_id = session["user_id"])
        db.execute("UPDATE users SET cash = :new_balance WHERE id = :recipient_id", new_balance = requester_balance + amount, recipient_id = requester_data[0]["id"])
        db.execute("UPDATE transactions SET confirmed = 1 WHERE id = :transaction", transaction = int(transaction_id))

        flash("Request accepted!")
        return redirect("/")


# ADD CARD
@app.route("/add_card", methods=["POST"])
@login_required
def add_card():
    # Ensures card number valid
    card_number = request.form.get("card_number")
    if verify(card_number) != True:
        return apology("Invalid credit card number")

    # Adds card to file
    card_hash = generate_password_hash(card_number)
    db.execute("UPDATE users SET cof = 1, card_hash = :card_hash WHERE id = :user_id", card_hash = card_hash, user_id = session["user_id"])

    # Redirects with flash
    flash("Card added!")
    return redirect("/")


# ADD FRIEND
@app.route("/addfriend", methods=["POST"])
@login_required
def add_friend():
    #Recognizes which request user is responding to by accessing friendship ID
    request_id = list(request.form.keys())[0].strip()

    # Updates friends table to establish friendship
    db.execute("UPDATE friends SET confirmed = 1 WHERE id = :request", request = request_id)

    # Accesses friendship information
    friendship = db.execute("SELECT * FROM friends WHERE id = :request", request = request_id)
    db.execute("INSERT INTO convos (user1_id, user2_id) VALUES (:user_id, :other_id)", user_id = session["user_id"], other_id = friendship[0]["sender_id"])

    flash("Friend request confirmed!")
    return redirect("/")


# CHANGE CARD
@app.route("/change_card", methods=["POST"])
@login_required
def change_card():
    # Provide password
    if not request.form.get("password"):
        return apology("Provide a password", 403)

    # Ensures password valid
    rows = db.execute("SELECT hash FROM users WHERE id = :user_id",
                      user_id=session["user_id"])
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        return apology("Invalid password", 403)

    # Ensures card number valid
    card_number = request.form.get("card_number")
    if verify(card_number) != True:
        return apology("Invalid credit card number")

    # Changes card on file
    card_hash = generate_password_hash(card_number)
    db.execute("UPDATE users SET cof = 1, card_hash = :card_hash WHERE id = :user_id", card_hash = card_hash, user_id = session["user_id"])

    # Redirects with flash
    flash("Card changed!")
    return redirect("/")


# DECLINE (MONEY REQUEST)
@app.route("/decline", methods=["POST"])
@login_required
def decline_request():
    # Accesses the transaction id of request
    transaction_id = list(request.form.keys())[0].strip()
    # Updates transactions table setting confirmed to 0 to indicate declined transaction
    db.execute("UPDATE transactions SET confirmed = 0 WHERE id = :transaction", transaction = int(transaction_id))

    flash("Request declined.")
    return redirect("/")


# DECLINE (FRIEND REQUEST)
@app.route("/declinefriend", methods=["POST"])
@login_required
def decline_friend():
    # Access id of friend requests
    request_id = list(request.form.keys())[0].strip()

    # Updates friends table to set confirmed to 0
    db.execute("UPDATE friends SET confirmed = 0 WHERE id = :request", request = request_id)

    flash("Friend request declined.")
    return redirect("/")


# DONATIONS
@app.route("/donations", methods=["GET", "POST"])
@login_required
def donations():
    """Show potential donations"""

    # User has just donated to some cause
    if request.method == "POST":
        # Gets relevant variables
        amount = float(request.form.get("amount"))
        donreq_id = list(request.form.keys())[1].strip()

        # Ensures amount was given
        if amount <= 0:
            return apology("Donation amount must be a positive number", 400)


        # Gets user's current cash balance
        balance = get_balance()

        # Card not on file
        cof = db.execute("SELECT cof FROM users WHERE id = :user_id", user_id=session["user_id"])
        cof = cof[0]["cof"]
        if cof == 0:
            # Not enough cash
            if balance < amount:
                return apology("Not enough money & card not on file")

        # Card on file or enough cash
        new_cash = balance - amount
        if new_cash < 0:
            # Someone can't have negative cash - it sets it to 0 and the remainder is 'covered' by the card transaction
            new_cash = 0
        # Sender's balance gets updated
        db.execute("UPDATE users SET cash = :new_cash WHERE id = :user_id", new_cash = new_cash, user_id=session["user_id"])
        # Getting recipient id
        recipient_id = db.execute("SELECT requester_id FROM donation_reqs WHERE id = :donreq_id", donreq_id=donreq_id)
        recipient_id = recipient_id[0]["requester_id"]
        # Updating recipient's money
        recipient_cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = recipient_id)
        recipient_cash = recipient_cash[0]["cash"]
        recipient_cash += amount
        db.execute("UPDATE users SET cash = :cash WHERE id = :user_id", cash = recipient_cash, user_id = recipient_id)

        # Adds row to donations
        db.execute("INSERT INTO donations (donation_id, donor_id, amount) VALUES (:donation_id, :donor_id, :amount)", donation_id = donreq_id, donor_id = session["user_id"], amount = float(amount))

        # Adds row to transactions
        db.execute("INSERT INTO transactions (sender_id, recipient_id, amount, msg, confirmed) VALUES (:sender_id, :recipient_id, :amount, 'DONATION', 1)", sender_id = session["user_id"], recipient_id = recipient_id, amount = float(amount))

        # Updates donation_reqs table
        info = db.execute("SELECT current, goal FROM donation_reqs WHERE id = :donreq_id", donreq_id = donreq_id)
        current = info[0]["current"]
        goal = info[0]["goal"]
        current += amount
        # Goal has been reached
        if current >= goal:
            db.execute("UPDATE donation_reqs SET reached = 1 WHERE id = :donreq_id", donreq_id = donreq_id)
        # Updates current amount
        db.execute("UPDATE donation_reqs SET current = :current WHERE id = :donreq_id", current = current, donreq_id = donreq_id)

        # All done, so redirect with flash
        flash("Donation successful. Thank you!")
        return redirect("/")

    # User arrived via GET
    else:
        # Unfulfilled donation requests, newest first, limit of 50. (Can receive donation requests from people you're not friends with)
        donreqs = db.execute("SELECT * FROM donation_reqs WHERE reached IS NULL ORDER BY id DESC LIMIT 50")

        # Adds requester's name
        for donreq in donreqs:
            requester_id = donreq["requester_id"]
            fullname = db.execute("SELECT fullname FROM users WHERE id = :user_id", user_id = requester_id)
            fullname = fullname[0]["fullname"]
            donreq["fullname"] = fullname
            # Changes to USD formatting.
            donreq["goal"] = usd(donreq["goal"])
            donreq["current"] = usd(donreq["current"])

        return render_template("donations.html", donreqs = donreqs, user_id = session["user_id"])


# DONATION REQUEST
@app.route("/donreq", methods=["GET", "POST"])
@login_required
def donreq():
    """Submit a donation request"""

    # Arrived via POST
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        goal = request.form.get("goal")

        # Error checking
        if not title:
            return apology("Enter title")
        if not description:
            return apology("Enter description")
        if not goal:
            return apology("Enter goal amount")

        # All seems good. Insert into database
        db.execute("INSERT INTO donation_reqs (requester_id, goal, title, description) VALUES (:user_id, :goal, :title, :description)",
                   user_id = session["user_id"], goal = goal, title = title, description = description)

        # Redirects to donations page
        flash("Donation request created!")
        return redirect("/donations")

    # Arrived via GET
    else:
        return render_template("donreq.html")


# DONATION REQUEST SEARCH
@app.route("/donation_search")
@login_required
def donation_search():
    # Arrived via GET
    # Saves name to be searched
    searchname = request.args["searchname"]
    searchname = '%' + searchname + '%'

    # Queries DB for people whose name/username is like searchname
    names = db.execute("SELECT id, username, fullname FROM users WHERE username LIKE :searchname OR fullname LIKE :searchname", searchname = searchname)

    # List of donations for ultimate use
    donations = []

    # Ensures at least one person was found
    if len(names) != 0:
        # If that user has an unmet donation request, that request is added to a list of donations to display.
        for name in names:
            user_donations = db.execute("SELECT * FROM donation_reqs WHERE requester_id = :user_id AND reached IS NULL", user_id = name["id"])

            # Ensures user has at least 1 donation request
            if len(user_donations) == 0:
                continue

            # Adds requester's fullname for display
            for user_donation in user_donations:
                user_donation["fullname"] = name["fullname"]

            # Appends to donations list
            donations.append(user_donation)

    # Now queries DB for donation_requests whose title/description is like searchname
    don_reqs = db.execute("SELECT * FROM donation_reqs WHERE title LIKE :searchname OR description LIKE :searchname AND reached IS NULL", searchname = searchname)

    # Ensures at least one donation request was returned
    if len(don_reqs) != 0:
        for don_req in don_reqs:
            print(don_req)
            # Adds user's fullname
            fullname = db.execute("SELECT fullname FROM users WHERE id = :requester_id", requester_id = don_req["requester_id"])
            don_req["fullname"] = fullname[0]["fullname"]

            # Appends to donations list
            donations.append(don_req)


    # Renders search results template. Includes user_id so that user can't donate to their own cause, like in the regular donations page
    return render_template("donationresults.html", donations = donations, user_id = session["user_id"])


# FRIEND REQUEST
@app.route("/friendrequest", methods=["POST"])
@login_required
def friend_request():
    # Recognizes which person user is trying to send friend request to
    recipient_username =  list(request.form.keys())[0].strip()

    #Gets ID of person receiving friend request
    recipient = db.execute("SELECT id FROM users WHERE username = :username", username = recipient_username)

    #Sends friend request to user
    db.execute("INSERT INTO friends (sender_id, recipient_id) VALUES (:sender_id, :recipient_id)", sender_id = session["user_id"], recipient_id = recipient[0]["id"])

    flash("Friend request sent!")
    return redirect("/")


# HISTORY (TRANSACTIONS)
@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Max. of 50 transactions loaded
    history = db.execute("SELECT * FROM transactions WHERE (sender_id = :user_id OR recipient_id = :user_id) AND confirmed = 1 ORDER BY id DESC LIMIT 50", user_id=session["user_id"])

    # Adds usernames
    for transaction in history:
        sender_name = db.execute("SELECT username FROM users WHERE id = :sender_id", sender_id = transaction["sender_id"])
        recipient_name = db.execute("SELECT username FROM users WHERE id = :recipient_id", recipient_id = transaction["recipient_id"])
        # Only time recipient name is 0 is when BANK is involved
        if len(recipient_name) == 0:
            transaction["recipient"] = "BANK"
        else:
            transaction["recipient"] = recipient_name[0]["username"]

        transaction["sender"] = sender_name[0]["username"]
        transaction["amount"] = usd(float(transaction["amount"]))

    return render_template("history.html", history=history)


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# LOGOUT
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# MESSAGES
@app.route("/messages", methods=["GET", "POST"])
@login_required
def messages():
    """Show messages between users"""
    if request.method == "POST":
        # Send messages to other user
        # Access message from form
        message = request.form.get("content")
        conversation = db.execute("SELECT * FROM convos WHERE user1_id = :user_id OR user2_id = :user_id", user_id = session["user_id"])

        # Access id of other person in conversation
        if conversation[0]["user1_id"] == session["user_id"]:
            recipient_id = conversation[0]["user2_id"]
        else:
            recipient_id = conversation[0]["user1_id"]

        db.execute("INSERT INTO messages (sender_id, recipient_id, content, convo_id) VALUES (:sender_id, :recipient, :content, :convo_id)", sender_id = session["user_id"],
                    recipient = recipient_id , content = message, convo_id = int(request.form.get("conversation_id")))

        return redirect("/messages?conversation_id=" + request.form.get("conversation_id"))

    # If method is GET load all messages
    else:
        # Query database for all conversations involving user
        convos = db.execute("SELECT * FROM convos WHERE user1_id = :user_id OR user2_id = :user_id", user_id = session["user_id"])

        # For each conversation store id and username of other user as "person_id" and "person_username" respectively
        for conversation in convos:
            # Get latest messsage in each conversation
            latest = db.execute("SELECT content, id FROM messages WHERE convo_id = :convo ORDER BY id DESC LIMIT 1", convo = conversation["id"])
            if len(latest) != 0:
                conversation["latest_message"] = latest[0]["content"]
                conversation["order"] = latest[0]["id"]
            else:
                conversation["latest_message"] = ""
                conversation["order"] = 0

            # Get id and username of person that conversation is with
            if conversation["user1_id"] == session["user_id"]:
                person = db.execute("SELECT username FROM users WHERE id = :user2", user2 = conversation["user2_id"])
                conversation["person_id"] = conversation["user2_id"]
                conversation["person_username"] = person[0]["username"]

            elif conversation["user2_id"] == session["user_id"]:
                person = db.execute("SELECT username FROM users WHERE id = :user1", user1 = conversation["user1_id"])
                conversation["person_id"] = conversation["user1_id"]
                conversation["person_username"] = person[0]["username"]

        conversations =sorted(convos, key = lambda k:k["order"], reverse = True)

        # If user is not opening a specific conversation
        if not request.args.get("conversation_id"):
            friends = findfriends()
            # Adds conversation id between friend and user to dictionary of friends
            for friend in friends:
                convo_id = db.execute("SELECT id FROM convos WHERE (user1_id = :user_id AND user2_id = :friend) OR (user1_id = :friend AND user2_id = :user_id)", user_id = session["user_id"],
                            friend = friend["id"])
                friend["convo_id"] = convo_id[0]["id"]

            return render_template("messages.html", conversations = conversations, amount = None, friends = friends)

        # If user is opening a specific conversation
        else:
            # Get id of conversation selected
            convo_id = request.args.get("conversation_id")

            # Query messages for all messages in specified conversation
            messages = db.execute("SELECT * FROM messages WHERE convo_id = :convo ORDER BY id DESC", convo = convo_id)
            messages.reverse()
            amount = len(messages)

            return render_template("messages.html", conversations = conversations, messages = messages, amount = amount, user_id = session["user_id"], convo_id = convo_id)



# PASSWORD CHANGE
@app.route("/pass_change", methods=["POST"])
@login_required
def change():
    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE id = :user_id",
                          user_id=session["user_id"])

    # Ensure username exists and password is correct
    if not check_password_hash(rows[0]["hash"], request.form.get("current_password")):
            return apology("incorrect current password", 403)

    # Checks that new password is not the same as old one
    elif request.form.get("current_password") == request.form.get("new_password"):
        return apology("new password cannot be the same as the old one")

    # Checks that new password matches confirmation
    elif request.form.get("new_password") != request.form.get("confirm"):
        return apology("New password does not match confirmation field")


    else:
        db.execute("UPDATE users SET hash = :newhash WHERE id = :user_id", newhash=generate_password_hash(request.form.get("new_password")), user_id=session["user_id"])

    flash("Password successfully changed!")
    return redirect("/")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Checks that user inputs both a username and a password
        if not request.form.get("username"):
            return apology("must provide a username")

        # Checks that user is inputting a password
        elif not request.form.get("password"):
            return apology("must provide a password")

        # Checks that password matches with password confirmation
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation do not match")

        # Checks that user put in a full name
        elif not request.form.get("fullname"):
            return apology("Please include your name")

        # Query database for users
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            username=request.form.get("username"))

        # If a row is returned then the username already exists in database
        if len(rows) != 0:
            return apology("sorry, username already exists")

        # If no rows are returned then user can be registered with that username
        else:
            db.execute("INSERT INTO users (username, fullname, hash) VALUES (:username, :fullname, :pass_hash)", username=request.form.get("username"),
                        fullname = request.form.get("fullname"), pass_hash=generate_password_hash(request.form.get("password")))

        new_id = db.execute("SELECT id FROM users WHERE username = :username", username = request.form.get("username"))
        session["user_id"] = new_id[0]["id"]

        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


# REQUEST (MONEY)
@app.route("/request", methods=["GET", "POST"])
@login_required
def makerequest():
    """Send money to another user"""
    # Arrived via POST
    if request.method == "POST":

        # Gets requestee's id and updates DB
        message = request.form.get("message")
        sender = db.execute("SELECT id FROM users WHERE username = :friend", friend = request.form.get("friend"))
        db.execute("INSERT INTO transactions (sender_id, recipient_id, amount, msg) VALUES (:sender_id, :recipient_id, :amount, :message)", sender_id = sender[0]["id"],
                    recipient_id = session["user_id"], amount = float(request.form.get("amount")), message = request.form.get("message"))

        # Flash and redirect
        flash("Request sent!")
        return redirect("/")

    else:
        friends = findfriends()
        return render_template("request.html", friends = friends)



# SEARCH PEOPLE
@app.route("/search")
@login_required
def search():
    # Arrived via GET
    # Saves name to be searched
    searchname = request.args
    searchname = searchname["searchname"]
    searchname = '%' + searchname + '%'

    # Queries DB for people with similar names
    names = db.execute("SELECT id, username, fullname FROM users WHERE username LIKE :searchname OR fullname LIKE :searchname", searchname = searchname)

    # No users like that
    if len(names) == 0:
        return apology("No users with that name exist, sorry")

    # Some users with names like that exist
    else:
        # If user is already friends with person (or returned person is the user themself), no option to add friend
        for name in names:
            isfriends = db.execute("SELECT confirmed FROM friends WHERE (sender_id = :name_id AND recipient_id = :user_id) OR (sender_id = :user_id AND recipient_id = :name_id)",
                                   name_id = name["id"], user_id = session["user_id"])

            # Should return either 0 or 1 line
            if len(isfriends) == 0:
                # No friend request sent
                if name["id"] != session["user_id"]:
                    name["isfriend"] = 0
            elif isfriends[0]["confirmed"] is None:
                # Friend request sent but not confirmed
                name["isfriend"] = None
            elif isfriends[0]["confirmed"] == 1:
                # Friend request sent and confirmed
                name["isfriend"] = 1
                convo = db.execute("SELECT * FROM convos WHERE (user1_id = :name_id AND user2_id = :user_id) OR (user1_id = :user_id AND user2_id = :name_id)", name_id = name["id"],
                                    user_id = session["user_id"])
                name["convo_id"] = convo[0]["id"]

            # The logic is now handled in the HTML, as each name has an 'isfriend' key: 0 if not friends, 1 if friends
        #DO LATER
        return render_template("searchresults.html", names = names, user_id = session["user_id"])


# SEND (MONEY)
@app.route("/send", methods=["GET", "POST"])
@login_required
def send():
    """Send money to another user"""

    # Arrived via POST
    if request.method == "POST":

        # Useful variables
        friend = request.form.get("friend")
        amount = request.form.get("amount")
        message = request.form.get("message")
        funds = db.execute("SELECT cash, cof FROM users WHERE id = :user_id", user_id=session["user_id"])
        # Gets friend's id
        friendid = db.execute("SELECT id FROM users WHERE username = :username", username = friend)
        friendid = friendid[0]["id"]

        # Transfer amount is more than user has
        if float(amount) > funds[0]["cash"]:
            # User hasn't linked credit card
            if funds[0]["cof"] == 0:
                return apology("Link your card or add money")

            # User has linked credit card - drains current cash and 'transfers' remainder using credit card
            else:
                # Sender's cash set to 0
                db.execute("UPDATE users SET cash = 0 WHERE id = :user_id", user_id = session["user_id"])

                # Updates recipient's cash
                recipient_cash = db.execute("SELECT cash FROM users WHERE id = :recipient_id", recipient_id = friendid)
                recipient_cash = recipient_cash[0]["cash"]
                recipient_cash = recipient_cash + float(amount)
                db.execute("UPDATE users SET cash = :newcash WHERE id = :recipient_id", newcash = recipient_cash, recipient_id = friendid)

                # Inserts into transactions
                # Note confirmed is 1 because money comes from sender.
                # If money requested, then confirmed = 0 until request has been confirmed (or denied)
                db.execute("INSERT INTO transactions (sender_id, recipient_id, amount, msg, confirmed) VALUES (:sender_id, :recipient_id, :amount, :msg, 1)", sender_id = session["user_id"], recipient_id = friendid, amount = amount, msg=message)

        # User has enough cash: updates database ONLY USING CASH
        else:
            # Inserts into transactions
            db.execute("INSERT INTO transactions (sender_id, recipient_id, amount, msg, confirmed) VALUES (:sender_id, :recipient_id, :amount, :msg, 1)", sender_id = session["user_id"], recipient_id = friendid, amount = amount, msg=message)

            #Updates SENDER'S cash
            sender_cash = db.execute("SELECT cash FROM users WHERE id = :sender_id", sender_id = session["user_id"])
            sender_cash = sender_cash[0]["cash"]
            sender_cash = sender_cash - float(amount)
            db.execute("UPDATE users SET cash = :newcash WHERE id = :sender_id", newcash = sender_cash, sender_id = session["user_id"])

            # Updates RECIPIENT'S cash
            recipient_cash = db.execute("SELECT cash FROM users WHERE id = :recipient_id", recipient_id = friendid)
            recipient_cash = recipient_cash[0]["cash"]
            recipient_cash = recipient_cash + float(amount)
            db.execute("UPDATE users SET cash = :newcash WHERE id = :recipient_id", newcash = recipient_cash, recipient_id = friendid)

        # Money has been sent
        flash("Money sent!")
        return redirect("/")

    # Arrived via GET
    else:
        #Gets friends to give as options
        friends = findfriends()
        return render_template("send.html", friends = friends)



# SETTINGS
@app.route("/settings")
@login_required
def settings():
    # Give settings access to whether a user has a card on file
    cof = db.execute("SELECT cof FROM users WHERE id = :user_id", user_id = session["user_id"])
    cof = cof[0]["cof"]
    return render_template("settings.html", cof = cof)


# TRANSFER (TO BANK ACC)
@app.route("/transfer_funds", methods=["POST"])
@login_required
def addfunds():
    #Query database to access user data
    user_data = db.execute("SELECT * FROM users WHERE id = :user_id", user_id = session["user_id"])

    # Check that amount is valid
    if not re.fullmatch('^[0-9]+(\.[0-9]{1,2})?$', request.form.get("amount")):
        return apology("Input only dollar units and cents, separated by a period", 403)

    # Check password
    if not check_password_hash(user_data[0]["hash"], request.form.get("password")):
        return apology("Incorrect password")

    else:
        # Check that user has a card on file
        if len(db.execute("SELECT * FROM users WHERE id = :user_id AND NOT cof = 0", user_id = session["user_id"])) == 0:
            flash("No card on file. Please add a card.")
            return redirect("/settings")

        # If user has a card on file check that user can afford transaction
        elif float(user_data[0]["cash"]) < float(request.form.get("amount")):
            return apology("Sorry, you do not have that amount of money to transfer.")

        else:
            db.execute("UPDATE users SET cash = :new_balance WHERE id = :user_id", new_balance = float(user_data[0]["cash"]) - float(request.form.get("amount")), user_id = session["user_id"])
            db.execute("INSERT INTO transactions (sender_id, recipient_id, amount, msg, confirmed) VALUES (:sender_id, 0, :amount, :message, 1)", sender_id = session["user_id"], amount = float(request.form.get("amount")),
                        message = "Transferred money to bank.")
            return redirect("/")

# ------------------------------------------------------------------------------------------------------------------------------------------------------------#
# HELPER FUNCTIONS

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

# Returns a user's friends
def findfriends():
    # Queries database. All friends, alphabetically
    friends = db.execute("SELECT id, username, fullname FROM users WHERE id IN (SELECT recipient_id FROM friends WHERE sender_id = :user_id AND confirmed = 1) OR id IN (SELECT sender_id FROM friends WHERE recipient_id = :user_id AND confirmed = 1) ORDER BY username",
                       user_id = session["user_id"])

    return friends


# Returns current balance of user
def get_balance():
    cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = session["user_id"])
    balance = cash[0]["cash"]
    return balance