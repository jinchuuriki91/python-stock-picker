#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
from datetime import datetime


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
        return datetime.strptime(date, "%d-%b-%Y") if date else None

    @property
    def price(self):
        return self.data.get("StockPrice", 0.000)


class RecordSet:

    def __init__(self, data):
        self._arr = data

    def __repr__(self):
        return "<RecordSet: %s>" % self._arr

    def get(self, name):
        return RecordSet([x for x in self._arr if x.name == name])

    def order_by_date(self, desc=False):
        return sorted(self._arr, key=lambda x: x.date, reverse=desc)


def read_file(path):
    with open(path, "r") as fp:
        reader = csv.DictReader(fp)
        res = [Record(x) for x in reader]
        return res


def main(buffer):
    record_set = RecordSet(buffer)
    rs = record_set.get("AICIXE")
    print(rs.order_by_date())


if __name__ == "__main__":
    try:
        path = sys.argv[1]
        main(read_file(path))
    except IndexError:
        print("File not found")
        exit(0)
