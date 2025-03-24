import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime
import os

class Task:
    def __init__(self, title, description, due_date, priority):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.completed = False

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'priority': self.priority,
            'completed': self.completed
        }
    
    @classmethod
    def from_dict(cls, data):
        task = cls(data['title'], data['description'], data['due_date'], data['priority'])
        task.completed = data['completed']
        return task

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        return None

    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def peek(self):
        if not self.is_empty():
            return self.items[0]
        return None

    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

class TaskManager:
    def __init__(self):
        self.task_queue = Queue()  # For task scheduling (FIFO)
        self.undo_stack = Stack()  # For undo operations
        self.tasks = []  # List to store all tasks
        self.file_path = "tasks.json"

    def add_task(self, task):
        # Add task to both the list and queue
        self.tasks.append(task)
        self.task_queue.enqueue(task)
        # Save the operation for undo
        self.undo_stack.push(("add", task))

    def remove_task(self, task):
        if task in self.tasks:
            # Remove task from the list
            self.tasks.remove(task)
            # Save the operation for undo
            self.undo_stack.push(("remove", task))
            # Recreate the queue with the remaining tasks
            self._rebuild_queue()

    def complete_task(self, task):
        if task in self.tasks:
            old_state = task.completed
            task.completed = True
            # Save the operation for undo
            self.undo_stack.push(("complete", task, old_state))
            # Rebuild the queue
            self._rebuild_queue()

    def _rebuild_queue(self):
        # Rebuild the queue based on the current task list
        # Only include non-completed tasks
        self.task_queue = Queue()
        for task in self.tasks:
            if not task.completed:
                self.task_queue.enqueue(task)

    def undo(self):
        if not self.undo_stack.is_empty():
            operation = self.undo_stack.pop()
            if operation[0] == "add":
                task = operation[1]
                self.tasks.remove(task)
                self._rebuild_queue()
                return f"Undid adding task: {task.title}"
            elif operation[0] == "remove":
                task = operation[1]
                self.tasks.append(task)
                self._rebuild_queue()
                return f"Undid removing task: {task.title}"
            elif operation[0] == "complete":
                task = operation[1]
                old_state = operation[2]
                task.completed = old_state
                self._rebuild_queue()
                return f"Undid completing task: {task.title}"
        return "Nothing to undo"

    def save_to_file(self, file_path=None):
        if file_path:
            self.file_path = file_path
        
        tasks_data = [task.to_dict() for task in self.tasks]
        with open(self.file_path, 'w') as file:
            json.dump(tasks_data, file)

    def load_from_file(self, file_path=None):
        if file_path:
            self.file_path = file_path
        
        try:
            with open(self.file_path, 'r') as file:
                tasks_data = json.load(file)
                self.tasks = [Task.from_dict(task_data) for task_data in tasks_data]
                self._rebuild_queue()
                return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    def get_next_task(self):
        return self.task_queue.peek()

    def get_all_tasks(self):
        return self.tasks

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self.task_manager = TaskManager()
        
        # Try to load tasks from file
        self.task_manager.load_from_file()
        
        self._create_widgets()
        self._update_task_list()
        
    def _create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tasks tab
        self.tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_frame, text="Tasks")
        
        # Queue tab
        self.queue_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.queue_frame, text="Task Queue")
        
        # Undo History tab
        self.undo_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.undo_frame, text="Undo History")
        
        # Setup Tasks tab
        self._setup_tasks_tab()
        
        # Setup Queue tab
        self._setup_queue_tab()
        
        # Setup Undo History tab
        self._setup_undo_tab()
        
        # Add menu
        self._create_menu()
        
    def _setup_tasks_tab(self):
        # Task input frame
        input_frame = ttk.LabelFrame(self.tasks_frame, text="Add New Task")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Task title
        ttk.Label(input_frame, text="Title:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Task description
        ttk.Label(input_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.desc_entry = ttk.Entry(input_frame, width=30)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Due date
        ttk.Label(input_frame, text="Due Date (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Priority
        ttk.Label(input_frame, text="Priority:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.priority_combobox = ttk.Combobox(input_frame, values=["High", "Medium", "Low"], width=10)
        self.priority_combobox.grid(row=1, column=3, padx=5, pady=5)
        self.priority_combobox.current(1)  # Set default to Medium
        
        # Add task button
        ttk.Button(input_frame, text="Add Task", command=self._add_task).grid(row=2, column=1, padx=5, pady=10)
        
        # Task list frame
        list_frame = ttk.LabelFrame(self.tasks_frame, text="Task List")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Task list
        columns = ("Title", "Description", "Due Date", "Priority", "Status")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, width=100)
        
        self.task_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for the treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.task_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.tasks_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Complete task button
        ttk.Button(buttons_frame, text="Complete Task", command=self._complete_task).pack(side=tk.LEFT, padx=5)
        
        # Remove task button
        ttk.Button(buttons_frame, text="Remove Task", command=self._remove_task).pack(side=tk.LEFT, padx=5)
        
        # Undo button
        ttk.Button(buttons_frame, text="Undo", command=self._undo_action).pack(side=tk.LEFT, padx=5)
        
    def _setup_queue_tab(self):
        # Queue visualization frame
        queue_viz_frame = ttk.LabelFrame(self.queue_frame, text="Task Queue (FIFO Order)")
        queue_viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Queue display
        self.queue_listbox = tk.Listbox(queue_viz_frame, height=15)
        self.queue_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Next task frame
        next_task_frame = ttk.LabelFrame(self.queue_frame, text="Next Task in Queue")
        next_task_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Next task info
        self.next_task_label = ttk.Label(next_task_frame, text="No tasks in queue")
        self.next_task_label.pack(padx=5, pady=5)
        
        # Update queue display
        self._update_queue_display()
        
    def _setup_undo_tab(self):
        # Undo stack visualization frame
        undo_viz_frame = ttk.LabelFrame(self.undo_frame, text="Undo Stack")
        undo_viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Undo stack display
        self.undo_listbox = tk.Listbox(undo_viz_frame, height=15)
        self.undo_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Undo button
        ttk.Button(self.undo_frame, text="Undo Last Action", command=self._undo_action).pack(pady=10)
        
        # Update undo display
        self._update_undo_display()
        
    def _create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self._new_task_list)
        file_menu.add_command(label="Open", command=self._load_tasks)
        file_menu.add_command(label="Save", command=self._save_tasks)
        file_menu.add_command(label="Save As", command=self._save_tasks_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
    def _add_task(self):
        title = self.title_entry.get().strip()
        description = self.desc_entry.get().strip()
        due_date = self.date_entry.get().strip()
        priority = self.priority_combobox.get()
        
        if not title:
            messagebox.showwarning("Warning", "Task title cannot be empty")
            return
        
        # Validate due date format
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Warning", "Date format should be YYYY-MM-DD")
                return
        
        # Create and add new task
        new_task = Task(title, description, due_date, priority)
        self.task_manager.add_task(new_task)
        
        # Clear input fields
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        
        # Update displays
        self._update_task_list()
        self._update_queue_display()
        self._update_undo_display()
        
        # Auto-save
        self.task_manager.save_to_file()
        
    def _complete_task(self):
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to complete")
            return
        
        item_id = selection[0]
        task_index = int(self.task_tree.item(item_id)["values"][-1])
        
        if task_index < len(self.task_manager.tasks):
            task = self.task_manager.tasks[task_index]
            if not task.completed:
                self.task_manager.complete_task(task)
                # Update displays
                self._update_task_list()
                self._update_queue_display()
                self._update_undo_display()
                # Auto-save
                self.task_manager.save_to_file()
            else:
                messagebox.showinfo("Info", "Task is already completed")
        
    def _remove_task(self):
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to remove")
            return
        
        item_id = selection[0]
        task_index = int(self.task_tree.item(item_id)["values"][-1])
        
        if task_index < len(self.task_manager.tasks):
            task = self.task_manager.tasks[task_index]
            self.task_manager.remove_task(task)
            # Update displays
            self._update_task_list()
            self._update_queue_display()
            self._update_undo_display()
            # Auto-save
            self.task_manager.save_to_file()
        
    def _undo_action(self):
        message = self.task_manager.undo()
        messagebox.showinfo("Undo", message)
        # Update displays
        self._update_task_list()
        self._update_queue_display()
        self._update_undo_display()
        # Auto-save
        self.task_manager.save_to_file()
        
    def _update_task_list(self):
        # Clear current items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Add tasks to treeview
        for i, task in enumerate(self.task_manager.tasks):
            status = "Completed" if task.completed else "Pending"
            self.task_tree.insert("", tk.END, values=(
                task.title,
                task.description,
                task.due_date,
                task.priority,
                status,
                i  # Store task index as last column (hidden)
            ))
        
    def _update_queue_display(self):
        # Clear current items
        self.queue_listbox.delete(0, tk.END)
        
        # Create a temporary copy of the queue
        temp_queue = Queue()
        queue_items = []
        
        # Dequeue all items from the task queue
        while not self.task_manager.task_queue.is_empty():
            task = self.task_manager.task_queue.dequeue()
            queue_items.append(task)
            temp_queue.enqueue(task)
        
        # Restore the original queue
        self.task_manager.task_queue = temp_queue
        
        # Display items in the listbox
        for task in queue_items:
            self.queue_listbox.insert(tk.END, f"{task.title} - {task.priority}")
        
        # Update next task label
        next_task = self.task_manager.get_next_task()
        if next_task:
            self.next_task_label.config(text=f"Next: {next_task.title} - {next_task.priority}")
        else:
            self.next_task_label.config(text="No tasks in queue")
        
    def _update_undo_display(self):
        # Clear current items
        self.undo_listbox.delete(0, tk.END)
        
        # Create a temporary copy of the stack
        temp_stack = Stack()
        stack_items = []
        
        # Pop all items from the undo stack
        while not self.task_manager.undo_stack.is_empty():
            operation = self.task_manager.undo_stack.pop()
            stack_items.append(operation)
            temp_stack.push(operation)
        
        # Restore the original stack
        while not temp_stack.is_empty():
            self.task_manager.undo_stack.push(temp_stack.pop())
        
        # Display items in reverse order (top of stack first)
        for operation in reversed(stack_items):
            if operation[0] == "add":
                self.undo_listbox.insert(tk.END, f"Add: {operation[1].title}")
            elif operation[0] == "remove":
                self.undo_listbox.insert(tk.END, f"Remove: {operation[1].title}")
            elif operation[0] == "complete":
                self.undo_listbox.insert(tk.END, f"Complete: {operation[1].title}")
        
    def _new_task_list(self):
        if messagebox.askyesno("New", "Create a new task list? All current tasks will be lost."):
            self.task_manager = TaskManager()
            self._update_task_list()
            self._update_queue_display()
            self._update_undo_display()
        
    def _load_tasks(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            if self.task_manager.load_from_file(file_path):
                self._update_task_list()
                self._update_queue_display()
                self._update_undo_display()
                messagebox.showinfo("Success", "Tasks loaded successfully")
            else:
                messagebox.showerror("Error", "Failed to load tasks")
        
    def _save_tasks(self):
        if self.task_manager.file_path:
            self.task_manager.save_to_file()
            messagebox.showinfo("Success", "Tasks saved successfully")
        else:
            self._save_tasks_as()
        
    def _save_tasks_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.task_manager.save_to_file(file_path)
            messagebox.showinfo("Success", "Tasks saved successfully")
        
    def _show_about(self):
        messagebox.showinfo(
            "About Task Manager",
            "Task Manager Application\n\n" +
            "Created for COE 363 Project\n" +
            "Date: March 2025\n\n" +
            "Features:\n" +
            "- Task management with Stack and Queue data structures\n" +
            "- Undo operations\n" +
            "- Task scheduling (FIFO)\n" +
            "- File persistence (JSON)"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()


