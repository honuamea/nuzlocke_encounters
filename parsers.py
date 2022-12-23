"""Defines html parsing classes"""

from html.parser import HTMLParser


class FormParser(HTMLParser):
    """Parses simple, depth-1 forms & the options within them into
       <obj>.forms"""
    def __init__(self):
        """FormParser constructor"""
        super().__init__()
        self._cur_form = None
        self._cur_option = None
        self._cur_value = None
        self.forms = []

    def handle_starttag(self, tag, attrs):
        """Handles <form> & <option> tags"""
        if tag == "form":
            assert self._cur_form is None, \
                "Nested forms are not supported"
            self._cur_form = {}
        elif tag == "option":
            assert self._cur_option is None, \
                "Unexpected nested option"
            self._cur_option = []
            for key, value in attrs:
                if key == "value":
                    self._cur_value = value

    def handle_endtag(self, tag):
        """Handles </form> & </option> tags"""
        if tag == "form":
            self.forms.append(self._cur_form)
            self._cur_form = None
        elif tag == "option":
            option = "".join(self._cur_option)
            self._cur_form[option] = self._cur_value
            self._cur_option = None
            self._cur_value = None

    def handle_data(self, data):
        """Handles option text"""
        if self._cur_option is None:
            return

        self._cur_option.append(data)


class TableParser(HTMLParser):
    """Parses top-level tables from html into <obj>.tables"""
    def __init__(self):
        """TableParser constructor"""
        super().__init__()
        self.depth = 0
        # _cur_* are indexed by depth
        self._cur_data = {}
        self._cur_rows = {}
        self._cur_tables = {}
        self.tables = []

    def handle_starttag(self, tag, attrs):
        """Handles <table>, <tr> & <td> tags"""
        if tag == "table":
            self.depth += 1
            self._cur_tables[self.depth] = []
        if self.depth == 0:
            return
        if tag == "tr":
            self._cur_rows[self.depth] = []
        elif tag == "td":
            self._cur_data[self.depth] = []

    def handle_endtag(self, tag):
        """Handles </table>, </tr> & </td> tags"""
        if self.depth == 0:
            # avoid ever going negative due to malformed html
            return

        if tag == "table":
            # end of table - add to class tables list
            table = self._cur_tables[self.depth]
            self.tables.append(table)
            del self._cur_tables[self.depth]
            self.depth -= 1
        elif tag == "tr":
            # end of row - add to table
            row = self._cur_rows[self.depth]
            self._cur_tables[self.depth].append(row)
            del self._cur_rows[self.depth]
        elif tag == "td":
            # end of one cell - add to row
            cell = "".join(self._cur_data[self.depth])
            self._cur_rows[self.depth].append(cell)
            del self._cur_data[self.depth]

    def handle_data(self, data):
        """Handle table data"""
        if self.depth == 0:
            # not in a table; ignore
            return

        if self.depth not in self._cur_data:
            # encountered data outside of defined cells; skip it
            return

        self._cur_data[self.depth].append(data)
