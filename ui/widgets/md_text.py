import tkinter as tk

from ui import tk_color
from ui.utilities.font import Font
from ui.utilities.markdown import MarkdownState
from ui.widgets.scroll_bound_canvas import ScrollBoundCanvas


class MDText(ScrollBoundCanvas):
    def __init__(self, parent, markdown, colors, line_spacing=1, header_spacing=0.25, outer_padding=16,
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.markdown = markdown
        self.colors = colors
        self.line_spacing = line_spacing
        self.header_spacing = header_spacing
        self.outer_padding = outer_padding
        self.preferred_height = 0

        self.bind("<Configure>", lambda config_event: self.refresh(config_event))

    def refresh(self, config_event):
        self.delete(tk.ALL)

        self.xview_moveto(0)
        self.yview_moveto(0)

        y = self.outer_padding
        total_width = config_event.width

        first_line = True
        for line in self.markdown.parsed:
            x = self.outer_padding
            max_height = 0
            first_chunk = True
            for text, markdown_state in line:
                size = markdown_state.size
                weight = "bold" if MarkdownState.BOLD in markdown_state else "normal"
                slant = "italic" if MarkdownState.ITALIC in markdown_state else "roman"
                font, font_spacing = Font.create_font(size, weight, slant)
                color = tk_color(self.colors[1])\
                    if (MarkdownState.INLINE_CODE not in markdown_state and
                        MarkdownState.MULTILINE_CODE not in markdown_state) else tk_color(self.colors[2])

                height = Font.metrics(font, self, "linespace")
                space_width = Font.measure(font, self, " ")

                if first_chunk and (not first_line) and markdown_state.size > 0:
                    y += height * self.header_spacing
                first_chunk = False
                first_line = False

                if height > max_height:
                    max_height = height

                for word in text.split(" "):
                    width = Font.measure(font, self, word)

                    if x != self.outer_padding and x + width > total_width - self.outer_padding:
                        x = self.outer_padding
                        y += max_height * self.line_spacing

                    self.create_text(x, y, text=word, font=font.value if isinstance(font, Font) else font,
                                     anchor=tk.NW, justify=tk.LEFT, fill=color)
                    x += width + space_width

                x -= space_width

            y += max_height * self.line_spacing

        self.preferred_height = y + self.outer_padding
        self.config(height=self.preferred_height)
        self.config(scrollregion=(0, 0, total_width, self.preferred_height))
