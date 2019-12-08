DOLLA'S DESIGN

FRAMEWORK:
We largely used Flask, and adopted the skeleton of Finance. For our database, we used SQLite3, contained in data.db. In just one case, we made use of
JavaScript, and otherwise made our pages interactive using Jinja.

DATABASE:
The database (data.db) manages the storing and organization of all kinds of data including user data, transactions, friendships, messages and donation request posts.
This was done using 7 tables total which include:

    - convos (conversations):
    Whenever a friendship is confirmed a new entry was made to create a conversation between the two users involved in the friendship. This included the user id for each
    user (foreign key referencing the users table) and a unique id for the conversation itself. This helped when we needed to identify which conversations to open.
        * We now realize that a better design may have been to make the "conversations" based on the friendships table as it is inefficient to have this table for the sole
        purpose of opening conversations. However, due to time constraints we were unable to change all of our code to be reliant on the friends table.

    - donation_reqs (donation requests):
    Whenever someone made a new donation request we updated this table by inserting a new row consisting of the requester's user id, request title and description, goal amount,
    current amount achieved, date that it was posted and a unique id for the request itself. There is also a boolean value named "reached" which is false by default, but changes
    to true when the goal is met.

    - donations (donation transactions):
    Every donation made is documented in this table by inserting a row consisting of the donor's user id, the id of the donation they donated to, and the amount that was donated.

    - friends (friendship status between users):
    When a friend request is made there is a new entry into the friends table consisting of a unique id, the the sender id, recipient id and a boolean named "confirmed" which is set to NULL by
    default. Once the recipient responds with either "Accept" or "Decline" the table entry gets updated changing "confirmed" to either 1 or 0 accordingly. Each friend request has a
    unique id. If the request is denied, the user can make a new request, and a new entry will be made. This table allows us to query the database later, accessing users whose friendship status
    set, in other words "confirmed" has been set equal to 1. This way we allow certain interactions to occur only between users that are friends.

    - messages (all messages):
    The messages table stores all messages sent between users. When a message is sent a new entry is made with a unique id, convo id, sender id, recipient id, the content and a date. The
    sender and recipient ids reference the users table, while the convo id references the convos table. Setting up the table this way helps us organize when to load which messages, based
    on which conversation they belong to.

    - transactions (all transactions):
    Whenever the user sends money, or accepts a money request from another user, the transactions table is updated with a new transaction. This entry includes the sender id, recipient id,
    amount, message/explanation and date. Each transaction has a boolean of "confirmed" whose value depends on the type of transaction. If the transaction is a "send" transaction
    then its value is 1 meaning that it has been confirmed in which case we update the users' information (balance, transaction history, etc.). If he transaction is a "request" then
    its value is set to NULL and only when the recipient of the request either accepts or declines it is its value set to 1 or 0 depending on the response. If it's accepted then, again,
    both users' information is updated.

    - users (user information)
    The users table manages all information relating to individual users. This stores their unique id (assigned upon registration), full name, username, password hash, balance (cash), as well
    as a boolean named "cof" for "card on file" which is set to false by default and changed to true when a card is added. If a card is added then its hash it also added to the users information.


PYTHON (APPLICATION.PY):

    - ROUTES:
    For every distinct action we wanted to implement, we chose to create a new route. This allowed us to bypass the issue of needing to check certain conditions
    in each route. This also modularized our functionality so that it was easier to find certain actions and change them according to their specific requirements.

    - MANAGING USERS:
    Whenever a user registers, we use forms to access the information they input and update our database.
    When the user logs in, we check the database to ensure the user exists and the password they input is correct.
    When the user adds a card, we update the 'cof' (card on file) column in the users table of the database, and similarly store a hash of their card number.
    When the user is involved in any transaction, we update the 'cash' column of the database to the appropriate value (if the user's balance would become
    negative just by using cash, the balance is set to 0 and the remainder is covered by the user's card - if the user doesn't have a card, an error is given).

    - MANAGING FRIENDSHIPS:
    Whenever a friend request is sent, we insert into the friends table (with confirmed, representing if the 2 are friends, set to NULL, meaning they are not
    yet friends.).
    Whenever a friend request is accepted or denied, we update the confirmed column of the appropriate row in friends. If the request is accepted, it is set to
    1. If the request is rejected, it is set to 0. The reason we distinguish between NULL and 0 is so that we can distinguish between requests that have been
    denied, and requests that are still pending.

    - MANAGING TRANSACTIONS:
    Whenever any transaction occurs, it is added to the database. If the transaction is a donation, its message is automatically set to 'DONATION' in order to
    easily distinguish donations from other transactions. Similarly, if the transaction is a balance transfer to the bank account of the user's card number,
    the recipient_id is automatically set to 0 while the description is automatically set to 'Transferred money to bank' in order to easily distinguish
    bank transfers from other transactions. In addition to this, when the transaction history is loaded, a recipient_id of 0 automatically results in a
    recipient name of 'BANK'. We chose this because no user will ever have an ID of 0, so this simplifies our handling of bank transfers.

    - MANAGING DONATIONS:
    Whenever a donation request is created, it is added to the database. Then, when displaying donation requests, we chose the following:
        - Only display unfulfilled donation requests (those that haven't reached their goal amount).
        - Display a maximum of 50 requests. We chose this as with scale, we will not be able to show every unfulfilled donation request in the whole database.
        - To compensate for this, we created a search function so that if there is a specific unfulfilled request you wish to find, you can search for it. This
          makes use of a SQL Query that uses a regular expression and the LIKE operator.

    - MANAGING MESSAGES:



HTML:
Most HTML pages require queries from application.py to pass the appropriate information to the page and then use jinja to print the information. If the page has a form then the
information is accessed in appliation.py via the names and values of each input field, which then allows the appropriate changes to be made in the database through application.py.

    - apology.html:
    Page rendered when a function returns apology. Displays image of cat with text describing the error that lead to the apology.

    - donationresults.html:
    Page prints the results from searching for specific donations. Loads page using for loops and if statements in jinja that determine what information should be
    printed and what actions to allow the user to take. If a user makes a donation to one of the donation requests then the information is accessed in application.py
    and the appropriate data tables are updated.

    - donatiosn.html:
    Loads all existing donations using a jinja for loop to iterate over all of them and printing the appropriate information. If a donation is made then the input information
    is accessed in application.py and the appropriate tables are updated in the database.

    - donreq.html:
    Simpy displays a form for the user to fill out if they want to make a new donation request. This information gets accessed in applications.py and updates the database.

    - history.html:
    Loads all transactions in which the user is involved. Uses a for loop to iterate over all of them and prints the appropriate information.

    - index.html:
    The homepage of the website. When a user is logged in it displays the user's balance which is accessed using jinja and the users "cash" attribute. It also offers the ability to add
    a card or traansfer funds which are both forms. In either form, the information that is entered is accessed in application.py and the databases are updated accordingly. There is also
    a list of money requests and friend requests which are generated using queries in application.py and using for loops in jinja to iterate over them and print the appropriate information.
    These offer actions to accept or decline which, when clicked, will update the database accordingly. The bottom of the page has a friends table which portrays all of the user's friends'
    usernames and full names. Each has the option to message which simply redirects the user to the messages page with the indicated conversation already open.

    - layout.htl:
    Determines the main layout of the page. Offers the skeleton to which every other page simply adds information to. If the user is logged in it displays the navigation bar to all other pages.
    If no user is logged in the navigation bar only offers the login and register pages.

    - login.html:
    This page allows a user to login by asking them to input their username and password. The information is then accessed in appliation.py to check the information against the database and either
    grant the user access to the account or return an apology.

    - messages.html:
    This page displays all conversations in order of most recently active to the left of the screen. The default screen has a drop down menu with the user's friends, a text box and a "send" button
    which allows the user to indicate who they want to message and then send the message. This will then redirect to a page where this specified conversation is loaded along with all previous messages.
    If instead the user clicks "open" on one of the conversations on the left side of the apge then the website reloads with the specified conversation open on the right of the page. When a conversation
    is loaded the user will see an "Enter message here" field where they can type a new message and click "send" to send new messages. If a new message has been received the user will see it when the
    page is reloaded.

    - register.html:
    The register page is only offered if no user is logged in. It allows for a new account to be made and asks for a fullname, username and password. This information is accessed in application.py which
    verifies that all input is valid and then updates the databse accordingly, adding a new user to the users table.

    - request.html:
    This page is simply a form that offers a drop down menu with the users friends, an input text field and an amount field. This information is then accessed in application.py where it updates the transactions
    table in the database and sends the request to the specified user.

    - searchresults.html:
    This page is accessed when the user searches (via username or name) in the navigation bar and clicks "search". The page then loads results for users with similar usernames or names to that of the user's input
    by using jinja for loops and if statements to iterate over the results of a query and output the appropriate information. Each user loaded will have the option to send friend request if they are still not friends,
    "friend request pending" if the user has yet to respond to the request, or "message" if the two users are already friends. Then, application.py accessses the information and redirects to the appropriate pages
    depending on what action was taken.

    - send.html:
    This page is very similar to requests as it also is a form with a drop down menu of friends, an input text field and an amount field. The user indicated to whom they are sending money, provides an explanation or
    message, and indicated the amount they intend to send. Then, in application.py, the information is accessed and the approriate tables are updated in the database.

    - settings.html:
    This page allows the user to change their password or change the card they currently have on file. Each of these is an independent form which then passes the input information into application.py and updates the
    database accordingly.