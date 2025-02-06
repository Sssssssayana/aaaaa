import msvcrt
import sys
import curses


def getpass_with_stars(stdscr=None, prompt="Введите пароль: "):
    """
    Функция для ввода пароля с отображением звездочек.
    Поддерживает как curses (Linux/Unix), так и msvcrt (Windows)
    """
    if stdscr:  # Используем curses (Linux/Unix)
        stdscr.clear()
        stdscr.addstr(prompt)
        stdscr.refresh()

        password = ""
        while True:
            ch = stdscr.getch()

            if ch == 10:  # Enter
                break
            elif ch in (127, 8):  # Backspace
                if password:
                    password = password[:-1]
                    stdscr.addstr("\b \b")
                    stdscr.refresh()
            else:
                password += chr(ch)
                stdscr.addstr('*')
                stdscr.refresh()

        return password

    else:  # Используем msvcrt (Windows)
        print(prompt, end='', flush=True)
        password = ""

        while True:
            char = msvcrt.getch()
            char = char.decode('utf-8', errors='ignore')

            if char == '\r':  # Enter
                print()
                break
            elif char == '\b':  # Backspace
                if password:
                    password = password[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            elif char.isprintable():
                password += char
                sys.stdout.write('*')
                sys.stdout.flush()

        return password 