import tkinter as tk

from ui import tk_color
from ui.utilities.font import Font
from ui.utilities.markdown import MarkdownState


def tag_name(line_number, segment_number):
    return f"tag_{line_number}_{segment_number}"


class MDTextV2(tk.Text):
    def __init__(self, parent, markdown, colors, *args, padding=0, **kwargs):
        super().__init__(parent, wrap=tk.WORD, selectbackground=tk_color(colors[3]), *args, **kwargs)
        self.markdown = markdown
        self.colors = colors

        for line_number, line in enumerate(self.markdown.parsed):
            for segment_number, (text, markdown_state) in enumerate(line):
                if segment_number == len(line) - 1 and line_number < len(self.markdown.parsed) - 1:
                    text += "\n"

                self.insert(tk.END, text, tag_name(line_number, segment_number))

                size = markdown_state.size
                weight = "bold" if MarkdownState.BOLD in markdown_state else "normal"
                slant = "italic" if MarkdownState.ITALIC in markdown_state else "roman"
                font, font_spacing = Font.create_font(size, weight, slant)
                color = tk_color(self.colors[1]) \
                    if (MarkdownState.INLINE_CODE not in markdown_state and
                        MarkdownState.MULTILINE_CODE not in markdown_state) else tk_color(self.colors[2])

                spacing_above = padding if line_number == 0 and segment_number == 0 else font_spacing

                self.tag_config(tag_name(line_number, segment_number), font=font, foreground=color,
                                spacing1=spacing_above)

        self.config(state=tk.DISABLED)

    @property
    def pixel_height(self):
        return self.count("1.0", tk.END, "ypixels")[0]
