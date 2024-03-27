from config import load_config
from connect import connection
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse


def new_account(parameters: dict):
    first_name = parameters['given-name']
    last_name = parameters['last-name']
    dob = parameters['date']
    dob_date = dob.split('T')[0]
    PIN = parameters['number']
    PIN = int(PIN)

    if len(str(PIN)) == 4:
        # Connect to bankingbot database
        config = load_config()
        cnx = connection(config)
        cursor = cnx.cursor()

        # Update database with new user information (initialize balance to 0)
        query = ('INSERT INTO accountholder (first_name, last_name, date_of_birth, pin) VALUES (%s, %s, %s, %s);')
        cursor.execute(query, (first_name, last_name, dob_date, PIN))

        # Make sure both tables in database have a new entry. ID's MUST match! ID in accountholder is automatic. ID in accountinfo is NOT!
        query = ('SELECT id FROM accountholder WHERE first_name = %s and last_name = %s and pin = %s;')
        cursor.execute(query, (first_name, last_name, PIN))
        id = cursor.fetchone()
        query = ('INSERT INTO accountinfo (id, balance, num_deposit, num_withdrawal) VALUES (%s, %s, %s, %s);')
        cursor.execute(query, (id, 0, 0, 0))
        cnx.commit()
        cursor.close()
        cnx.close()
        return JSONResponse(content={'fulfillmentText':f'Thank you for creating a new account with us {first_name} {last_name}. How else can I assist you today? You can say "new account" or "existing account."'})
    else:
        #
        # Below comments need to be updated. How to force user to make only 4-digit pin???
        #

        # response_parameters = {
        #     'last_name':last_name,
        #     'first_name':first_name,
        #     'date':dob
        # }
        # response_payload = {
        #     'fulfillmentText':'Your PIN must be exactly 4-digits. Please re-enter your PIN.',
        #     'outputContexts':[
        #         {
        #             'parameters':response_parameters
        #         }
        #     ]
        # }
        return JSONResponse(content={'fulfillmentText':'Your PIN must be exactly 4-digits. Please re-enter your PIN.'})
        # return JSONResponse(content=response_payload)


def account_login(parameters: dict):
    dob = parameters['date']
    dob_date = dob.split('T')[0]
    PIN = parameters['number']
    PIN = int(PIN)

    # Connect to bankingbot database
    config = load_config()
    cnx = connection(config)
    cursor = cnx.cursor()

    # Update database with new user information (initialize balance to 0)
    query = ('SELECT first_name, last_name FROM accountholder WHERE date_of_birth=%s AND pin=%s;')
    cursor.execute(query, (dob_date, PIN))
    response = cursor.fetchone()
    # Need to put check here for only one row of data returned. What if there are two+ people with the same pin and dob??
    first_name = response[0]
    last_name = response[1]

    # Handle error on query here.
    # If no error, proceed.
    # If error, let user know information didn't match and to try again.

    credentials = {
        'first_name':first_name,
        'last_name':last_name,
        'date_of_birth':dob_date,
        'pin':PIN
    }

    cursor.close()
    cnx.close()
    # return JSONResponse and dictionary of parameters
    msg = JSONResponse(content={'fulfillmentText':f'You are successfully logged in {first_name} {last_name}. Would you like to deposit or withdraw money, or check your balance?'})
    return msg, credentials


def account_balance(parameters: dict):
    first_name = parameters['first_name']
    last_name = parameters['last_name']
    dob = parameters['date_of_birth']
    dob_date = dob.split('T')[0]
    PIN = parameters['pin']
    PIN = int(PIN)
    
    # Connect to bankingbot database
    config = load_config()
    cnx = connection(config)
    cursor = cnx.cursor()

    query = ('SELECT balance FROM accountholder h LEFT JOIN accountinfo i ON h.id=i.id WHERE pin=%s and first_name=%s and last_name=%s;')
    cursor.execute(query, (PIN, first_name, last_name))
    balance = cursor.fetchone()
    cursor.close()
    cnx.close()

    msg = JSONResponse(content={'fulfillmentText':f'Your current balance is ${balance}. Thank you {first_name} {last_name}. What else can I do for you?'})
    return msg


def account_withdrawal(parameters: dict):
    first_name = parameters['first_name']
    last_name = parameters['last_name']
    dob = parameters['date_of_birth']
    dob_date = dob.split('T')[0]
    PIN = parameters['pin'] # <--- This and PIN need to be figured out. They can't share the same name ('number')
    PIN = int(PIN)
    amount = parameters['withdrawal'] # <--- This and PIN need to be figured out. They can't share the same name ('number')

    # Connect to bankingbot database
    config = load_config()
    cnx = connection(config)
    cursor = cnx.cursor()

    query = ('SELECT balance FROM accountholder h LEFT JOIN accountinfo i ON h.id=i.id WHERE pin=%s and first_name=%s and last_name=%s;')
    cursor.execute(query, (PIN, first_name, last_name))
    balance = cursor.fetchone()[0]

    if amount <= balance:
        new_balance = balance - amount
        query = ('UPDATE accountinfo SET balance = %s WHERE id = (SELECT id FROM accountholder WHERE first_name = %s AND last_name = %s AND pin = %s);')
        cursor.execute(query, (new_balance, first_name, last_name, PIN))

        query = ('UPDATE accountinfo SET num_withdrawal = num_withdrawal+1 WHERE id = (SELECT id FROM accountholder WHERE first_name = %s AND last_name = %s AND pin = %s);')
        cursor.execute(query, (first_name, last_name, PIN))

        msg = JSONResponse(content={'fulfillmentText':f'Your withdrawal of ${amount} has been completed. How else can I assist you?'})
    else:
        msg = JSONResponse(content={'fulfillmentText':f'You do not have enough money for this withdrawal. Your current balance is ${balance} How else can I assist you?'})

    cnx.commit()
    cursor.close()
    cnx.close()
    return msg


def account_deposit(parameters: dict):
    first_name = parameters['first_name']
    last_name = parameters['last_name']
    dob = parameters['date_of_birth']
    dob_date = dob.split('T')[0]
    PIN = parameters['pin'] # <--- This and PIN need to be figured out. They can't share the same name ('number')
    PIN = int(PIN)
    amount = parameters['deposit'] # <--- This and PIN need to be figured out. They can't share the same name ('number')

    # Connect to bankingbot database
    config = load_config()
    cnx = connection(config)
    cursor = cnx.cursor()

    query = ('SELECT balance FROM accountholder h LEFT JOIN accountinfo i ON h.id=i.id WHERE pin=%s and first_name=%s and last_name=%s;')
    cursor.execute(query, (PIN, first_name, last_name))
    balance = cursor.fetchone()[0]

    new_balance = balance + amount
    query = ('UPDATE accountinfo SET balance = %s WHERE id = (SELECT id FROM accountholder WHERE first_name = %s AND last_name = %s AND pin = %s);')
    cursor.execute(query, (new_balance, first_name, last_name, PIN))

    query = ('UPDATE accountinfo SET num_deposit = num_deposit+1 WHERE id = (SELECT id FROM accountholder WHERE first_name = %s AND last_name = %s AND pin = %s);')
    cursor.execute(query, (first_name, last_name, PIN))

    cnx.commit()
    cursor.close()
    cnx.close()
    msg = JSONResponse(content={'fulfillmentText':f'You have deposited ${amount} into your account. How else may I assist you today?'})
    return msg