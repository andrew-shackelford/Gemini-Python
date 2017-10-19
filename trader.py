from helper import Gemini_Helper
from twilio.rest import TwilioRestClient
import json
import time
import datetime

MAX_PRICE_SELL_PERCENTAGE = 0.95
BITCOIN_SELL_PRICE = 5000
ETHEREUM_SELL_PRICE = 250

def print_status(amount, type, price, total):
    print("You have " + str(amount) + " " +
           type + " at $" + str(price) + " per " +
           type + " for a total of $" + str(round(total, 2)))

def print_sell_status():
    bitcoin_percentage = helper.prices['BTC']/ helper.max_prices['BTC']
    ethereum_percentage = helper.prices['ETH'] / helper.max_prices['ETH']
    print("Bitcoin is at " + str(round(bitcoin_percentage * 100, 2)) + "% compared to our max percentage of " + str(MAX_PRICE_SELL_PERCENTAGE * 100) + "%")
    print("Ethereum is at " + str(round(ethereum_percentage * 100, 2)) + "% compared to our max percentage of " + str(MAX_PRICE_SELL_PERCENTAGE * 100) + "%")

    bitcoin_would_sell = str(round(max(MAX_PRICE_SELL_PERCENTAGE*helper.max_prices['BTC'], BITCOIN_SELL_PRICE), 2))
    ethereum_would_sell = str(round(max(MAX_PRICE_SELL_PERCENTAGE*helper.max_prices['ETH'], ETHEREUM_SELL_PRICE), 2))
    print("Bitcoin would sell at $" + bitcoin_would_sell + " but it is currently at $" + str(round(helper.prices['BTC'], 2)))
    print("Ethereum would sell at $" + ethereum_would_sell + " but it is currently at $" + str(round(helper.prices['ETH'], 2)))

def send_text(honor_text_sent=True, message="Something went wrong on the trading script. You should probably check it out."):
    global text_sent
    # we don't want to spam my Twilio account and run out of money - one text will do
    if not text_sent or not honor_text_sent:
        try:
            with open('twilio.json', 'rb') as f:
                twilio_dict = json.load(f)
            client = TwilioRestClient(twilio_dict['sid'], twilio_dict['token'])
        except:
            print("Client failed to load")
        try:
            message = client.messages.create(
                to=twilio_dict['to_number'], 
                from_=twilio_dict['from_number'],
                body=message)
            print(message.sid)
            text_sent = True
        except:
            print("Message failed to send")

def sell_test():
    global helper
    helper.sell('BTC', '0.00001', '9999.99')
    helper.sell('ETH', '0.001', '9999.99')

def check_sell_status():
    """
    we will sell everything if the price of bitcoin goes below our hard sell prices or
    a certain percentage of the max price it has ever reached.
    hopefully, this will help us avoid the effects of a crash.
    """
    bitcoin_percentage = helper.prices['BTC']/ helper.max_prices['BTC']
    ethereum_percentage = helper.prices['ETH'] / helper.max_prices['ETH']
    if helper.prices['BTC'] < BITCOIN_SELL_PRICE and helper.portfolio['BTC'] > 0:
        sell_str = "The price of bitcoin dropped below our sell price of $" + str(BITCOIN_SELL_PRICE) + ", so we sold everything."
        print(sell_str)
        send_text(False, sell_str)
        result = helper.sell_all('BTC')
        send_text(False, str(result))
    if helper.prices['ETH'] < ETHEREUM_SELL_PRICE and helper.portfolio['ETH'] > 0:
        sell_str = "The price of ethereum dropped below our sell price of $" + str(ETHEREUM_SELL_PRICE) + ", so we sold everything."
        print(sell_str)
        send_text(False, sell_str)
        result = helper.sell_all('ETH')
        send_text(False, str(result))
    if bitcoin_percentage < MAX_PRICE_SELL_PERCENTAGE and helper.portfolio['BTC'] > 0:
        sell_str = "The price of bitcoin dropped below our sell percentage of " + str(MAX_PRICE_SELL_PERCENTAGE * 100) + "%, so we sold everything."
        print(sell_str)
        send_text(False, sell_str)
        result = helper.sell_all('BTC')
        send_text(False, str(result))
    if  ethereum_percentage < MAX_PRICE_SELL_PERCENTAGE and helper.portfolio['ETH'] > 0:
        sell_str = "The price of ethereum dropped below our sell percentage of " + str(MAX_PRICE_SELL_PERCENTAGE * 100) + "%, so we sold everything."
        print(sell_str)
        send_text(False, sell_str)
        result = helper.sell_all('ETH')
        send_text(False, str(result))

def loop():
    # update everything
    global helper
    helper.update_all()

    # print out the prices
    print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
    print_status(helper.portfolio['BTC'], "bitcoin", helper.prices['BTC'], helper.totals['BTC'])
    print_status(helper.portfolio['ETH'], "ethereum", helper.prices['ETH'], helper.totals['ETH'])

    # check whether we should sell and print the statuses
    check_sell_status()
    print_sell_status()

    # print a new line so it looks pretty :)
    print("")

def main():
    global text_sent
    global helper
    text_sent = False
    helper = Gemini_Helper()
    last_status_text_sent = time.time()
    FOUR_HOURS = 60*60*4

    while True:
        try:
            loop()
            if text_sent:
                send_text(False, "And we're back up! Whatever went wrong is fixed.")
            if time.time() - last_status_text_sent > FOUR_HOURS:
                send_text(False, "All good here! Bitcoin trading script is up and running.")
                last_status_text_sent = time.time()
            text_sent = False
            time.sleep(10)
        except KeyboardInterrupt:
            raise
        except:
            """
            we really do not want this to fail and stop running,
            so the whole thing is going into a try-except loop in case
            the API goes down momentarily or something.
            we're also gonna send a text so I can know and figure out
            what's going on.
            """
            print("SOMETHING WENT WRONG")
            send_text()
            time.sleep(10)



if __name__ == "__main__":
    main()