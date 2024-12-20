from os import path, listdir
import sys
from tkinter import *
from tkinter import filedialog, messagebox
import re
from natsort import natsorted


def resource_path(relative):
    """
    Функция-адаптер пути к файлу для инсталлятора.

    При распаковке архива программы во временный каталог новый путь будет прописан в sys._MEIPASS.
    :param relative: Путь в проекте.
    """
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = path.abspath('.')
    return path.join(bundle_dir, relative)


class But(Button):
    """
    Переопределение стиля кнопки.
    """
    def __init__(self, master, **vars):
        super().__init__(
            master,
            bg='#9ff',
            cursor='hand2',
            fg='#190000',
            font=('Calibri', 12),
            **vars
        )


class Lab(Label):
    """
    Переопределение стиля надписи (метки).
    """
    def __init__(self, master, bg='#000e20', fg='#b4b4b4', font_size=14, **vars):
        super().__init__(
            master,
            bg=bg,
            fg=fg,
            font=('Calibri', font_size),
            justify='left',
            **vars
        )


class Tex(Entry):
    """
    Переопределение стиля текстового поля.
    """
    def __init__(self, master, width=55, placeholder='', **vars):
        self.fg = '#9ba7bd'
        self.fg2 = '#4d535c'
        super().__init__(
            master,
            bg='#1b273d',
            border=1,
            fg=self.fg,
            font=('Calibri', 14),
            width=width,
            **vars
        )
        self.placeholder = placeholder
        self.bind('<FocusIn>', self.foc_in)
        self.bind('<FocusOut>', self.foc_out)
        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.fg2

    def foc_in(self, *args):
        if self['fg'] == self.fg2:
            self.delete(0, END)
            self['fg'] = self.fg

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()


class Chb(Checkbutton):
    """
    Переопределение стиля выключателя.
    """
    def __init__(self, master, **vars):
        super().__init__(
            master,
            bg='#000e20',
            fg='#b4b4b4',
            font=('Calibri', 14),
            **vars
        )


class App(Tk):
    def __init__(self):
        super().__init__()
        self.iconbitmap(resource_path('Orland.ico'))
        self.title('Music.m3u8')
        self.geometry('1000x435')
        self.resizable(False, False)
        self.config(bg='#000e20', padx=5, pady=5)

        # Результирующий текстовый файл (Music.txt).
        self.txt = None
        lbl_txt_a = Lab(self, text='Укажите результирующий текстовый файл')
        lbl_txt_a.grid(column=0, row=0, sticky=W)
        self.but_txt = But(self, command=self.ask_save_txt_filename, text='Обзор…')
        self.but_txt.grid(column=1, row=0, sticky=W, padx=5)
        self.txt_txt = Tex(self, placeholder='Файл не указан.')
        self.txt_txt.grid(column=2, row=0, padx=5)

        # Результирующий M3U8-файл (плейлист) (Music.m3u8).
        self.m3u8 = None
        lbl_m3u8_a = Lab(self, text='Укажите результирующий M3U8-файл')
        lbl_m3u8_a.grid(column=0, row=1, sticky=W)
        self.but_m3u8 = But(self, command=self.ask_save_m3u8_filename, text='Обзор…')
        self.but_m3u8.grid(column=1, row=1, sticky=W, padx=5)
        self.txt_m3u8 = Tex(self, placeholder='Файл не указан.')
        self.txt_m3u8.grid(column=2, row=1, padx=5)

        # Путь к папке с музыкой.
        self.pdsn = None
        lbl_pdsn_a = Lab(self, text='Укажите путь к папке с музыкой')
        lbl_pdsn_a.grid(column=0, row=2, sticky=W)
        self.but_pdsn = But(self, command=self.ask_pdsn_dirname, text='Обзор…')
        self.but_pdsn.grid(column=1, row=2, sticky=W, padx=5)
        self.txt_pdsn = Tex(self, placeholder='Путь не указан.')
        self.txt_pdsn.grid(column=2, row=2, padx=5)

        # Путь к папке с M3U8-файлами (плейлистами).
        self.pm3u8 = None
        lbl_pm3u8_a = Lab(self, text='Укажите путь к папке с M3U8-файлами')
        lbl_pm3u8_a.grid(column=0, row=3, sticky=W)
        self.but_pm3u8 = But(self, command=self.ask_pm3u8_dirname, text='Обзор…')
        self.but_pm3u8.grid(column=1, row=3, sticky=W, padx=5)
        self.txt_pm3u8 = Tex(self, placeholder='Путь не указан.')
        self.txt_pm3u8.grid(column=2, row=3, padx=5)

        # Выключатель «Добавлять в результирующий M3U8-файл ID3-теги.»
        self.chb_tags_var = BooleanVar()
        chb_tags = Chb(self, text='Добавлять в результирующий M3U8-файл ID3-теги.', variable=self.chb_tags_var)
        chb_tags.grid(column=0, row=4, columnspan=3, sticky=W)
        lbl_tags_ = Lab(
            self,
            font_size=11,
            text='(Теги берутся из исходных M3U8-файлов. Если тегов там нет, результат будет некорректен.)'
        )
        lbl_tags_.grid(column=0, row=5, columnspan=3, sticky=W)

        # Выключатель «Форсировать обновление результирующего M3U8-файла.»
        self.chb_force_var = BooleanVar()
        chb_force = Chb(self, text='Форсировать обновление результирующего M3U8-файла.', variable=self.chb_force_var)
        chb_force.grid(column=0, row=6, columnspan=3, sticky=W)

        # Выключатель «Создать LAN-версию результирующего M3U8-файла.»
        self.chb_lan_var = BooleanVar()
        chb_lan = Chb(self, text='Создать LAN-версию результирующего M3U8-файла.', variable=self.chb_lan_var)
        chb_lan.grid(column=0, row=7, columnspan=3, sticky=W)

        # Сетевой адрес папки с музыкой.
        self.smb = None
        lbl_smb_a = Lab(self, text='Укажите сетевой адрес папки с музыкой')
        lbl_smb_a.grid(column=0, row=8, sticky=W)
        self.txt_smb = Tex(self, 63, placeholder='Сетевой адрес не указан. Формат: smb://192.168.0.100/Music')
        self.txt_smb.grid(column=1, row=8, columnspan=2, sticky=W, padx=5)

        # Кнопка «OK».
        but_ok = But(self, command=self.main, text='OK')
        but_ok.grid(column=0, row=9, columnspan=3)

        # Места выводов сообщений об обновлении результирующих файлов или пропуске обязательных полей.
        self.lbl_rep_txt = Lab(self)
        self.lbl_rep_txt.grid(column=0, row=10, columnspan=3)
        self.lbl_rep_m3u8 = Lab(self)
        self.lbl_rep_m3u8.grid(column=0, row=11, columnspan=3)

        # Авторский титр.
        self.lbl_author = Lab(self, font_size=12, text='© Orland, 2024.')
        self.lbl_author.grid(column=0, row=12, columnspan=3, sticky=W, pady=15)

    def ask_save_txt_filename(self) -> None:
        """
        Выбор результирующего текстового файла.
        """
        fn = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=(('Текстовый файл', '*.txt'),),
            initialdir='/',
            initialfile='Music.txt',
            title='Выбор результирующего текстового файла'
        )
        if fn:
            self.txt = fn
            self.txt_txt.delete(0, END)
            self.txt_txt.insert(0, fn)

    def ask_save_m3u8_filename(self) -> None:
        """
        Выбор результирующего M3U8-файла.
        """
        fn = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=(('Плейлист формата M3U8', '*.m3u8'),),
            initialdir='/',
            initialfile='Music.m3u8',
            title='Выбор результирующего M3U8-файла'
        )
        if fn:
            self.m3u8 = fn
            self.txt_m3u8.delete(0, END)
            self.txt_m3u8.insert(0, fn)

    def ask_pdsn_dirname(self) -> None:
        """
        Выбор пути к папке с музыкой.
        """
        fn = filedialog.askdirectory(
            # Здесь рекомендуется в коде указать конкретную папку, если она постоянная.
            # Например: initialdir='C:/Music'
            initialdir='/',
            mustexist=True,
            title='Выбор пути к папке с музыкой'
        )
        if fn:
            self.pdsn = fn
            self.txt_pdsn.delete(0, END)
            self.txt_pdsn.insert(0, fn)

    def ask_pm3u8_dirname(self) -> None:
        """
        Выбор пути к папке с M3U8-файлами.
        """
        fn = filedialog.askdirectory(
            # Здесь рекомендуется в коде указать конкретную папку, если она постоянная.
            # Плейлисты с ID3-тегами и без тегов должны быть разделены по разным папкам.
            # Используя соответствующий выключатель можно в коде указать:
            # initialdir='C:/WinAMP playlists' if self.chb_tags_var.get() else 'C:/foobar2000 playlists',
            initialdir='/',
            mustexist=True,
            title='Выбор пути к папке с M3U8-файлами'
        )
        if fn:
            self.pm3u8 = fn
            self.txt_pm3u8.delete(0, END)
            self.txt_pm3u8.insert(0, fn)

    def no_file(self, i: int) -> None:
        """
        Выбор и вывод сообщения о пропуске обязательного поля.
        :param i: Индекс поля.
        """
        if i == 0:
            self.lbl_rep_txt['text'] = 'Не указан результирующий текстовый файл!'
        if i == 1:
            self.lbl_rep_m3u8['text'] = 'Не указан результирующий M3U8-файл!'
        if i == 2:
            self.lbl_rep_txt['text'] = 'Не указан путь к папке с музыкой!'
        if i == 3:
            self.lbl_rep_m3u8['text'] = 'Не указан путь к папке с M3U8-файлами!'
        if i == 4:
            self.lbl_rep_txt['text'] = 'Не указан сетевой адрес папки с музыкой!'

    @staticmethod
    def path_(text: str) -> str:
        """
        Удаление слэша в конце пути.
        :param text: Путь.
        :return: Отредактированный путь.
        """
        s = text[-1]
        if s == '\\' or s == '/':
            return text[:-1]
        return text

    def music_txt(self) -> tuple[bool, dict]:
        """
        Формирование результирующего текстового файла.
        :return: Флаг обновления и словарь сообщений об отсутствии в конкретной папке исполнителя файла
            «Date-SN-Name.txt».
        """
        fs = '/Date-SN-Name.txt'
        mt = path.getmtime(self.txt) if path.isfile(self.txt) else 0
        dirs = listdir(self.pdsn)
        res = []
        e = {}
        for key, d in enumerate(dirs):
            if path.isfile(self.pdsn + '/' + d + fs):
                ft = path.getmtime(self.pdsn + '/' + d + fs)
                mt = ft if ft > mt else mt
            else:
                e[key] = f'В папке «<tt>{d}</tt>» нет файла «<tt>Date-SN-Name.txt</tt>».'
        if not path.isfile(self.txt) or mt > path.getmtime(self.txt):
            pattern = r'\A(?:[+=]+?)?(?:\s)?(\S{10})\s(\S+)\s+'
            for key, d in enumerate(dirs):
                if key not in e:
                    with open(self.pdsn + '/' + d + fs, 'r', encoding='utf8') as file:
                        lst = [line.replace(chr(151), chr(8212)) for line in file]
                    for i in range(1, len(lst)):
                        if lst[i][1:3].isdigit():
                            if lst[i][0] in ['-', '?'] or lst[i].strip() == '':
                                continue
                            m = re.match(pattern, lst[i])
                            tt = ''
                            if len(m[2]) < 9:
                                tt = '\t\t'
                            elif len(m[2]) < 13:
                                tt = '\t'
                            lst[i] = re.sub(pattern, f'{m[1]} {m[2]}\t{tt}{lst[0].strip()}//\t\t', lst[i])
                            if not lst[i][0].isdigit():
                                res.append(lst[i][2 if not lst[i][1].isdigit() else 1:])
                            else:
                                res.append(lst[i])
                        elif lst[i][0:4] == 'http':
                            break
                        elif lst[i][0:3] == '\t\t\t' or lst[i][0:3] == '   ':
                            res[len(res) - 1] = res[len(res) - 1].strip() + lst[i]
            if len(res) > 0:
                res = natsorted(res)
                s = []
                for _ in range(len(res)):
                    if res[0][2] == '_':
                        s.append(res.pop(0))
                    else:
                        break
                res.extend(s)
                with open(self.txt, 'w', encoding='utf8') as file:
                    file.writelines(res)
                return True, e
            return False, e
        return False, e

    def music_m3u8(self) -> tuple[bool, str | None]:
        """
        Формирование результирующего плейлиста.
        :return: Флаг обновления и сообщение об отсутствии результирующего текстового файла в случае его отсутствия.
        """
        if path.isfile(self.txt) and (
            not path.isfile(self.m3u8) or
            path.getmtime(self.txt) > path.getmtime(self.m3u8) or
            self.chb_force_var.get()
        ):
            res = ['#EXTM3U\n'] if self.chb_tags_var.get() else ['#\n']
            with open(self.txt, 'r', encoding='utf8') as file:
                albums = [line.replace(chr(151), chr(8212)) for line in file]
            for album in albums:
                y = False
                m = re.match(r'\A(\S{10}\s\S+)\s+(.*?)//\s', album)
                m2 = m[2]
                for o, n in {':': '_', ';': '_'}.items():
                    if o in m2:
                        m2 = m2.replace(o, n)
                with open(self.pm3u8 + '/' + m2 + '.m3u8', 'r', encoding='utf8') as file:
                    m3u8 = [line.replace(chr(151), chr(8212)) for line in file]
                if self.chb_tags_var.get() and m3u8[1][0] == '#':
                    for i in range(2, len(m3u8), 2):
                        if m[1] in m3u8[i]:
                            res.append(m3u8[i - 1])
                            res.append(m3u8[i])
                            y = True
                        elif y:
                            break
                else:
                    for tr in m3u8:
                        if tr[0] == '#':
                            continue
                        if m[1] in tr:
                            res.append(tr)
                            y = True
                        elif y:
                            break
            with open(self.m3u8, 'w', encoding='utf8') as file:
                file.writelines(res)
            if self.chb_lan_var.get():
                res_m3u8 = re.sub(r'\.m3u8\Z', '_LAN.m3u8', self.m3u8)
                t = 2 if self.chb_tags_var.get() else 1
                for i in range(t, len(res), t):
                    res[i] = res[i].replace('\\', '/').replace(self.pdsn, self.smb)
                with open(res_m3u8, 'w', encoding='utf8') as file:
                    file.writelines(res)
            return True, None
        if not path.isfile(self.txt):
            return False, f'Нет файла «<tt>{self.txt}</tt>».'
        return False, None

    @staticmethod
    def errors(e: dict) -> None:
        """
        Вывод диалогового окна с сообщениями об ошибках.
        :param e: Словарь с сообщениями.
        """
        str_e = ''
        for val in e.values():
            str_e += val + '\n'
        messagebox.showwarning('Внимание!', str_e)

    def main(self) -> None:
        """
        Обработчик нажатия на кнопку «OK» в окне программы.
        """
        self.lbl_rep_txt['text'] = ''
        self.lbl_rep_m3u8['text'] = ''
        try:  # Проверка обязательных полей.
            if not self.txt:
                self.txt = self.txt_txt.get().strip()
            if not path.isdir(path.dirname(self.txt)):
                self.no_file(0)
                raise ValueError()
            if not self.m3u8:
                self.m3u8 = self.txt_m3u8.get().strip()
            if not path.isdir(path.dirname(self.m3u8)):
                self.no_file(1)
                raise ValueError()
            if not self.pdsn:
                self.pdsn = self.txt_pdsn.get().strip()
            if not path.isdir(self.pdsn):
                self.no_file(2)
                raise ValueError()
            if not self.pm3u8:
                self.pm3u8 = self.txt_pm3u8.get().strip()
            if not path.isdir(self.pm3u8):
                self.no_file(3)
                raise ValueError()
            if self.chb_lan_var.get() and not self.smb:
                self.smb = self.txt_smb.get().strip()
            if self.chb_lan_var.get() and not self.smb:
                self.no_file(4)
                raise ValueError()
        except:
            self.errors({0: 'Недостаточно данных.'})
        else:
            self.pdsn = self.path_(self.pdsn)
            self.pm3u8 = self.path_(self.pm3u8)
            txt_chg, err = self.music_txt()
            m3u8_chg = False
            if len(err) == 0:
                m3u8_chg, e = self.music_m3u8()
                if e:
                    err['m3u8'] = e
            if txt_chg:
                self.lbl_rep_txt['text'] = f'{self.txt} обновлён.'
            else:
                self.lbl_rep_txt['text'] = f'{self.txt} | Обновления не было.'
            if m3u8_chg:
                self.lbl_rep_m3u8['text'] = f'{self.m3u8} обновлён.'
            if len(err):
                self.errors(err)


if __name__ == '__main__':
    app = App()
    app.mainloop()
