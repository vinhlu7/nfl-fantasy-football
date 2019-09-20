import pandas as pd
from yahoo_oauth import OAuth2
import logging
import json
from json import dumps
import datetime
from twilio.rest import Client


class Yahoo_Api():
    def __init__(self,
                 consumer_key,

                 consumer_secret#,
                #access_token
                ):
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        #self._access_token = access_token
        self._authorization = None
    def _login(self):
        global oauth
        oauth = OAuth2(None, None, from_file='../auth/oauth2yahoo.json')
        if not oauth.token_is_valid():
            oauth.refresh_access_token()

class Authorize():

    def SendText(self, transaction_details):
        account_sid = 'twilio account sid'
        auth_token = 'twilio account token'
        client = Client(account_sid, auth_token)
        text_message = ''
        for transaction in transaction_details:
            if 'add' in  transaction:
                text_message += transaction['Team'] + ' Added: ' + transaction['add'] + ', '
            if 'drop' in transaction:
                text_message += transaction['Team'] + ' Dropped: ' + transaction['drop'] + '\n'

        message = client.messages \
            .create(
                body=text_message,
                from_='NUMBER',
                to='NUMBER'
            )

    def AuthorizeLeague(self):
        # UPDATE LEAGUE GAME ID
        yahoo_api._login()
        url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/380.l.XXXXXX/transactions'
        response = oauth.session.get(url, params={'format': 'json'})
        r = response.json()
        leagueObject = r['fantasy_content']['league']
        transactions = leagueObject[1]['transactions']
        first_transaction = transactions['0']['transaction']
        first_transaction_id = first_transaction[0]['transaction_id']
        with open('./LastTransaction.json') as last_transaction_file:
           last_transaction_id = json.load(last_transaction_file)

        transaction_diff = []
        #There are new transactions. Build differences
        if last_transaction_id != first_transaction_id:
            transaction_num = int(first_transaction_id) - int(last_transaction_id)
            for x in range(transaction_num):
                transaction_details = transactions[str(x)]['transaction'][1]
                transactions_players_info = {}
                if len(transaction_details) > 0:
                    for count in range(transaction_details['players']['count']):
                        #Add object is array, Drop is dict. Weird.
                        if isinstance(transaction_details['players'][str(count)]['player'][1]['transaction_data'], list):
                            add_or_drop = transaction_details['players'][str(count)]['player'][1]['transaction_data'][0]['type']
                            by_who =  transaction_details['players'][str(count)]['player'][1]['transaction_data'][0]['destination_team_name']
                        else:
                            add_or_drop = transaction_details['players'][str(count)]['player'][1]['transaction_data']['type']
                            by_who = transaction_details['players'][str(count)]['player'][1]['transaction_data']['source_team_name']

                        transactions_players_info[str(add_or_drop)] = transaction_details['players'][str(count)]['player'][0][2]['name']['full']
                        transactions_players_info['Team'] = by_who

                    transaction_diff.append(transactions_players_info)

            with open('LastTransaction.json', 'w') as last_transaction_file:
                json.dump(first_transaction_id, last_transaction_file)

        last_transaction_file.close()
        if len(transaction_diff) > 0:
           self.SendText(transaction_diff)

        return; 

def main():
##### Get Yahoo Auth ####

    # Yahoo Keys
    with open('../auth/oauth2yahoo.json') as json_yahoo_file:
        auths = json.load(json_yahoo_file)
    yahoo_consumer_key = auths['consumer_key']
    yahoo_consumer_secret = auths['consumer_secret']
    #yahoo_access_token = auths['access_token']
    #yahoo_access_secret = auths['access_token_secret']
    json_yahoo_file.close()

#### Declare Yahoo Variable ####

    global yahoo_api
    yahoo_api = Yahoo_Api(yahoo_consumer_key,
                            yahoo_consumer_secret,
                            #yahoo_access_token,
                            #yahoo_access_secret)
                                )
#### Where the magic happen ####
    bot = Bot(yahoo_api)
    bot.run()

class Bot():
    def __init__(self, yahoo_api):

        self._yahoo_api = yahoo_api

    def run(self):
        # Data Updates
        at = Authorize()
        at.AuthorizeLeague()
        print('Authorization Complete')

if __name__ == "__main__":
    main()
