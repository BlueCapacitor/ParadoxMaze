from enum import Flag, auto


class Markdown:
    def __init__(self, raw):
        self.raw = raw
        self.parsed = [[]]

        raw = "\n" + raw
        self.markdown_state = MarkdownState.NORMAL
        self.buffer = ""
        i = 0
        while i < len(raw):
            next_chars = (MarkdownState.INLINE_CODE in self.markdown_state or
                          MarkdownState.MULTILINE_CODE in self.markdown_state,) + \
                         tuple(raw[i + j] if i + j < len(raw) else None for j in range(6))
            match next_chars:
                case False, '\n', '#', '#', '#', ' ', _:
                    self.flush_buffer()
                    self.markdown_state &= ~MarkdownState.SIZE_BIT1
                    self.markdown_state |= MarkdownState.SIZE_BIT2
                    if len(self.parsed) > 0 and len(self.parsed[-1]) > 0:
                        self.parsed.append(list())
                    i += 5
                case False, '\n', '#', '#', ' ', _, _:
                    self.flush_buffer()
                    self.markdown_state |= MarkdownState.SIZE_BIT1
                    self.markdown_state &= ~MarkdownState.SIZE_BIT2
                    if len(self.parsed) > 0 and len(self.parsed[-1]) > 0:
                        self.parsed.append(list())
                    i += 4
                case False, '\n', '#', ' ', _, _, _:
                    self.flush_buffer()
                    self.markdown_state |= MarkdownState.SIZE_BIT1 | MarkdownState.SIZE_BIT2
                    if len(self.parsed) > 0 and len(self.parsed[-1]) > 0:
                        self.parsed.append(list())
                    i += 3
                case False, '\n', '\n', '#', '#', '#', ' ':
                    self.flush_buffer()
                    self.markdown_state &= ~MarkdownState.SIZE_BIT1
                    self.markdown_state |= MarkdownState.SIZE_BIT2
                    if len(self.parsed) > 0 and len(self.parsed[-1]) > 0:
                        self.parsed.append(list())
                    i += 6
                case False, '\n', '\n', '#', '#', ' ', _:
                    self.flush_buffer()
                    self.markdown_state |= MarkdownState.SIZE_BIT1
                    self.markdown_state &= ~MarkdownState.SIZE_BIT2
                    if len(self.parsed) > 0 and len(self.parsed[-1]) > 0:
                        self.parsed.append(list())
                    i += 5
                case False, '\n', '\n', '#', ' ', _, _:
                    self.flush_buffer()
                    self.markdown_state |= MarkdownState.SIZE_BIT1 | MarkdownState.SIZE_BIT2
                    if len(self.parsed) > 0 and len(self.parsed[-1]) > 0:
                        self.parsed.append(list())
                    i += 4
                case True, '\n', _, _, _, _, _:
                    assert MarkdownState.INLINE_CODE not in self.markdown_state, "Unclosed inline code"
                    self.flush_buffer()
                    self.parsed.append(list())
                    i += 1
                case False, '\n', '\n', _, _, _, _:
                    self.flush_buffer()
                    self.markdown_state &= ~(MarkdownState.SIZE_BIT1 | MarkdownState.SIZE_BIT2)
                    if len(self.parsed) > 0 and len(self.parsed[-1]) > 0:
                        self.parsed.append(list())
                    i += 2
                case False, '\n', _, _, _, _, _:
                    if len(self.parsed) > 0 and self.markdown_state.size != 0:
                        self.flush_buffer()
                        self.parsed.append(list())
                        self.markdown_state &= ~(MarkdownState.SIZE_BIT1 | MarkdownState.SIZE_BIT2)
                    elif len(self.buffer) > 0 and self.buffer[-1] != " ":
                        self.buffer += " "
                    elif len(self.parsed) == 1 and len(self.parsed[0]) == 0 and len(self.buffer) == 0:
                        self.parsed.append(list())
                    i += 1
                case False, '\\', c, _, _, _, _:
                    self.buffer += c
                    i += 2
                case False, '*', '*', _, _, _, _:
                    self.flush_buffer()
                    self.markdown_state ^= MarkdownState.BOLD
                    i += 2
                case False, '*', _, _, _, _, _:
                    self.flush_buffer()
                    self.markdown_state ^= MarkdownState.ITALIC
                    i += 1
                case _, '`', '`', '`', _, _, _:
                    assert MarkdownState.INLINE_CODE not in self.markdown_state, "Unclosed inline code"
                    self.flush_buffer()
                    self.markdown_state &= ~(MarkdownState.SIZE_BIT1 | MarkdownState.SIZE_BIT2)
                    if len(self.parsed) > 0 and len(self.parsed[-1]) > 0:
                        self.parsed.append(list())
                    self.markdown_state ^= MarkdownState.MULTILINE_CODE
                    i += 3
                case _, '`', _, _, _, _, _:
                    self.flush_buffer()
                    self.markdown_state ^= MarkdownState.INLINE_CODE
                    i += 1
                case _, c, _, _, _, _, _:
                    if c != '\n':
                        self.buffer += c
                    i += 1
        self.flush_buffer()
        del self.parsed[0]

    def flush_buffer(self):
        self.parsed[-1].append((self.buffer, self.markdown_state))
        self.buffer = ""


class MarkdownState(Flag):
    NORMAL = 0
    BOLD = auto()
    ITALIC = auto()
    INLINE_CODE = auto()
    MULTILINE_CODE = auto()
    SIZE_BIT1 = auto()
    SIZE_BIT2 = auto()

    @property
    def size(self):
        return 2 * (MarkdownState.SIZE_BIT1 in self) + (MarkdownState.SIZE_BIT2 in self)
