"""
 https://docs.python.org/2/library/csv.html#examples
"""

import csv
import codecs
import cStringIO


def _utf8_recoder(f, encoding):
    reader = codecs.getreader(encoding)(f)
    return (l.encode("utf-8") for l in reader)


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = _utf8_recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.row_len = 0

    def next(self):
        new_row = self.reader.next()
        while len(new_row) < self.row_len:
            next_row = self.reader.next()

            # Concat with next line when row is incomplete
            new_row = new_row[:-1]+['\n'.join((new_row[-1], next_row[0]))]+next_row[1:]

        self.row_len = len(new_row)

        return [unicode(s, "utf-8") for s in new_row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and re-encode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):  # pragma: no cover
        for row in rows:
            self.writerow(row)
