from helper import Gemini_Helper
from twilio.rest import TwilioRestClient
import json
import time

def print_status(amount, type, price, total):
    print("You have " + str(amount) + " " +
           type + " at $" + str(price) + " per " +
           type + " for a total of $" + str(round(total, 2)))

def loop():
    global helper
    helper.update_all()
    print_status(helper.portfolio['BTC'], "bitcoin", helper.prices['BTC'], helper.totals['BTC'])
    print_status(helper.portfolio['ETH'], "ethereum", helper.prices['ETH'], helper.totals['ETH'])
    print("")

def send_text(check_text_sent=True, message="Something went wrong on the trading script. You should probably check it out."):
    global text_sent
    # we don't want to spam my Twilio account and run out of money - one text will do
    if not text_sent or not check_text_sent:
    	with open('twilio.json', 'rb') as f:
    		twilio_dict = json.load(f)
        client = TwilioRestClient(twilio_dict['sid'], twilio_dict['token'])
        message = client.messages.create(
		    to=twilio_dict['to_number'], 
		    from_=twilio_dict['from_number'],
		    body=message)
        print(message.sid)
        text_sent = True


def sell_test():
    global helper
    helper.sell('BTC', '0.00001', '9999.99')
    helper.sell('ETH', '0.001', '9999.99')

def main():
    global text_sent
    global helper
    text_sent = False
    helper = Gemini_Helper()

    while True:
        try:
            loop()
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