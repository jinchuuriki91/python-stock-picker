#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
from datetime import datetime
from statistics import mean, stdev


DATE_FORMAT = "%d-%b-%Y"
MAX_RETRY = 3
DECIMAL_PRECISION = 3
MSG_NEG_DATE = "Please enter date as DD/MMM/YYYY eg 20-Jan-2019\n"


class Record:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return "<%s: %s (%s)>" % (
            self.name, self.data.get("StockDate", None), self.price)

    @property
    def name(self):
        return self.data.get("StockName", "")

    @property
    def date(self):
        date = self.data.get("StockDate", False)
        return datetime.strptime(date, DATE_FORMAT) if date else None

    @property
    def price(self):
        return float(self.data.get("StockPrice", "0.000"))


class RecordSet:

    def __init__(self, data):
        self._arr = data

    def __repr__(self):
        return "<RecordSet: %s>" % self._arr

    @property
    def empty(self):
        return False if self._arr else True

    def get(self, name):
        return RecordSet([x for x in self._arr if x.name == name]).order()

    def order(self, desc=False, by_price=False):
        if by_price:
            return RecordSet(
                sorted(self._arr, key=lambda x: x.price, reverse=desc))
        else:
            return RecordSet(
                sorted(self._arr, key=lambda x: x.date, reverse=desc))

    def filter(self, start_date, end_date):
        _f = filter(
            lambda x: x.date >= start_date and x.date <= end_date, self._arr)
        return RecordSet([x for x in _f])

    @property
    def mean(self):
        return round(mean([x.price for x in self._arr]), DECIMAL_PRECISION)

    @property
    def stdev(self):
        return round(stdev([x.price for x in self._arr]), DECIMAL_PRECISION)

    def buy_sell(self):
        rs = self.order(by_price=True)
        b = rs._arr[0]
        s = rs._arr[-1]
        return {
            "buy_date": b.data.get("StockDate", None),
            "sell_date": s.data.get("StockDate", None),
            "profit": round((s.price - b.price) * 100, DECIMAL_PRECISION)
        }


def read_file(path):
    try:
        with open(path, "r") as fp:
            reader = csv.DictReader(fp)
            res = [Record(x) for x in reader]
            return res
    except FileNotFoundError as exc:
        raise exc


def main(buffer):
    record_set = RecordSet(buffer)
    try:
        while True:
            name = input("Welcome Agent! Which stock you need to process?:-  ")
            rs = record_set.get(name)
            if rs.empty:
                print("Stock not found, try again ...\n")
            else:
                sd_idx = 0
                ed_idx = 0
                start_date = end_date = None
                while sd_idx < MAX_RETRY:
                    sd_input = input("From which date you want to start:-  ")
                    try:
                        start_date = datetime.strptime(sd_input, DATE_FORMAT)
                        break
                    except ValueError:
                        print(MSG_NEG_DATE)
                        sd_idx += 1
                if start_date is None:
                    print("Too many retries ... exiting.")
                    exit(0)
                while ed_idx < MAX_RETRY:
                    ed_input = input("Till which date you want to analyze:-  ")
                    try:
                        end_date = datetime.strptime(ed_input, DATE_FORMAT)
                        break
                    except ValueError:
                        print(MSG_NEG_DATE)
                        ed_idx += 1
                if end_date is None:
                    print("Too many retries ... exiting.")
                    exit(0)
                elif start_date > end_date:
                    print("Start date cannot be greater than end date")
                else:
                    rec_fil = rs.filter(start_date, end_date)
                    bs = rec_fil.buy_sell()
                    print('"Here is you result":-  Mean: %s, Std: %s, Buy date: %s, Sell date: %s, Profit: %s' % (rec_fil.mean, rec_fil.stdev, bs.get("buy_date", ""), bs.get("sell_date", ""), bs.get("profit", "")))  ## noqa

                    repeat = input("Do you want to continue? (y or n):-")
                    if repeat != 'y':
                        exit(0)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    try:
        path = sys.argv[1]
        main(read_file(path))
    except (IndexError, FileNotFoundError):
        print("File not found")
        exit(0)
