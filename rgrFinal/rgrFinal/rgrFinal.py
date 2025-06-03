import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime, timedelta

class FilmStudioApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Киностудия")
        self.master.geometry("1000x700")
        
        self.setup_styles()
        self.conn = sqlite3.connect("filmstudio.db")
        self.create_tables()

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=1, fill="both")
        
        self.tabs = {
            "actors": ttk.Frame(self.notebook),
            "movies": ttk.Frame(self.notebook),
            "shootings": ttk.Frame(self.notebook),
            "schedule": ttk.Frame(self.notebook),
            "expenses": ttk.Frame(self.notebook),
            "budget": ttk.Frame(self.notebook),
            "export": ttk.Frame(self.notebook)
        }
        
        for name, tab in self.tabs.items():
            self.notebook.add(tab, text=self.get_tab_name(name))
        
        self.setup_actors_tab()
        self.setup_movies_tab()
        self.setup_shootings_tab()
        self.setup_schedule_tab()
        self.setup_expenses_tab()
        self.setup_budget_tab()
        self.setup_export_tab()
        
        self.setup_menu()
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def get_tab_name(self, tab_key):
        names = {
            "actors": "Актёры",
            "movies": "Фильмы",
            "shootings": "Съёмки",
            "schedule": "Расписание",
            "expenses": "Затраты на актёров",
            "budget": "Бюджеты фильмов",
            "export": "Экспорт"
        }
        return names.get(tab_key, tab_key)

    def setup_styles(self):
        style = ttk.Style()
        
        style.configure(".", padding=5)
        style.configure("TButton", padding=5)
        style.configure("TEntry", padding=5, width=25)
        style.configure("TCombobox", padding=5, width=25)
        style.configure("Treeview", rowheight=25)
        style.configure("TFrame", padding=10)
        style.configure("TLabel", padding=5)
        
        style.map('TCombobox',
            fieldbackground=[('!focus', 'white'), ('focus', 'white')],
            selectbackground=[('!focus', 'white'), ('focus', '#0078d7')],
            selectforeground=[('!focus', 'black'), ('focus', 'white')],
            background=[('!focus', 'white'), ('focus', 'white')],
            foreground=[('!focus', 'black'), ('focus', 'black')]
        )

    def setup_menu(self):
        menubar = tk.Menu(self.master)
        
        info_menu = tk.Menu(menubar, tearoff=0)
        info_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Информация", menu=info_menu)
        
        self.master.config(menu=menubar)

    def show_about(self):
        about_window = tk.Toplevel(self.master)
        about_window.title("О программе")
        about_window.geometry("400x300")
        
        ttk.Label(about_window, text="Киностудия", font=('Arial', 14, 'bold')).pack(pady=10)
        ttk.Label(about_window, text="Версия 1.0").pack()
        ttk.Label(about_window, text="Программа для учета актеров, фильмов и съемок").pack(pady=10)
        ttk.Label(about_window, text="Разработчик: Кулешов Дмитрий").pack()
        ttk.Label(about_window, text="© 2025 Все права защищены").pack(pady=20)
        
        ttk.Button(about_window, text="Закрыть", command=about_window.destroy).pack()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS actors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fio TEXT NOT NULL,
                ставка_за_день REAL NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                название TEXT NOT NULL,
                режиссёр TEXT,
                бюджет REAL NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS shootings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id INTEGER NOT NULL,
                movie_id INTEGER NOT NULL,
                дата TEXT NOT NULL,
                сцена TEXT,
                гонорар REAL,
                FOREIGN KEY(actor_id) REFERENCES actors(id),
                FOREIGN KEY(movie_id) REFERENCES movies(id)
            )
        """)
        self.conn.commit()

    def treeview_sort_column(self, tree, col, reverse):
        l = [(tree.set(k, col), k) for k in tree.get_children("")]
        try:
            l.sort(key=lambda t: float(t[0].replace(',', '.')), reverse=reverse)
        except (ValueError, TypeError):
            l.sort(key=lambda t: t[0], reverse=reverse)
        
        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)
        
        tree.heading(col, command=lambda: self.treeview_sort_column(tree, col, not reverse))

    def setup_actors_tab(self):
        main_frame = ttk.Frame(self.tabs["actors"])
        main_frame.pack(fill="both", expand=True)
        
        frame_form = ttk.Frame(main_frame)
        frame_form.pack(padx=10, pady=10, fill='x')
        
        search_frame = ttk.Frame(frame_form)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Label(search_frame, text="Поиск:").pack(side="left", padx=5)
        self.actor_search_entry = ttk.Entry(search_frame, width=30)
        self.actor_search_entry.pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(search_frame, text="Найти", command=self.search_actors).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Сброс", command=self.load_actors).pack(side="left", padx=5)
        
        ttk.Label(frame_form, text="ФИО:").grid(row=1, column=0, sticky="e")
        self.actor_fio_entry = ttk.Entry(frame_form, width=30)
        self.actor_fio_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Ставка за день:").grid(row=2, column=0, sticky="e")
        self.actor_rate_entry = ttk.Entry(frame_form, width=30)
        self.actor_rate_entry.grid(row=2, column=1, padx=5, pady=5)
        
        btn_frame = ttk.Frame(frame_form)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Добавить", command=self.add_actor).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_actor).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_actor).grid(row=0, column=2, padx=5)
        
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.actors_tree = ttk.Treeview(tree_frame, columns=("id", "fio", "rate"), show="headings")
        self.actors_tree.heading("id", text="ID", command=lambda: self.treeview_sort_column(self.actors_tree, "id", False))
        self.actors_tree.heading("fio", text="ФИО", command=lambda: self.treeview_sort_column(self.actors_tree, "fio", False))
        self.actors_tree.heading("rate", text="Ставка за день", command=lambda: self.treeview_sort_column(self.actors_tree, "rate", False))
        
        self.actors_tree.column("id", width=50, anchor="center")
        self.actors_tree.column("fio", width=250)
        self.actors_tree.column("rate", width=150, anchor="e")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.actors_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.actors_tree.configure(yscrollcommand=scrollbar.set)
        
        self.actors_tree.pack(fill="both", expand=True)
        self.actors_tree.bind("<<TreeviewSelect>>", self.on_actor_select)
        
        self.load_actors()

    def search_actors(self):
        search_text = self.actor_search_entry.get().strip()
        if not search_text:
            self.load_actors()
            return
        
        for row in self.actors_tree.get_children():
            self.actors_tree.delete(row)
        
        c = self.conn.cursor()
        c.execute("SELECT * FROM actors WHERE fio LIKE ?", (f"%{search_text}%",))
        
        for row in c.fetchall():
            self.actors_tree.insert("", "end", values=row)

    def load_actors(self):
        for row in self.actors_tree.get_children():
            self.actors_tree.delete(row)
        
        c = self.conn.cursor()
        c.execute("SELECT * FROM actors ORDER BY id")
        
        for row in c.fetchall():
            self.actors_tree.insert("", "end", values=row)

    def add_actor(self):
        fio = self.actor_fio_entry.get().strip()
        rate = self.actor_rate_entry.get().strip()
        
        if not fio:
            messagebox.showerror("Ошибка", "Введите ФИО актёра.")
            return
        
        try:
            rate_value = float(rate)
            if rate_value < 0:
                raise ValueError("Ставка не может быть отрицательной")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную ставку (положительное число).")
            return
        
        c = self.conn.cursor()
        c.execute("INSERT INTO actors (fio, ставка_за_день) VALUES (?, ?)", (fio, rate_value))
        self.conn.commit()
        
        self.load_actors()
        self.refresh_shootings_comboboxes()
        self.load_expenses_tab_data()
        
        self.actor_fio_entry.delete(0, tk.END)
        self.actor_rate_entry.delete(0, tk.END)

    def on_actor_select(self, event):
        selected = self.actors_tree.selection()
        if selected:
            values = self.actors_tree.item(selected[0])['values']
            self.actor_fio_entry.delete(0, tk.END)
            self.actor_fio_entry.insert(0, values[1])
            self.actor_rate_entry.delete(0, tk.END)
            self.actor_rate_entry.insert(0, values[2])

    def update_actor(self):
        selected = self.actors_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите актёра для обновления.")
            return
        
        actor_id = self.actors_tree.item(selected[0])['values'][0]
        fio = self.actor_fio_entry.get().strip()
        rate = self.actor_rate_entry.get().strip()
        
        if not fio:
            messagebox.showerror("Ошибка", "Введите ФИО актёра.")
            return
        
        try:
            rate_value = float(rate)
            if rate_value < 0:
                raise ValueError("Ставка не может быть отрицательной")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную ставку (положительное число).")
            return
        
        c = self.conn.cursor()
        c.execute("UPDATE actors SET fio=?, ставка_за_день=? WHERE id=?", (fio, rate_value, actor_id))
        self.conn.commit()
        
        self.load_actors()
        self.refresh_shootings_comboboxes()
        self.load_expenses_tab_data()

    def delete_actor(self):
        selected = self.actors_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите актёра для удаления.")
            return
        
        actor_id = self.actors_tree.item(selected[0])['values'][0]
        
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM shootings WHERE actor_id=?", (actor_id,))
        if c.fetchone()[0] > 0:
            messagebox.showerror("Ошибка", "Невозможно удалить актёра, так как он участвует в съёмках.")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого актёра?"):
            c.execute("DELETE FROM actors WHERE id=?", (actor_id,))
            self.conn.commit()
            self.load_actors()
            self.refresh_shootings_comboboxes()
            self.load_expenses_tab_data()

    def setup_movies_tab(self):
        main_frame = ttk.Frame(self.tabs["movies"])
        main_frame.pack(fill="both", expand=True)
        
        frame_form = ttk.Frame(main_frame)
        frame_form.pack(padx=10, pady=10, fill='x')
        
        search_frame = ttk.Frame(frame_form)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Label(search_frame, text="Поиск:").pack(side="left", padx=5)
        self.movie_search_entry = ttk.Entry(search_frame, width=30)
        self.movie_search_entry.pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(search_frame, text="Найти", command=self.search_movies).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Сброс", command=self.load_movies).pack(side="left", padx=5)
        
        ttk.Label(frame_form, text="Название:").grid(row=1, column=0, sticky="e")
        self.movie_title_entry = ttk.Entry(frame_form, width=30)
        self.movie_title_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Режиссёр:").grid(row=2, column=0, sticky="e")
        self.movie_director_entry = ttk.Entry(frame_form, width=30)
        self.movie_director_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Бюджет:").grid(row=3, column=0, sticky="e")
        self.movie_budget_entry = ttk.Entry(frame_form, width=30)
        self.movie_budget_entry.grid(row=3, column=1, padx=5, pady=5)
        
        btn_frame = ttk.Frame(frame_form)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Добавить", command=self.add_movie).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_movie).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_movie).grid(row=0, column=2, padx=5)
        
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.movies_tree = ttk.Treeview(tree_frame, columns=("id", "title", "director", "budget"), show="headings")
        self.movies_tree.heading("id", text="ID", command=lambda: self.treeview_sort_column(self.movies_tree, "id", False))
        self.movies_tree.heading("title", text="Название", command=lambda: self.treeview_sort_column(self.movies_tree, "title", False))
        self.movies_tree.heading("director", text="Режиссёр", command=lambda: self.treeview_sort_column(self.movies_tree, "director", False))
        self.movies_tree.heading("budget", text="Бюджет", command=lambda: self.treeview_sort_column(self.movies_tree, "budget", False))
        
        self.movies_tree.column("id", width=50, anchor="center")
        self.movies_tree.column("title", width=200)
        self.movies_tree.column("director", width=150)
        self.movies_tree.column("budget", width=150, anchor="e")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.movies_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.movies_tree.configure(yscrollcommand=scrollbar.set)
        
        self.movies_tree.pack(fill="both", expand=True)
        self.movies_tree.bind("<<TreeviewSelect>>", self.on_movie_select)
        
        self.load_movies()

    def search_movies(self):
        search_text = self.movie_search_entry.get().strip()
        if not search_text:
            self.load_movies()
            return
        
        for row in self.movies_tree.get_children():
            self.movies_tree.delete(row)
        
        c = self.conn.cursor()
        c.execute("SELECT * FROM movies WHERE название LIKE ?", (f"%{search_text}%",))
        
        for row in c.fetchall():
            self.movies_tree.insert("", "end", values=row)

    def load_movies(self):
        for row in self.movies_tree.get_children():
            self.movies_tree.delete(row)
        
        c = self.conn.cursor()
        c.execute("SELECT id, название, режиссёр, бюджет FROM movies ORDER BY id") 
        
        for row in c.fetchall():
            self.movies_tree.insert("", "end", values=row)

    def add_movie(self):
        title = self.movie_title_entry.get().strip()
        director = self.movie_director_entry.get().strip()
        budget = self.movie_budget_entry.get().strip()
        
        if not title:
            messagebox.showerror("Ошибка", "Введите название фильма.")
            return
        
        try:
            budget_value = float(budget)
            if budget_value < 0:
                raise ValueError("Бюджет не может быть отрицательным")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный бюджет (положительное число).")
            return
        
        c = self.conn.cursor()
        c.execute("INSERT INTO movies (название, режиссёр, бюджет) VALUES (?, ?, ?)", 
                 (title, director, budget_value))
        self.conn.commit()
        
        self.load_movies()
        self.refresh_shootings_comboboxes()
        self.load_budget_tab_data()
        
        self.movie_title_entry.delete(0, tk.END)
        self.movie_director_entry.delete(0, tk.END)
        self.movie_budget_entry.delete(0, tk.END)

    def on_movie_select(self, event):
        selected = self.movies_tree.selection()
        if selected:
            values = self.movies_tree.item(selected[0])['values']
            self.movie_title_entry.delete(0, tk.END)
            self.movie_title_entry.insert(0, values[1])
            self.movie_director_entry.delete(0, tk.END)
            self.movie_director_entry.insert(0, values[2])
            self.movie_budget_entry.delete(0, tk.END)
            self.movie_budget_entry.insert(0, values[3])

    def update_movie(self):
        selected = self.movies_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите фильм для обновления.")
            return
        
        movie_id = self.movies_tree.item(selected[0])['values'][0]
        title = self.movie_title_entry.get().strip()
        director = self.movie_director_entry.get().strip()
        budget = self.movie_budget_entry.get().strip()
        
        if not title:
            messagebox.showerror("Ошибка", "Введите название фильма.")
            return
        
        try:
            budget_value = float(budget)
            if budget_value < 0:
                raise ValueError("Бюджет не может быть отрицательным")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный бюджет (положительное число).")
            return
        
        c = self.conn.cursor()
        c.execute("UPDATE movies SET название=?, режиссёр=?, бюджет=? WHERE id=?", 
                 (title, director, budget_value, movie_id))
        self.conn.commit()
        
        self.load_movies()
        self.refresh_shootings_comboboxes()
        self.load_budget_tab_data()

    def delete_movie(self):
        selected = self.movies_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите фильм для удаления.")
            return
        
        movie_id = self.movies_tree.item(selected[0])['values'][0]
        
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM shootings WHERE movie_id=?", (movie_id,))
        if c.fetchone()[0] > 0:
            messagebox.showerror("Ошибка", "Невозможно удалить фильм, так как он используется в съёмках.")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот фильм?"):
            c.execute("DELETE FROM movies WHERE id=?", (movie_id,))
            self.conn.commit()
            self.load_movies()
            self.refresh_shootings_comboboxes()
            self.load_budget_tab_data()

    def setup_shootings_tab(self):
        frame_form = ttk.Frame(self.tabs["shootings"])
        frame_form.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame_form, text="Актёр:").grid(row=0, column=0, sticky="e")
        self.shooting_actor_cb = ttk.Combobox(frame_form, state="readonly", width=30)
        self.shooting_actor_cb.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Фильм:").grid(row=1, column=0, sticky="e")
        self.shooting_movie_cb = ttk.Combobox(frame_form, state="readonly", width=30)
        self.shooting_movie_cb.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Дата (YYYY-MM-DD):").grid(row=2, column=0, sticky="e")
        self.shooting_date_entry = ttk.Entry(frame_form, width=30)
        self.shooting_date_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Сцена:").grid(row=3, column=0, sticky="e")
        self.shooting_scene_entry = ttk.Entry(frame_form, width=30)
        self.shooting_scene_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Гонорар:").grid(row=4, column=0, sticky="e")
        self.shooting_fee_entry = ttk.Entry(frame_form, width=30)
        self.shooting_fee_entry.grid(row=4, column=1, padx=5, pady=5)
        
        btn_frame = ttk.Frame(frame_form)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Добавить", command=self.add_shooting).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_shooting).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_shooting).grid(row=0, column=2, padx=5)
        
        tree_frame = ttk.Frame(self.tabs["shootings"])
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.shootings_tree = ttk.Treeview(tree_frame, 
                                         columns=("id", "actor", "movie", "date", "scene", "fee"), 
                                         show="headings")
        self.shootings_tree.heading("id", text="ID", command=lambda: self.treeview_sort_column(self.shootings_tree, "id", False))
        self.shootings_tree.heading("actor", text="Актёр", command=lambda: self.treeview_sort_column(self.shootings_tree, "actor", False))
        self.shootings_tree.heading("movie", text="Фильм", command=lambda: self.treeview_sort_column(self.shootings_tree, "movie", False))
        self.shootings_tree.heading("date", text="Дата", command=lambda: self.treeview_sort_column(self.shootings_tree, "date", False))
        self.shootings_tree.heading("scene", text="Сцена", command=lambda: self.treeview_sort_column(self.shootings_tree, "scene", False))
        self.shootings_tree.heading("fee", text="Гонорар", command=lambda: self.treeview_sort_column(self.shootings_tree, "fee", False))
        
        self.shootings_tree.column("id", width=50, anchor="center")
        self.shootings_tree.column("actor", width=150)
        self.shootings_tree.column("movie", width=150)
        self.shootings_tree.column("date", width=100)
        self.shootings_tree.column("scene", width=150)
        self.shootings_tree.column("fee", width=100, anchor="e")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.shootings_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.shootings_tree.configure(yscrollcommand=scrollbar.set)
        
        self.shootings_tree.pack(fill="both", expand=True)
        self.shootings_tree.bind("<<TreeviewSelect>>", self.on_shooting_select)
        
        self.refresh_shootings_comboboxes()
        self.load_shootings()

    def refresh_shootings_comboboxes(self):
        c = self.conn.cursor()
    
        c.execute("SELECT id, fio FROM actors ORDER BY id")
        actors = [f"{row[0]} - {row[1]}" for row in c.fetchall()]
        self.shooting_actor_cb['values'] = actors
    
        c.execute("SELECT id, название FROM movies ORDER BY id")
        movies = [f"{row[0]} - {row[1]}" for row in c.fetchall()]
        self.shooting_movie_cb['values'] = movies

    def load_shootings(self):
        for row in self.shootings_tree.get_children():
            self.shootings_tree.delete(row)
        
        c = self.conn.cursor()
        c.execute("""
            SELECT s.id, a.fio, m.название, s.дата, s.сцена, s.гонорар
            FROM shootings s
            JOIN actors a ON s.actor_id = a.id
            JOIN movies m ON s.movie_id = m.id
            ORDER BY s.дата DESC
        """)
        
        for row in c.fetchall():
            self.shootings_tree.insert("", "end", values=row)

    def add_shooting(self):
        actor_text = self.shooting_actor_cb.get()
        movie_text = self.shooting_movie_cb.get()
        date_text = self.shooting_date_entry.get().strip()
        scene = self.shooting_scene_entry.get().strip()
        fee = self.shooting_fee_entry.get().strip()
        
        if not actor_text or not movie_text or not date_text:
            messagebox.showerror("Ошибка", "Заполните обязательные поля (Актёр, Фильм, Дата).")
            return
        
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите дату в формате ГГГГ-ММ-ДД.")
            return
        
        try:
            fee_value = float(fee) if fee else 0
            if fee_value < 0:
                raise ValueError("Гонорар не может быть отрицательным")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный гонорар (положительное число).")
            return
        
        actor_id = int(actor_text.split(" - ")[0])
        movie_id = int(movie_text.split(" - ")[0])
        
        c = self.conn.cursor()
        c.execute("SELECT бюджет FROM movies WHERE id=?", (movie_id,))
        budget = c.fetchone()[0]
        
        c.execute("SELECT SUM(гонорар) FROM shootings WHERE movie_id=?", (movie_id,))
        total_fees = c.fetchone()[0] or 0
        
        if total_fees + fee_value > budget:
            messagebox.showerror("Ошибка", 
                               f"Общий гонорар ({total_fees + fee_value:.2f}) превышает бюджет фильма ({budget:.2f})!")
            return
        
        c.execute("""
            INSERT INTO shootings (actor_id, movie_id, дата, сцена, гонорар)
            VALUES (?, ?, ?, ?, ?)
        """, (actor_id, movie_id, date_text, scene, fee_value))
        self.conn.commit()
        
        self.load_shootings()
        self.load_schedule_data()
        self.load_expenses_tab_data()
        self.load_budget_tab_data()
        
        self.shooting_actor_cb.set('')
        self.shooting_movie_cb.set('')
        self.shooting_date_entry.delete(0, tk.END)
        self.shooting_scene_entry.delete(0, tk.END)
        self.shooting_fee_entry.delete(0, tk.END)

    def on_shooting_select(self, event):
        selected = self.shootings_tree.selection()
        if selected:
            values = self.shootings_tree.item(selected[0])['values']
            
            c = self.conn.cursor()
            c.execute("SELECT id FROM actors WHERE fio=?", (values[1],))
            actor_id = c.fetchone()[0]
            
            c.execute("SELECT id FROM movies WHERE название=?", (values[2],))
            movie_id = c.fetchone()[0]
            
            self.shooting_actor_cb.set(f"{actor_id} - {values[1]}")
            self.shooting_movie_cb.set(f"{movie_id} - {values[2]}")
            self.shooting_date_entry.delete(0, tk.END)
            self.shooting_date_entry.insert(0, values[3])
            self.shooting_scene_entry.delete(0, tk.END)
            self.shooting_scene_entry.insert(0, values[4])
            self.shooting_fee_entry.delete(0, tk.END)
            self.shooting_fee_entry.insert(0, values[5])

    def update_shooting(self):
        selected = self.shootings_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите съёмку для обновления.")
            return
        
        shooting_id = self.shootings_tree.item(selected[0])['values'][0]
        actor_text = self.shooting_actor_cb.get()
        movie_text = self.shooting_movie_cb.get()
        date_text = self.shooting_date_entry.get().strip()
        scene = self.shooting_scene_entry.get().strip()
        fee = self.shooting_fee_entry.get().strip()
        
        if not actor_text or not movie_text or not date_text:
            messagebox.showerror("Ошибка", "Заполните обязательные поля (Актёр, Фильм, Дата).")
            return
        
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите дату в формате ГГГГ-ММ-ДД.")
            return
        
        try:
            fee_value = float(fee) if fee else 0
            if fee_value < 0:
                raise ValueError("Гонорар не может быть отрицательным")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный гонорар (положительное число).")
            return
        
        actor_id = int(actor_text.split(" - ")[0])
        movie_id = int(movie_text.split(" - ")[0])
        
        c = self.conn.cursor()
        c.execute("SELECT бюджет FROM movies WHERE id=?", (movie_id,))
        budget = c.fetchone()[0]
        
        c.execute("SELECT SUM(гонорар) FROM shootings WHERE movie_id=? AND id!=?", (movie_id, shooting_id))
        total_fees = c.fetchone()[0] or 0
        
        if total_fees + fee_value > budget:
            messagebox.showerror("Ошибка", 
                               f"Общий гонорар ({total_fees + fee_value:.2f}) превышает бюджет фильма ({budget:.2f})!")
            return
        
        c.execute("""
            UPDATE shootings 
            SET actor_id=?, movie_id=?, дата=?, сцена=?, гонорар=?
            WHERE id=?
        """, (actor_id, movie_id, date_text, scene, fee_value, shooting_id))
        self.conn.commit()
        
        self.load_shootings()
        self.load_schedule_data()
        self.load_expenses_tab_data()
        self.load_budget_tab_data()

    def delete_shooting(self):
        selected = self.shootings_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите съёмку для удаления.")
            return
        
        shooting_id = self.shootings_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту запись о съёмке?"):
            c = self.conn.cursor()
            c.execute("DELETE FROM shootings WHERE id=?", (shooting_id,))
            self.conn.commit()
            
            self.load_shootings()
            self.load_schedule_data()
            self.load_expenses_tab_data()
            self.load_budget_tab_data()

    def setup_schedule_tab(self):
        filter_frame = ttk.Frame(self.tabs["schedule"])
        filter_frame.pack(padx=10, pady=10, fill='x')
        
        ttk.Label(filter_frame, text="Период:").pack(side='left', padx=5)
        
        self.schedule_period = tk.StringVar()
        period_options = ["Все записи", "Сегодня", "Эта неделя", "Этот месяц", "Будущие"]
        period_menu = ttk.Combobox(filter_frame, textvariable=self.schedule_period, 
                                 values=period_options, state="readonly")
        period_menu.pack(side='left', padx=5)
        period_menu.current(0)
        period_menu.bind("<<ComboboxSelected>>", lambda e: self.load_schedule_data())
        
        tree_frame = ttk.Frame(self.tabs["schedule"])
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.schedule_tree = ttk.Treeview(tree_frame, 
                                        columns=("actor", "movie", "date", "scene"), 
                                        show="headings")
        
        self.schedule_tree.heading("actor", text="Актёр", command=lambda: self.treeview_sort_column(self.schedule_tree, "actor", False))
        self.schedule_tree.heading("movie", text="Фильм", command=lambda: self.treeview_sort_column(self.schedule_tree, "movie", False))
        self.schedule_tree.heading("date", text="Дата", command=lambda: self.treeview_sort_column(self.schedule_tree, "date", False))
        self.schedule_tree.heading("scene", text="Сцена", command=lambda: self.treeview_sort_column(self.schedule_tree, "scene", False))
        
        self.schedule_tree.column("actor", width=150)
        self.schedule_tree.column("movie", width=150)
        self.schedule_tree.column("date", width=100)
        self.schedule_tree.column("scene", width=250)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.schedule_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.schedule_tree.configure(yscrollcommand=scrollbar.set)
        
        self.schedule_tree.pack(fill="both", expand=True)
        
        self.load_schedule_data()

    def load_schedule_data(self):
        for row in self.schedule_tree.get_children():
            self.schedule_tree.delete(row)
        
        period = self.schedule_period.get()
        today = datetime.now().date()
        
        query = """
            SELECT a.fio, m.название, s.дата, s.сцена
            FROM shootings s
            JOIN actors a ON s.actor_id = a.id
            JOIN movies m ON s.movie_id = m.id
        """
        
        if period == "Сегодня":
            query += f" WHERE s.дата = '{today}'"
        elif period == "Эта неделя":
            start_week = today - timedelta(days=today.weekday())
            end_week = start_week + timedelta(days=6)
            query += f" WHERE s.дата BETWEEN '{start_week}' AND '{end_week}'"
        elif period == "Этот месяц":
            first_day = today.replace(day=1)
            last_day = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            query += f" WHERE s.дата BETWEEN '{first_day}' AND '{last_day}'"
        elif period == "Будущие":
            query += f" WHERE s.дата >= '{today}'"
        
        query += " ORDER BY s.дата"
        
        c = self.conn.cursor()
        c.execute(query)
        
        for row in c.fetchall():
            self.schedule_tree.insert("", "end", values=row)

    def setup_expenses_tab(self):
        main_frame = ttk.Frame(self.tabs["expenses"])
        main_frame.pack(fill="both", expand=True)
        
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        self.total_actors_label = ttk.Label(stats_frame, text="Всего актёров: 0")
        self.total_actors_label.pack(side="left", padx=10)
        
        self.total_expenses_label = ttk.Label(stats_frame, text="Общие затраты: 0.00")
        self.total_expenses_label.pack(side="left", padx=10)
        
        self.avg_expense_label = ttk.Label(stats_frame, text="Средний гонорар: 0.00")
        self.avg_expense_label.pack(side="left", padx=10)
        
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.expenses_tree = ttk.Treeview(tree_frame, 
                                        columns=("actor", "total_fee"), 
                                        show="headings")
        
        self.expenses_tree.heading("actor", text="Актёр", command=lambda: self.treeview_sort_column(self.expenses_tree, "actor", False))
        self.expenses_tree.heading("total_fee", text="Общие затраты", command=lambda: self.treeview_sort_column(self.expenses_tree, "total_fee", False))
        
        self.expenses_tree.column("actor", width=200)
        self.expenses_tree.column("total_fee", width=150, anchor="e")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.expenses_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.expenses_tree.configure(yscrollcommand=scrollbar.set)
        
        self.expenses_tree.pack(fill="both", expand=True)
        
        self.load_expenses_tab_data()

    def load_expenses_tab_data(self):
        for row in self.expenses_tree.get_children():
            self.expenses_tree.delete(row)
        
        c = self.conn.cursor()
        
        c.execute("""
            SELECT a.fio, IFNULL(SUM(s.гонорар), 0) as total_fee
            FROM actors a
            LEFT JOIN shootings s ON a.id = s.actor_id
            GROUP BY a.id
            ORDER BY a.fio
        """)
        
        total_expenses = 0
        actor_count = 0
        
        for row in c.fetchall():
            actor, fee = row
            self.expenses_tree.insert("", "end", values=(actor, f"{fee:.2f}"))
            total_expenses += fee
            actor_count += 1
        
        self.total_actors_label.config(text=f"Всего актёров: {actor_count}")
        self.total_expenses_label.config(text=f"Общие затраты: {total_expenses:.2f}")
        
        avg_expense = total_expenses / actor_count if actor_count > 0 else 0
        self.avg_expense_label.config(text=f"Средний гонорар: {avg_expense:.2f}")

    def setup_budget_tab(self):
        main_frame = ttk.Frame(self.tabs["budget"])
        main_frame.pack(fill="both", expand=True)
        
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        self.total_movies_label = ttk.Label(stats_frame, text="Всего фильмов: 0")
        self.total_movies_label.pack(side="left", padx=10)
        
        self.total_budget_label = ttk.Label(stats_frame, text="Общий бюджет: 0.00")
        self.total_budget_label.pack(side="left", padx=10)
        
        self.avg_budget_label = ttk.Label(stats_frame, text="Средний бюджет: 0.00")
        self.avg_budget_label.pack(side="left", padx=10)
        
        self.remaining_label = ttk.Label(stats_frame, text="Общий остаток: 0.00")
        self.remaining_label.pack(side="left", padx=10)
        
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.budget_tree = ttk.Treeview(tree_frame, 
                                      columns=("movie", "budget", "spent", "remaining"), 
                                      show="headings")
        
        self.budget_tree.heading("movie", text="Фильм", command=lambda: self.treeview_sort_column(self.budget_tree, "movie", False))
        self.budget_tree.heading("budget", text="Бюджет", command=lambda: self.treeview_sort_column(self.budget_tree, "budget", False))
        self.budget_tree.heading("spent", text="Потрачено", command=lambda: self.treeview_sort_column(self.budget_tree, "spent", False))
        self.budget_tree.heading("remaining", text="Остаток", command=lambda: self.treeview_sort_column(self.budget_tree, "remaining", False))
        
        self.budget_tree.column("movie", width=200)
        self.budget_tree.column("budget", width=120, anchor="e")
        self.budget_tree.column("spent", width=120, anchor="e")
        self.budget_tree.column("remaining", width=120, anchor="e")
        
        self.budget_tree.tag_configure('positive', foreground='green')
        self.budget_tree.tag_configure('negative', foreground='red')
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.budget_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.budget_tree.configure(yscrollcommand=scrollbar.set)
        
        self.budget_tree.pack(fill="both", expand=True)
        
        self.load_budget_tab_data()

    def load_budget_tab_data(self):
        for row in self.budget_tree.get_children():
            self.budget_tree.delete(row)
        
        c = self.conn.cursor()
        
        c.execute("""
            SELECT 
                m.название, 
                m.бюджет, 
                IFNULL(SUM(s.гонорар), 0) as spent,
                m.бюджет - IFNULL(SUM(s.гонорар), 0) as remaining
            FROM movies m
            LEFT JOIN shootings s ON m.id = s.movie_id
            GROUP BY m.id
            ORDER BY m.название
        """)
        
        total_movies = 0
        total_budget = 0
        total_spent = 0
        total_remaining = 0
        
        for row in c.fetchall():
            movie, budget, spent, remaining = row
            tag = 'positive' if remaining >= 0 else 'negative'
            self.budget_tree.insert("", "end", 
                                   values=(movie, f"{budget:.2f}", f"{spent:.2f}", f"{remaining:.2f}"), 
                                   tags=(tag,))
            
            total_movies += 1
            total_budget += budget
            total_spent += spent
            total_remaining += remaining
        
        self.total_movies_label.config(text=f"Всего фильмов: {total_movies}")
        self.total_budget_label.config(text=f"Общий бюджет: {total_budget:.2f}")
        self.avg_budget_label.config(text=f"Средний бюджет: {total_budget/total_movies:.2f}" if total_movies > 0 else "Средний бюджет: 0.00")
        self.remaining_label.config(text=f"Общий остаток: {total_remaining:.2f}")

    def setup_export_tab(self):
        frame = ttk.Frame(self.tabs["export"])
        frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        ttk.Label(frame, text="Экспорт данных", font=('Arial', 12, 'bold')).pack(pady=10)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Экспорт актёров", command=lambda: self.export_data("actors")).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="Экспорт фильмов", command=lambda: self.export_data("movies")).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(btn_frame, text="Экспорт съёмок", command=lambda: self.export_data("shootings")).grid(row=0, column=2, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Экспорт всех данных", command=self.export_all_data).grid(row=1, column=0, columnspan=3, pady=10)
        
        self.export_status = ttk.Label(frame, text="")
        self.export_status.pack(pady=10)

    def export_data(self, data_type):
        directory = filedialog.askdirectory(title="Выберите папку для сохранения")
        if not directory:
            return
        
        try:
            c = self.conn.cursor()
            
            if data_type == "actors":
                filename = f"{directory}/actors.csv"
                c.execute("SELECT * FROM actors")
                data = c.fetchall()
                headers = ["ID", "ФИО", "Ставка за день"]
            elif data_type == "movies":
                filename = f"{directory}/movies.csv"
                c.execute("SELECT * FROM movies")
                data = c.fetchall()
                headers = ["ID", "Название", "Режиссёр", "Бюджет"]
            elif data_type == "shootings":
                filename = f"{directory}/shootings.csv"
                c.execute("""
                    SELECT s.id, a.fio, m.название, s.дата, s.сцена, s.гонорар
                    FROM shootings s
                    JOIN actors a ON s.actor_id = a.id
                    JOIN movies m ON s.movie_id = m.id
                """)
                data = c.fetchall()
                headers = ["ID", "Актёр", "Фильм", "Дата", "Сцена", "Гонорар"]
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)
            
            self.export_status.config(text=f"Данные успешно экспортированы в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")

    def export_all_data(self):
        directory = filedialog.askdirectory(title="Выберите папку для сохранения")
        if not directory:
            return
        
        try:
            self.export_data("actors")
            self.export_data("movies")
            self.export_data("shootings")
            self.export_status.config(text=f"Все данные экспортированы в {directory}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")

    def on_tab_changed(self, event):
        tab_name = self.notebook.tab(self.notebook.select(), "text")
        
        if tab_name == "Расписание":
            self.load_schedule_data()
        elif tab_name == "Затраты на актёров":
            self.load_expenses_tab_data()
        elif tab_name == "Бюджеты фильмов":
            self.load_budget_tab_data()

if __name__ == "__main__":
    root = tk.Tk()
    app = FilmStudioApp(root)
    root.mainloop()