DOLLA'S DESIGN

FRAMEWORK:
We largely used Flask, and adopted the skeleton of Finance. For our database, we used SQLite3, contained in data.db. In just one case, we made use of
JavaScript, and otherwise made our pages interactive using Jinja.

DATABASE:
The database (data.db) manages the storing and organization of all kinds of data including user data, transactions, friendships, messages and donation request posts.
This was done using 7 tables total which include:

    - convos (conversations):
    Whenever a friendship is confirmed a new entry was made to create a conversation between the two users involved in the friendship. This included the user id for each
    user (foreign key referencing the users table) and a unique id for the conversation itself.

    - donation_reqs (donation requests):


    - donations (donation transactions):


    - friends (friendship status between users):


    - messages (all messages):


    - transactions (all transactions):


    - users (user information)



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