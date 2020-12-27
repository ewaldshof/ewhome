# utility functions for formatting text



class ColorText():
    DEBUG = True

    def __init__(self, text):
        self.text = text
        self.codes = set()

    def ANSIS(self, codes):
        self.codes |= {*codes}
        return self

    def ANSI(self, code):
        self.codes.add(code)
        return self

    def show(self, reset=True):
        end = "\033[0m\n" if reset else "\n" 
        print("\033[0", end="")
        print(*self.codes, sep=";", end="")
        print("m", self.text, end=end,  sep="")

    @classmethod 
    def print_heading(cls, text):
        cls("\n"+text).heading().show()

    @classmethod 
    def print_error(cls, text):
        cls(text).error().show()

    @classmethod 
    def print_ok(cls, text):
        cls(text).ok().show()
 
    @classmethod 
    def print_warning(cls, text):
        cls(text).warning().show()

    @classmethod 
    def print_info(cls, text):
        cls(text).info().show()

    @classmethod 
    def print_exception(cls, text):
        cls(text).exception().show()

    @classmethod
    def format_exception(cls, e, msg="Exception"):
        cls(msg).exception().blink().show()
        cls.print_exception(f"\t{type(e).__name__}: {str(e)}")

    @classmethod 
    def print_debug(cls, text):
        if cls.DEBUG:
            cls(text).debug().show()

    def heading(self):
        return self.bold().blue().underline()

    def error(self):
        return self.bold().red()

    def ok(self):
        return self.green()

    def warning(self):
        return self.yellow()

    def info(self):
        return self.blue()

    def exception(self):
        return self.bold().magenta()

    def debug(self):
        return self.faint().cyan()


    def reset(self):
        return self.ANSI(0)

    def bold(self):
        return self.ANSI(1)

    def faint(self):
        return self.ANSI(2)

    def italic(self):
        return self.ANSI(3)

    def underline(self):
        return self.ANSI(4)

    def blink(self, rapid=True):
        return self.ANSI(6 if rapid else 5)

    def reverse(self):
        return self.ANSI(7)

    def crossed_out(self):
        return self.ANSI(9)

    def black(self):
        return self.ANSI(30)

    def red(self):
        return self.ANSI(31)

    def green(self):
        return self.ANSI(32)

    def yellow(self):
        return self.ANSI(33)

    def blue(self):
        return self.ANSI(34)

    def magenta(self):
        return self.ANSI(35)

    def cyan(self):
        return self.ANSI(36)

    def white(self):
        return self.WHITE(37)

    def bg_black(self):
        return self.ANSI(90)

    def bg_red(self):
        return self.ANSI(91)

    def bg_green(self):
        return self.ANSI(92)

    def bg_yellow(self):
        return self.ANSI(93)

    def bg_blue(self):
        return self.ANSI(94)

    def bg_magenta(self):
        return self.ANSI(95)

    def bg_cyan(self):
        return self.ANSI(96)

    def bg_white(self):
        return self.WHITE(97)


# run tests if called from the command line
if __name__ == '__main__':
    ColorText("Hello").ANSI(31).ANSI(1).show()
    ColorText("Hello from list").ANSIS((31,1)).show()
    ColorText("Hello from chain").bold().red().show()
    
    ColorText("Heading").heading().show()
    ColorText("Error").error().show()
    ColorText("OK").ok().show()
    ColorText("Warning").warning().show()
    ColorText("Info").info().show()
    ColorText("Exception").exception().show()
    ColorText("Debug").debug().show()

    ColorText.print_heading("Heading")
    ColorText.print_error("Error")
    ColorText.print_ok("OK")
    ColorText.print_warning("Warning")
    ColorText.print_info("Info")
    ColorText.print_exception("Exception")
    ColorText.print_debug("Debug")

    try:
        a=1/0
    except Exception as e:
        ColorText.format_exception(e)