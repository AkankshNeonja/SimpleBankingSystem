import random
import sys
import sqlite3

conn = sqlite3.connect("card.s3db")
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS card (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT,
            pin TEXT,
            balance INTEGER DEFAULT 0
            );''')


def check_luhn(card_number):
    number_of_digits = len(card_number)
    number_sum = 0
    is_second = False
    for i in range(number_of_digits - 1, -1, -1):
        d = ord(card_number[i]) - ord('0')
        if is_second:
            d = d * 2
        else:
            pass
        number_sum += d // 10
        number_sum += d % 10
        is_second = not is_second
    if number_sum % 10 == 0:
        return True
    else:
        return False


class CreditCard:
    def __init__(self):
        self.card_number = 0
        self.pin = 0
        self.balance = 0

    def generate(self):
        while True:
            self.pin = random.randint(1000, 9999)
            self.card_number = random.randint(4000000000000001, 4000009999999999)
            luhn_valid = check_luhn(str(self.card_number))
            if luhn_valid:
                cur.execute("INSERT INTO card (number,pin,balance) VALUES ({},{},{});".format(self.card_number, self.pin, self.balance))
                conn.commit()
                break
            else:
                continue


def login_menu(card):
    print("1. Balance")
    print("2. Add income")
    print("3. Do transfer")
    print("4. Close account")
    print("5. Log out")
    print("0. Exit")
    log_inp = input()
    if log_inp == "1":
        cur.execute("SELECT balance FROM card WHERE number = {};".format(card))
        data_1 = cur.fetchall()
        print(data_1[0][0])
        return True
    if log_inp == "2":
        income = int(input("Enter income:"))
        cur.execute("SELECT balance FROM card WHERE number = {};".format(card))
        data_2 = cur.fetchall()
        balance = data_2[0][0]
        balance += income
        cur.execute("UPDATE card SET balance = balance + {} WHERE number ={};".format(income, card))
        conn.commit()
        print("Income added\n")
        return True
    if log_inp == "3":
        cd_no = input("Enter card number\n")
        if cd_no == card:
            print("Cannot transfer to same account\n")
            return True
        elif not check_luhn(cd_no):
            print("Probably you made mistake in card number. Please try again\n")
            return True
        cur.execute("""SELECT number from card WHERE number={};""".format(cd_no))
        if not bool(cur.fetchone()):
            print("Such a card does not exist\n")
            return True
        else:
            transfer = int(input("Enter money to transfer\n"))
            cur.execute("SELECT balance FROM card WHERE number={};".format(card))
            data_3 = cur.fetchall()
            balance1 = data_3[0][0]
            cur.execute("SELECT balance FROM card WHERE number={};".format(cd_no))
            data_4 = cur.fetchall()
            balance2 = data_4[0][0]
            if balance1 < transfer:
                print("Not enough money!\n")
                return True
            else:
                cur.execute(f"UPDATE card SET balance = {balance2} + {transfer} WHERE number={cd_no};")
                cur.execute(f"UPDATE card SET balance = {balance1} - {transfer} WHERE number={card};")
                conn.commit()
                print("Success\n")
                return True
    if log_inp == "4":
        cur.execute("DELETE FROM card WHERE number={};".format(card))
        conn.commit()
        return True
    if log_inp == "5":
        return False
    else:
        print("Bye!")
        sys.exit()


while True:
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")
    inp = input()
    if inp == "1":
        x1 = CreditCard()
        x1.generate()
        print("Your Card has been created")
        print("Your card number:")
        print(x1.card_number)
        print("Your card PIN")
        print(x1.pin)
        continue
    elif inp == "2":
        print("Enter your card number:\n")
        inp_card = input()
        print("Enter PIN:\n")
        inp_pin = input()
        cur.execute("""SELECT * FROM card WHERE number={} AND pin={}""".format(inp_card, inp_pin))
        if bool(cur.fetchone()) is True:
            print("You have successfully logged in!\n")
            while True:
                inc = login_menu(inp_card)
                if not inc:
                    break
        else:
            print("Wrong card number or PIN!\n")
    else:
        print("Bye!\n")
        break
