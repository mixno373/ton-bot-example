# Requests for API calls and time for delay between them
import requests
import time

import asyncio
import aiogram

# We also need config and database here
import config
import db


async def start():
    # Function that is checking our wallet for new deposits and process them

    try:
        # Try to load last_lt from file
        with open('last_lt.txt', 'r') as f:
            last_lt = int(f.read())
    except FileNotFoundError:
        # If file not found, set last_lt to 0
        last_lt = 0

    while True:
        # 2 Seconds delay between checks
        await asyncio.sleep(2)

        # API call to Toncenter that returns last 100 transactions of our wallet
        resp = requests.get('https://toncenter.com/api/v2/getTransactions?'
                            f'address={config.DEPOSIT_ADDRESS}&limit=100&'
                            f'archival=true&api_key={config.API_KEY}').json()

        print(last_lt, resp)

        # If call was not successful, try again
        if not resp['ok']:
            continue

        # Iterating over transactions
        for tx in resp['result']:
            # LT is Logical Time and Hash is hash of our transaction
            lt, hash = int(tx['transaction_id']['lt']), tx['transaction_id']['hash']

            # If this transaction's logical time is lower than our last_lt,
            # we already processed it, so skip it
            if lt <= last_lt:
                continue

            # Get value of transaction (how much NanoTONs have we received)
            value = int(tx['in_msg']['value'])
            if value > 0:
                # If value is greater than 0, it is probably a new deposit and
                # we must process it by increasing someone's balance in database
                message = tx['in_msg']['message']
                print('DEPOSIT!', message, value)

            # After we processed new transaction, last_lt must be updated
            last_lt = lt
            with open('last_lt.txt', 'w') as f:
                f.write(str(last_lt))
