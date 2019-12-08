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