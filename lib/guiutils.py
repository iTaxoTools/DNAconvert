import tkinter as tk
import tkinter.ttk as ttk


class ScrolledText():
    """
    A text input widget with two scrollbars
    """

    def __init__(self, parent: tk.Widget, *, width: int, height: int, label: str) -> None:
        self.frame = ttk.Frame(parent)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.label = ttk.Label(self.frame, text=label)
        self.text = tk.Text(self.frame, width=width, height=height)
        self.vbar = ttk.Scrollbar(
            self.frame, orient=tk.VERTICAL, command=self.text.yview)
        self.hbar = ttk.Scrollbar(
            self.frame, orient=tk.HORIZONTAL, command=self.text.xview)
        self.text.configure(xscrollcommand=self.hbar.set,
                            yscrollcommand=self.vbar.set)
        self.label.grid(row=0, column=0, sticky='w')
        self.text.grid(row=1, column=0, sticky='nsew')
        self.vbar.grid(row=1, column=1, sticky='nsew')
        self.hbar.grid(row=2, column=0, sticky='nsew')
        self.grid = self.frame.grid
