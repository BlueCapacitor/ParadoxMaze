from ui.widgets.display import Display


def set_up_and_run():
    display.current_page = display.Page.LEVEL_SELECT


display = Display()
display.title("Paradox Maze")

display.after(0, set_up_and_run)
display.mainloop()
