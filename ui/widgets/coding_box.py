import _tkinter
import tkinter as tk

from ui.utilities.font import Font
from ui.widgets.automatic_hide_scrollbar import AutomaticHideScrollbar


class CodeBox(tk.Frame):

    def __init__(self, parent, coding_page):
        super().__init__(parent)
        self.coding_page = coding_page

        self.do_not_overwrite_file = False

        self.text_box = CodeBox.TextWithModifiedCallback(self, wrap=tk.NONE, font=Font.NORMAL,
                                                         tabs=(Font.measure(Font.NORMAL, self, ' ' * 2),),
                                                         highlightthickness=0)
        self.text_box.grid(row=0, column=0, sticky=tk.NSEW)
        self.scroll_v = AutomaticHideScrollbar(self, orient=tk.VERTICAL, command=self.text_box.yview)
        self.scroll_v.grid(row=0, column=1, sticky=tk.NSEW)
        self.scroll_h = AutomaticHideScrollbar(self, orient=tk.HORIZONTAL, command=self.text_box.xview)
        self.scroll_h.grid(row=1, column=0, sticky=tk.NSEW)
        self.text_box.config(yscrollcommand=self.scroll_v.set, xscrollcommand=self.scroll_h.set)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.text_box.bind("<Return>", self.enter)
        self.text_box.bind('}', self.close_brace)

        self.text_box.bind("<<TextModified>>", self.save)

    def current_indentation(self):
        text = self.text_box.get("0.0", tk.INSERT)
        indentation = 0
        for line in text.split('\n'):
            indentation += line.split("//")[0].count('{') - line.split("//")[0].count('}')
        return indentation

    def character_before_cursor(self):
        return self.text_box.get("insert - 1 char", tk.INSERT)

    def enter(self, *_):
        self.text_box.insert(tk.INSERT, '\n' + '\t' * self.current_indentation())
        return "break"

    def close_brace(self, *_):
        if self.character_before_cursor() == '\t':
            self.text_box.delete("insert - 1 char", tk.INSERT)

    def load_file(self):
        self.do_not_overwrite_file = True
        file_path = self.coding_page.code_file_path
        with open(file_path, 'r') as file:
            self.write_value(file.read())
        self.do_not_overwrite_file = False

    def write_value(self, text):
        self.text_box.delete("0.0", tk.END)
        self.text_box.insert(tk.END, text)

    def save(self, *_):
        if not self.do_not_overwrite_file:
            file_path = self.coding_page.code_file_path
            file = open(file_path, 'w')
            file.flush()
            file.write(self.text)
            file.close()

    @property
    def text(self):
        text = self.text_box.get("0.0", "end")
        if len(text) > 0 and text[-1] == '\n':
            text = text[:-1]
        return text

    class TextWithModifiedCallback(tk.Text):
        # noinspection PyUnresolvedReferences
        def __init__(self, *args, **kwargs):
            tk.Text.__init__(self, *args, **kwargs)

            self._orig = self._w + "_orig"
            self.tk.call("rename", self._w, self._orig)
            self.tk.createcommand(self._w, self._proxy)

        def _proxy(self, command, *args):
            cmd = (self._orig, command) + args

            if command in ("insert", "delete", "replace"):
                pass

            try:
                result = self.tk.call(cmd)
            except _tkinter.TclError:
                return

            if command in ("insert", "delete", "replace"):
                self.event_generate("<<TextModified>>")

            return result
