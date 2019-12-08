DOLLA

*TO USE*
Simply cd into the dolla directory, run 'flask run' in the terminal window, and follow the link of the local server given.

CONCEPT:
The website DOLLA is a website where users can send and request money between friends, donate towards other users' causes and chat via direct messages.
Users can make transactions with existing funds on their account, or they can choose to link a credit/debit card and use funds from their bank accounts.
If the user would rather move the money in their account to their bank account, they can easily transfer the funds.


DISCLAIMER:
The money used on this website is completely imaginary and, although adding a card requires a valid card number (by this, we mean that the card
number passes the Luhn Algorithm test), the website will not have access to the money in the bank accounts associated with the card number provided.


REGISTER:
The user must provide a full name, username, and password to register (confirming their password, too). If there is an error with any of these, the app renders an apology stating the error.


LOGIN:
The user enters their username and password. If there is an error with either of these, the app renders an apology stating the error.


NAVBAR:
The navigation bar contains the following links:
    - Index
    - Send money
    - Request money
    - Donations
    - Transaction History
    - Messages
    - Settings
    - Logout
There is also a search users form, which redirects to a separate page where one can send a friend request (if one is not friends with the user) or have the option to message the user (if
they are friends). If a friend request is pending, that also appears. If the user searches themselves, that will also be shown with no options.


HOMEPAGE:
The user's homepage will portray their current balance as well as the abilities to add a card (if there DOES NOT exist a card on file), transfer
funds to a bank account (if there DOES exist a card on file), respond to money requests, respond to friend requests and see a list of their friends.

    - ADD CARD:
    This function will appear in a small square window to the right of the user's current balance (if the user hasn't already added a card). It will ask the user to input their card
    number and then click the "Add" button. The card number provided will then be run through a program to verify that it is a valid card number (using Luhn's Algorithm). If the card is
    verified then the card will be added to the user's file and they will be able to send money and transfer funds directly from/to this account. If the card number is determined to be
    invalid an apology will appear on screen telling the user that the card number provided was invalid and nothing will be changed in the user's account file. The add card function will
    be available on the user's homepage as long as they have not added a card. Once a card has been added this function will be replaced with the "Transfer Funds" function (see below).

    - TRANSFER FUNDS:
    This function replaces the add card function once a card has been added to the user's account. It will ask the user for two inputs: amount and verify password. The user simply inputs
    the amount of money they would like to transfer from their account balance to their bank account and input their password. If the password is correct and the amount is less than (or
    equal to) the user's current balance, the balance will decrease by the amount indicated and the funds will go to the account of the card on file. (Note that transferring to the bank
    merely logs a transaction and changes the user's current balance, with the recipient having an ID of 0, referring to a generic bank account.) Otherwise, if the password is
    incorrect or the amount is more than the user's current balance the website will return an apology indicating what went wrong.

    - MONEY REQUESTS:
    There will be a table titled "Money Requests" which will list requests for money that the user has received (up to 20 at a time). The table will display the username of the person
    that submitted the request, the amount requested, a message explaining why and the option to accept or decline the request. If the user accepts the request the transaction will go
    through, updating the friend's balance and depleting the user's balance by the requested amount. If the user does not have enough money in their current balance, the rest will come
    from the account they have on file (if they do, indeed, have a card on file). If there is no account on file, and the user's balance is less than that of the amount requested the
    website will return an apology informing the user that they cannot afford the transaction.

    - FRIEND REQUESTS:
    There is a table titled friend requests, which lists all friend requests a user has received (if more than 15 requests are pending, it will only load the most recent 15). You have
    the option to accept or reject the friend request. If you accept the friend request, that friend will appear on your friends list (below).

    - FRIENDS LIST:
    This table will list the user's friends including their username and full name. To the right of each row is the "message" button which will redirect the user to the messages pages, opening
    their conversation with the user they indicated.


SEND:
Here one has the option to send money to friends (provided one has enough of a cash balance or one's card is on file). One must choose a friend (from a dropdown menu), provide an amount
that one is sending, and give an explanation for the transaction. If any one of these is not provided, the website renders an apology displaying the error.


REQUEST:
This page gives one the option to request money from friends. One chooses a friend (from a dropdown menu), provides the amount that you are requesting, and writes a message to explain why
one is requesting the money. If any of the fields (friend, amount or message) are left blank the website renders an apology displaying the error.


DONATIONS:

    - DONATION REQUESTS:
    There is a table of unfulfilled donation requests (a maximum of 50 are loaded, with most recent requests on top). Each donation request contains a 'goal' amount which the donation requester wants to reach. If
    that goal is reached, the donation request no longer appears in the table. For each donation request, one has the option to donate whatever amount one wants (provided one has enough
    money or their card is on file). If the donation request was submitted by the currently logged in user, there is no such option.

    - CREATE A DONATION REQUEST:
    This button redirects to a page where the user must provide a title, description, and goal amount to create their own donation request. On submission, this shows in the donation
    requests table. If any of the fields are left out or invalid, the app renders an apology.

    - SEARCH DONATION REQUESTS:
    You can imagine that with scale, you cannot load every single unfulfilled donation request. To solve this problem, there is a search feature. Search terms that are similar to the
    title or description of the request, or the username or full name of the requester, are shown in a results table. This table has all of the features of the above donation requests
    table.


TRANSACTION HISTORY:
There is a table of all transactions involving the user. This includes money that the user sent via:
    - send
    - accepting the money requests of friends
    - donations
    - transferring money from their account balance back into the bank account of their card on file. (Note that transferring to the bank merely logs a transaction and changes the user's
      current balance, with the recipient having an ID of 0, referring to a generic bank account.)
as well as money that the user received via:
    - friends sending them money
    - having their money requests accepted by friends
    - having other users donate to their causes


MESSAGES:
This page lists all of the user's conversations in order form the one that was most recently active to the one that has gone the longest with no activity. Each list item will consist of the
username of the person with whom the conversation is, the most recent message in that conversation and an "open" button that will open the conversation.When a conversation has been opened the user
will see chat box appear to the right of the conversations list. The chat box will display all messages between the users in a scrollable field. Messages which the user has sent will be in blue and
to the right while messages the user has received will be in grey to the left. At the bottom of the chat box is a text field where the user can write a new message and then press the "send" button.
The new messages will appear in the chat box, both received and sent, once the page is reloaded.


SETTINGS:
The settings page will give the user the ability to do two things: change password and change the card on file (provided the user has a card on file. If not, this option does not exist).

    - CHANGE PASSWORD:
    This function will ask the user for their current password, new password and a confirmation of the new password. The user must type something into each of these three fields or the website will
    return an apology indicating that the form wasn't filled out properly. The current password will be checked against the current password on file for the user. If the current password is determined
    to be incorrect the website will return an apology to indicate this. The new password and confirmation field must also match against each other. If what was typed in the "confirmation" field is
    different from what was typed in the "new password" field the website will return an apology to tell the user that they do not match. The website will now allow the user's new password to be the
    same as the old password. If the new password and current password match then the website will return an apology.

    - CHANGE CARD:
    This function will ask the user for a new card number and to verify their password. The card number provided will be checked (using Luhn's Algorithm) to verify that it is a valid card number. The
    password entered into the "Verify Password" field will also be checked against the user's current password. If the card provided is determined to be invalid, or if the password is determined to be
    incorrect, the website will return an apology to indicate that the user has entered invalid information. If all fields pass their cooresponding tests then the card that the user has on file will be
    changed to the new card which they have provided.


LOGOUT:
Logs a user out, redirecting to the login page.