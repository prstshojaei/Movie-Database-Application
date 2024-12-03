import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import os

def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",

        # enter your own password here
        password="password",
        database="MovieCatalogDB"
    )

def create_database(conn):
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS MovieCatalogDB")
    cursor.execute("USE MovieCatalogDB")
    conn.commit()

def execute_sql_file(conn, filename):
    with open(filename, 'r') as file:
        sql_commands = file.read().split(';')
        cursor = conn.cursor()
        for command in sql_commands:
            command = command.strip()
            if command:
                cursor.execute(command)
        conn.commit()

class MovieDatabaseApp:
    def __init__(self, root, conn):
        self.root = root
        self.conn = conn
        self.root.title("Movie Database Search")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="Search by:").grid(row=0, column=0, padx=10, pady=10)

        self.search_var = tk.StringVar()
        search_options = ["Year", "Genre", "Actor", "Director", "Country", "Age", "Nationality", "Rating"]
        self.search_combobox = ttk.Combobox(self.root, textvariable=self.search_var, values=search_options)
        self.search_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.search_combobox.current(0)

        self.search_entry = ttk.Entry(self.root)
        self.search_entry.grid(row=0, column=2, padx=10, pady=10)

        search_button = ttk.Button(self.root, text="Search", command=self.search)
        search_button.grid(row=0, column=3, padx=10, pady=10)

        self.tree = ttk.Treeview(self.root,
                                columns=("ID", "Title", "Year", "Time", "Language", "Release Date", "Country", "Additional Info"),
                                show='headings')
        self.tree.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Year", text="Year")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Language", text="Language")
        self.tree.heading("Release Date", text="Release Date")
        self.tree.heading("Country", text="Country")
        self.tree.heading("Additional Info", text="Additional Info")

        self.tree.column("ID", width=50)
        self.tree.column("Title", width=200)
        self.tree.column("Year", width=100)
        self.tree.column("Time", width=100)
        self.tree.column("Language", width=100)
        self.tree.column("Release Date", width=150)
        self.tree.column("Country", width=100)
        self.tree.column("Additional Info", width=200)


    def search(self):
        search_type = self.search_var.get()
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showerror("Input Error", "Please enter a search term")
            return

        cursor = self.conn.cursor()
        if search_type == "Year":
            if not search_term.isdigit():
                messagebox.showerror("Input Error", "Please enter a valid year (numbers only)")
                return
            query = f"SELECT m.*, '' as additional_info FROM movie m WHERE m.mov_year = {search_term}"
        elif search_type == "Genre":
            query = f"""
                SELECT m.*, g.gen_title as additional_info
                FROM movie m
                JOIN movie_genres mg ON m.mov_id = mg.mov_id
                JOIN genres g ON mg.gen_id = g.gen_id
                WHERE g.gen_title = '{search_term}'
            """
        elif search_type == "Actor":
            query = f"""
                SELECT m.*, CONCAT(a.act_fname, ' ', a.act_lname) as additional_info
                FROM movie m
                JOIN movie_cast mc ON m.mov_id = mc.mov_id
                JOIN actor a ON mc.act_id = a.act_id
                WHERE a.act_fname = '{search_term}' OR a.act_lname = '{search_term}'
            """
        elif search_type == "Age":
            if not search_term.isdigit():
                messagebox.showerror("Input Error", "Please enter a valid age (numbers only)")
                return
            query = f"""
                SELECT m.*, CONCAT(a.act_fname, ' ', a.act_lname) as additional_info
                FROM movie m
                JOIN movie_cast mc ON m.mov_id = mc.mov_id
                JOIN actor a ON mc.act_id = a.act_id
                WHERE a.act_age = {search_term}
            """
        elif search_type == "Nationality":
            query = f"""
                SELECT m.*, CONCAT(a.act_fname, ' ', a.act_lname) as additional_info
                FROM movie m
                JOIN movie_cast mc ON m.mov_id = mc.mov_id
                JOIN actor a ON mc.act_id = a.act_id
                WHERE a.act_nationality = '{search_term}'
            """
        elif search_type == "Director":
            query = f"""
                SELECT m.*, CONCAT(d.dir_fname, ' ', d.dir_lname) as additional_info
                FROM movie m
                JOIN movie_direction md ON m.mov_id = md.mov_id
                JOIN director d ON md.dir_id = d.dir_id
                WHERE d.dir_fname = '{search_term}' OR d.dir_lname = '{search_term}'
            """
        elif search_type == "Country":
            query = f"SELECT m.*, '' as additional_info FROM movie m WHERE m.mov_rel_country = '{search_term}'"
        elif search_type == "Rating":
            if not search_term.isdigit():
                messagebox.showerror("Input Error", "Please enter a valid rating (numbers only)")
                return
            query = f"""
                SELECT m.*, r.rev_stars as additional_info
                FROM movie m
                JOIN rating r ON m.mov_id = r.mov_id
                WHERE r.rev_stars = '{search_term}'
            """  
        cursor.execute(query)
        results = cursor.fetchall()

        for row in self.tree.get_children():
            self.tree.delete(row)

        if not results:
            messagebox.showinfo("No Results", "There is no result")
            return

        for row in results:
            self.tree.insert("", tk.END, values=row)

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    create_db_query_path = os.path.join(script_dir, 'create_db_query.txt')
    insert_data_path = os.path.join(script_dir, 'insert_data.txt')

    conn = create_connection()
    create_database(conn)
    execute_sql_file(conn, create_db_query_path)
    execute_sql_file(conn, insert_data_path)
    root = tk.Tk()
    app = MovieDatabaseApp(root, conn)
    root.mainloop()
    conn.close()
