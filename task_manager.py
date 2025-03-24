import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime
import os
from tkinter import messagebox, simpledialog

class Task:
    def __init__(self, title, description, due_date, priority, category=None):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.category = category or "Uncategorized"
        self.completed = False
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'priority': self.priority,
            'category': self.category,
            'completed': self.completed,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(
            data['title'], 
            data['description'], 
            data['due_date'], 
            data['priority'], 
            data.get('category', 'Uncategorized')
        )
        task.completed = data['completed']
        task.created_at = data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return task

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("TaskMaster - Login")
        self.geometry("400x300")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create login frame
        self.login_frame = ctk.CTkFrame(self, corner_radius=15)
        self.login_frame.pack(expand=True, padx=20, pady=20, fill="both")
        
        # Logo or Title
        self.logo_label = ctk.CTkLabel(
            self.login_frame, 
            text="TaskMaster", 
            font=("Helvetica", 24, "bold")
        )
        self.logo_label.pack(pady=(40, 20))
        
        # Username Entry
        self.username_entry = ctk.CTkEntry(
            self.login_frame, 
            placeholder_text="Username", 
            width=300
        )
        self.username_entry.pack(pady=10)
        
        # Password Entry
        self.password_entry = ctk.CTkEntry(
            self.login_frame, 
            placeholder_text="Password", 
            show="*", 
            width=300
        )
        self.password_entry.pack(pady=10)
        
        # Login Button
        self.login_button = ctk.CTkButton(
            self.login_frame, 
            text="Login", 
            command=self.login,
            width=300
        )
        self.login_button.pack(pady=20)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username and password:
            self.destroy()
            app = TaskManagerApp()
            app.mainloop()
        else:
            messagebox.showerror("Login Failed", "Please enter username and password")

class TaskManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Configuration
        self.title("TaskMaster - Dashboard")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Custom style for Treeview
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview", 
                        background="#2a2d2e",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#343638",
                        bordercolor="#343638",
                        highlightcolor="#4a4d4e")
        style.map('Treeview', 
                  background=[('selected', '#4a4d4e')])
        
        # Tasks Storage
        self.tasks = []
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
            ("Edit", self.edit_task)
        ]
        
        for label, command in buttons:
            ctk.CTkButton(
                button_frame, 
                text=label, 
                command=command
            ).pack(side="left", padx=5)
        
        # Load initial tasks
        self.load_task_list()
    
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
        self.tasks.append(task)
        self.save_tasks()
        self.load_task_list()
        
        # Clear input fields
        for entry in [self.title_entry, self.desc_entry, self.due_entry]:
            entry.delete(0, 'end')
    
    def save_tasks(self):
        with open(self.file_path, 'w') as file:
            json.dump([task.to_dict() for task in self.tasks], file, indent=4)
    
    def load_tasks(self):
        try:
            with open(self.file_path, 'r') as file:
                self.tasks = [Task.from_dict(task) for task in json.load(file)]
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = []
    
    def load_task_list(self):
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Populate with tasks
        for task in self.tasks:
            # Unicode symbols for status
            # ✅ (Green checkmark in circle) for completed
            # ❌ (Red cross in circle) for pending
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
        for task in self.tasks:
            if task.title == task_title:
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
        self.tasks = [task for task in self.tasks if task.title != task_title]
        
        self.save_tasks()
        self.load_task_list()
    
    def edit_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task")
            return
        
        task_title = self.task_tree.item(selected_item)['values'][0]
        for task in self.tasks:
            if task.title == task_title:
                # Create a dialog to edit task details
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

def main():
    login_window = LoginWindow()
    login_window.mainloop()

if __name__ == "__main__":
    main()
