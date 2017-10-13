from helper import Gemini_Helper
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

def main():
    global helper
    helper = Gemini_Helper()

    while True:
        loop()
        time.sleep(10)

if __name__ == "__main__":
    main()