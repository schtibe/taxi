import re
import string
import datetime

from models import Entry

class ParseError(Exception):
    pass

class Parser:
    def process_line(self, line, line_number):
        pass

    def parse(self):
        file = open(self.file, 'r')
        line_number = 0

        for line in file:
            line_number += 1
            self.lines[line_number] = {'text': line, 'entry': None}
            self.process_line(line, line_number)

        file.close()

    def __init__(self, file):
        self.file = file
        self.entries = {}
        self.lines = {}

class TaxiParser(Parser):
    def process_date(self, date_matches):
        if len(date_matches.group(3)) == 2:
            current_year = datetime.date.today().year
            current_millennium = current_year - (current_year % 1000)
            year = current_millennium + int(date_matches.group(3))
        else:
            year = int(date_matches.group(3))

        self.date = datetime.date(year, int(date_matches.group(2)), int(date_matches.group(1)))

    def process_line(self, line, line_number):
        line = line.strip()

        if len(line) == 0 or line[0] == '#':
            return

        date_matches = re.match('(\d{1,2})\D(\d{1,2})\D(\d{4}|\d{2})', line)

        if date_matches is not None:
            self.process_date(date_matches)
        else:
            self.process_entry(line, line_number)

    def process_entry(self, line, line_number):
        splitted_line = string.split(s = line, maxsplit = 2)

        if len(splitted_line) == 0:
            return
        elif len(splitted_line) != 3:
            raise ParseError('Line #%s is not correctly formatted' % line_number)

        time = re.match(r'(\d{2}):(\d{2})-(?:(?:(\d{2}):(\d{2}))|\?)', splitted_line[1])

        if time is not None:
            time_start = datetime.datetime(self.date.year, self.date.month, self.date.day, int(time.group(1)), int(time.group(2)))

            if time.group(3) is not None and time.group(4) is not None:
                time_end = datetime.datetime(self.date.year, self.date.month, self.date.day, int(time.group(3)), int(time.group(4)))
                total_time = time_end - time_start
                total_hours = total_time.seconds / 3600.0
            else:
                total_hours = 0
        else:
            try:
                total_hours = float(splitted_line[1])
            except ValueError:
                raise ParseError('Line #%s is not correctly formatted' % line_number)

        if not self.date in self.entries:
            self.entries[self.date] = []

        new_entry = Entry(self.date, splitted_line[0], total_hours, splitted_line[2])
        self.entries[self.date].append(new_entry)
        self.lines[line_number]['entry'] = new_entry

    def update_file(self):
        file = open(self.file, 'w')

        for line in self.lines.itervalues():
            text = line['text']

            if line['entry'] is not None and line['entry'].pushed:
                text = '# %s' % text

            file.write(text)

        file.close()