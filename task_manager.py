import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime, timedelta
import os
from tkinter import messagebox, simpledialog
import random
import uuid
import hashlib
import sqlite3
import re


# Hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


class DatabaseManager:
    def __init__(self, db_name='users.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def add_user(self, username, password):
        hashed_password = hash_password(password)
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists

    def validate_user(self, username, password):
        hashed_password = hash_password(password)
        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        return self.cursor.fetchone() is not None


class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        raise IndexError("dequeue from an empty queue")

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)


class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        raise IndexError("pop from an empty stack")

    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        raise IndexError("peek from an empty stack")

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("TaskMaster - Login/Sign Up")
        self.geometry("600x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Background Animation Setup
        self.canvas = tk.Canvas(self, width=600, height=600, highlightthickness=0, bg='#1a1a1a')
        self.canvas.pack(fill="both", expand=True)

        # Call background animation methods
        self.particles = []
        self.create_background_animation()

        # Main Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1a1a1a", bg_color='#1a1a1a')
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Static Logo/Title
        self.logo_label = ctk.CTkLabel(self.main_frame, text="TaskMaster", font=("Helvetica", 36, "bold"),
                                       text_color="white")
        self.logo_label.pack(pady=(40, 20))

        # Create login widgets
        self.create_login_widgets()

    def create_background_animation(self):
        """Create a dynamic, moving background with particles."""
        for _ in range(50):
            x = random.randint(0, 600)
            y = random.randint(0, 500)
            size = random.randint(1, 3)
            speed = random.uniform(0.5, 2)
            color = random.choice(['white', 'light blue', 'gray'])
            particle = self.canvas.create_oval(x, y, x + size, y + size, fill=color, stipple='gray50')
            self.particles.append((particle, speed))
        self.animate_background()

    def animate_background(self):
        """Animate background particles."""
        for particle, speed in self.particles:
            self.canvas.move(particle, 0, speed)
            coords = self.canvas.coords(particle)
            if coords[1] > 500:
                self.canvas.coords(particle, coords[0], 0, coords[2], coords[3] - coords[1])
        self.after(50, self.animate_background)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Login Failed", "Please enter both username and password")
            return

        with DatabaseManager() as db:
            if db.validate_user(username, password):
                self.destroy()
                app = TaskManagerApp()
                app.mainloop()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        with DatabaseManager() as db:
            if db.add_user(username, password):
                messagebox.showinfo("Success", "Account created successfully")
                self.create_login_widgets()  # Switch back to login view
            else:
                messagebox.showerror("Error", "Username already exists")

    def create_login_widgets(self):
        # Clear existing widgets
        for widget in self.main_frame.winfo_children():
            if widget != self.logo_label:
                widget.destroy()

        # Username Entry
        self.username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Username", width=300, corner_radius=10)
        self.username_entry.pack(pady=10)

        # Password Entry
        self.password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Password", show="*", width=300,
                                           corner_radius=10)
        self.password_entry.pack(pady=10)

        # Login Button
        self.login_button = ctk.CTkButton(self.main_frame, text="Login", command=self.login, width=300,
                                          corner_radius=10)
        self.login_button.pack(pady=20)

        # Sign Up Button
        self.signup_button = ctk.CTkButton(self.main_frame, text="Sign Up", command=self.show_signup_widgets, width=300,
                                           corner_radius=10)
        self.signup_button.pack(pady=10)

    def show_signup_widgets(self):
        # Clear existing widgets
        for widget in self.main_frame.winfo_children():
            if widget != self.logo_label:
                widget.destroy()

        # Username Entry
        self.username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Username", width=300, corner_radius=10)
        self.username_entry.pack(pady=10)

        # Password Entry
        self.password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Password", show="*", width=300,
                                           corner_radius=10)
        self.password_entry.pack(pady=10)

        # Confirm Password Entry
        self.confirm_password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Confirm Password", show="*", width=300,
                                                   corner_radius=10)
        self.confirm_password_entry.pack(pady=10)

        # Create Account Button
        self.create_account_button = ctk.CTkButton(self.main_frame, text="Create Account", command=self.signup, width=300,
                                                   corner_radius=10)
        self.create_account_button.pack(pady=20)

        # Back to Login Button
        self.back_to_login_button = ctk.CTkButton(self.main_frame, text="Back to Login", command=self.create_login_widgets, width=300,
                                                  corner_radius=10)
        self.back_to_login_button.pack(pady=10)


class Task:
    def __init__(self, title, description, due_date, priority, category):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.category = category
        self.completed = False

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "category": self.category,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, task_dict):
        task = cls(
            task_dict.get("title", ""),
            task_dict.get("description", ""),
            task_dict.get("due_date", ""),
            task_dict.get("priority", "Low"),
            task_dict.get("category", "Other")
        )
        task.completed = task_dict["completed"]
        return task


class TaskManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("TaskMaster - Dashboard")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")  # Default to dark mode
        ctk.set_default_color_theme("blue")

        # Tasks Storage (using Queue)
        self.tasks = Queue()
        self.undo_stack = Stack()  # Stack for undo operations
        self.redo_stack = Stack()  # Stack for redo operations
        self.file_path = "tasks.json"
        self.load_tasks()

        # Main Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(expand=True, padx=20, pady=20, fill="both")

        # Create Widgets
        self.create_widgets()

    def create_widgets(self):
        # Left Sidebar for Task Input
        sidebar = ctk.CTkFrame(self.main_frame, width=300)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        # Sidebar Title
        ctk.CTkLabel(
            sidebar,
            text="Add New Task",
            font=("Helvetica", 18, "bold")
        ).pack(pady=(20, 10))

        # Input Fields
        input_fields = [
            ("Title", "title_entry"),
            ("Description", "desc_entry"),
            ("Due Date (YYYY-MM-DD)", "due_entry")
        ]
        for label_text, entry_name in input_fields:
            ctk.CTkLabel(sidebar, text=label_text).pack(pady=(10, 5))
            entry = ctk.CTkEntry(sidebar, width=250)
            entry.pack(pady=5)
            setattr(self, entry_name, entry)

        # Priority Dropdown
        ctk.CTkLabel(sidebar, text="Priority").pack(pady=(10, 5))
        self.priority_combobox = ctk.CTkComboBox(
            sidebar,
            values=["High", "Medium", "Low"],
            width=250
        )
        self.priority_combobox.pack(pady=5)

        # Category Dropdown
        ctk.CTkLabel(sidebar, text="Category").pack(pady=(10, 5))
        self.category_combobox = ctk.CTkComboBox(
            sidebar,
            values=["Work", "Personal", "Study", "Other"],
            width=250
        )
        self.category_combobox.pack(pady=5)

        # Add Task Button
        add_button = ctk.CTkButton(
            sidebar,
            text="Add Task",
            command=self.add_task,
            width=250
        )
        add_button.pack(pady=20)

        # Appearance Mode Toggle
        ctk.CTkLabel(sidebar, text="Appearance Mode").pack(pady=(20, 5))
        self.appearance_mode_toggle = ctk.CTkComboBox(
            sidebar,
            values=["Dark", "Light"],
            command=self.toggle_appearance_mode,
            width=250
        )
        self.appearance_mode_toggle.set("Dark")  # Default to dark mode
        self.appearance_mode_toggle.pack(pady=5)

        # Right Section for Task List
        task_list_frame = ctk.CTkFrame(self.main_frame)
        task_list_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        # Task List Title
        ctk.CTkLabel(
            task_list_frame,
            text="Task List",
            font=("Helvetica", 18, "bold")
        ).pack(pady=(20, 10))

        # Task Listbox with Treeview
        self.task_tree = ttk.Treeview(
            task_list_frame,
            columns=("Title", "Priority", "Due Date", "Category", "Status"),
            show="headings",
            style="Treeview"
        )

        # Configure columns
        column_configs = [
            ("Title", 200),
            ("Priority", 100),
            ("Due Date", 100),
            ("Category", 100),
            ("Status", 100)
        ]
        for col, width in column_configs:
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, anchor="center", width=width)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(task_list_frame, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscroll=scrollbar.set)
        self.task_tree.pack(expand=True, fill="both", padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Buttons for Task Management
        button_frame = ctk.CTkFrame(task_list_frame)
        button_frame.pack(pady=10)
        buttons = [
            ("Complete", self.complete_task),
            ("Delete", self.delete_task),
            ("Edit", self.edit_task),
            ("Undo", self.undo),
            ("Redo", self.redo)
        ]
        for label, command in buttons:
            ctk.CTkButton(
                button_frame,
                text=label,
                command=command
            ).pack(side="left", padx=5)

        # Load initial tasks
        self.load_task_list()

    def toggle_appearance_mode(self, mode):
        """Toggle between dark and light modes."""
        ctk.set_appearance_mode(mode)

    def add_task(self):
        title = self.title_entry.get()
        description = self.desc_entry.get()
        due_date = self.due_entry.get()
        priority = self.priority_combobox.get()
        category = self.category_combobox.get()

        if not title:
            messagebox.showwarning("Warning", "Task title cannot be empty")
            return

        task = Task(title, description, due_date, priority, category)
        self.tasks.enqueue(task)  # Use enqueue to add the task
        self.save_tasks()
        self.undo_stack.push(("add", task))
        self.redo_stack = Stack()  # Clear redo stack after a new action

        # Clear input fields
        for entry in [self.title_entry, self.desc_entry, self.due_entry]:
            entry.delete(0, 'end')

        self.load_task_list()

    def save_tasks(self):
        with open(self.file_path, 'w') as file:
            json.dump([task.to_dict() for task in self.tasks.items], file, indent=4)

    def load_tasks(self):
        try:
            with open(self.file_path, 'r') as file:
                for task_dict in json.load(file):
                    self.tasks.enqueue(Task.from_dict(task_dict))  # Use enqueue to load tasks
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = Queue()

    def load_task_list(self):
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        # Populate with tasks
        for task in self.tasks.items:
            status_symbol = "✅" if task.completed else "❌"
            status_color = "green" if task.completed else "red"
            self.task_tree.insert("", "end", values=(
                task.title,
                task.priority,
                task.due_date,
                task.category,
                status_symbol
            ), tags=(status_color,))

        # Configure tag colors
        self.task_tree.tag_configure("green", foreground="green")
        self.task_tree.tag_configure("red", foreground="red")

    def complete_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task")
            return

        task_title = self.task_tree.item(selected_item)['values'][0]
        for task in self.tasks.items:
            if task.title == task_title:
                self.undo_stack.push(("complete", task, task.completed))
                self.redo_stack = Stack()  # Clear redo stack after a new action
                task.completed = not task.completed  # Toggle completion
                break

        self.save_tasks()
        self.load_task_list()

    def delete_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task")
            return

        task_title = self.task_tree.item(selected_item)['values'][0]
        for task in self.tasks.items:
            if task.title == task_title:
                self.tasks.items.remove(task)
                self.undo_stack.push(("delete", task))
                self.redo_stack = Stack()  # Clear redo stack after a new action
                break

        self.save_tasks()
        self.load_task_list()

    def edit_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task")
            return

        task_title = self.task_tree.item(selected_item)['values'][0]
        for task in self.tasks.items:
            if task.title == task_title:
                edit_window = ctk.CTkToplevel(self)
                edit_window.title("Edit Task")
                edit_window.geometry("400x500")

                # Title
                ctk.CTkLabel(edit_window, text="Title").pack()
                title_entry = ctk.CTkEntry(edit_window, width=300)
                title_entry.insert(0, task.title)
                title_entry.pack()

                # Description
                ctk.CTkLabel(edit_window, text="Description").pack()
                desc_entry = ctk.CTkEntry(edit_window, width=300)
                desc_entry.insert(0, task.description)
                desc_entry.pack()

                # Due Date
                ctk.CTkLabel(edit_window, text="Due Date").pack()
                due_entry = ctk.CTkEntry(edit_window, width=300)
                due_entry.insert(0, task.due_date)
                due_entry.pack()

                # Priority
                ctk.CTkLabel(edit_window, text="Priority").pack()
                priority_combo = ctk.CTkComboBox(
                    edit_window,
                    values=["High", "Medium", "Low"],
                    width=300
                )
                priority_combo.set(task.priority)
                priority_combo.pack()

                # Category
                ctk.CTkLabel(edit_window, text="Category").pack()
                category_combo = ctk.CTkComboBox(
                    edit_window,
                    values=["Work", "Personal", "Study", "Other"],
                    width=300
                )
                category_combo.set(task.category)
                category_combo.pack()

                def save_changes():
                    task.title = title_entry.get()
                    task.description = desc_entry.get()
                    task.due_date = due_entry.get()
                    task.priority = priority_combo.get()
                    task.category = category_combo.get()
                    self.save_tasks()
                    self.load_task_list()
                    edit_window.destroy()

                save_button = ctk.CTkButton(
                    edit_window,
                    text="Save Changes",
                    command=save_changes
                )
                save_button.pack(pady=20)
                break

    def undo(self):
        if self.undo_stack.is_empty():
            messagebox.showinfo("Undo", "No actions to undo")
            return

        action = self.undo_stack.pop()
        if action[0] == "add":
            task = action[1]
            self.tasks.items.remove(task)
            self.redo_stack.push(("add", task))
        elif action[0] == "delete":
            task = action[1]
            self.tasks.enqueue(task)
            self.redo_stack.push(("delete", task))
        elif action[0] == "complete":
            task, previous_state = action[1], action[2]
            task.completed = previous_state
            self.redo_stack.push(("complete", task, not previous_state))

        self.save_tasks()
        self.load_task_list()

    def redo(self):
        if self.redo_stack.is_empty():
            messagebox.showinfo("Redo", "No actions to redo")
            return

        action = self.redo_stack.pop()
        if action[0] == "add":
            task = action[1]
            self.tasks.enqueue(task)
            self.undo_stack.push(("add", task))
        elif action[0] == "delete":
            task = action[1]
            self.tasks.items.remove(task)
            self.undo_stack.push(("delete", task))
        elif action[0] == "complete":
            task, previous_state = action[1], action[2]
            task.completed = not previous_state
            self.undo_stack.push(("complete", task, previous_state))

        self.save_tasks()
        self.load_task_list()


class LandingPage(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("TaskMaster - Organize Your World")
        self.geometry("600x600")
        ctk.set_appearance_mode("light")  # Default to light mode for the landing page
        ctk.set_default_color_theme("blue")

        # Header Section
        self.header_frame = ctk.CTkFrame(self, fg_color="#007BFF", height=150, corner_radius=0)
        self.header_frame.pack(fill="x")

        # Header Text
        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text="TaskMaster",
            font=("Helvetica", 36, "bold"),
            text_color="white"
        )
        self.header_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Main Content
        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.main_frame.pack(expand=True, fill="both")

        # Main Heading
        self.main_heading = ctk.CTkLabel(
            self.main_frame,
            text="Start Organizing Your World",
            font=("Helvetica", 24, "bold"),
            text_color="#333333"
        )
        self.main_heading.pack(pady=(50, 10))

        # Subheading/Instructional Text
        self.subheading = ctk.CTkLabel(
            self.main_frame,
            text="Tap the menu button to start creating your task lists.",
            font=("Helvetica", 16),
            text_color="#666666"
        )
        self.subheading.pack(pady=(10, 30))

        # Navigation Button (Hamburger Icon)
        self.nav_button = ctk.CTkButton(
            self.main_frame,
            text="☰ Menu",
            font=("Helvetica", 18),
            fg_color="#007BFF",
            hover_color="#0056b3",
            text_color="white",
            corner_radius=10,
            command=self.open_login_window  # Navigate to the login window
        )
        self.nav_button.pack(pady=20)

    def open_login_window(self):
        """Open the Login Window."""
        self.destroy()  # Close the landing page
        login_window = LoginWindow()
        login_window.mainloop()


def main():
    try:
        # Initialize the database and add a test user
        with DatabaseManager() as db:
            db.add_user("testuser", "password123")
        landing_page = LandingPage()
        landing_page.mainloop()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while connecting to the database: {e}")


if __name__ == "__main__":
    main()
