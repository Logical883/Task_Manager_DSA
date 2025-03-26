# Task Manager

## Overview
Task Manager is a Python-based application that provides an efficient way to manage tasks using a modern Graphical User Interface (GUI) built with CustomTkinter and Tkinter. The application implements advanced data structures like queues (FIFO) and stacks to provide robust task management features.

## Features
- **Modern UI Design:** 
  - Sleek, customizable interface using CustomTkinter
  - Dark and light mode support
- **Task Management:** 
  - Add new tasks with titles and descriptions
  - Remove tasks
  - Mark tasks as completed
- **Undo Operations:** 
  - Comprehensive undo functionality using a stack
  - Revert last actions (add, remove, complete)
- **Task Scheduling:** 
  - Implement First-In-First-Out (FIFO) task queue
- **Persistent Storage:** 
  - Save tasks to JSON file
  - Load previously saved tasks
- **User-Friendly Interface:** 
  - Clean and intuitive CustomTkinter-based GUI

## Prerequisites
- Python 3.7+
- CustomTkinter
- tkinter

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/task-manager.git
   cd task-manager
   ```

2. Install required dependencies:
   ```bash
   pip install customtkinter
   ```

3. Ensure you have Python installed:
   ```bash
   python --version
   ```

## Running the Application
```bash
python task_manager.py
```

## How to Use
1. **Adding a Task**
   - Enter task title in the first entry field
   - Enter task description in the second entry field
   - Click "Add Task"

2. **Completing a Task**
   - Select a task from the list
   - Click "Complete Task"

3. **Removing a Task**
   - Select a task from the list
   - Click "Remove Task"

4. **Undoing Actions**
   - Click "Undo" to revert the last action

5. **Saving Tasks**
   - Click "Save Tasks" to save current tasks to a JSON file
   - Tasks are automatically loaded when you restart the application

## Customization
- **Theme Switching:** 
  - The application supports both light and dark modes
  - Easily switch between system default, dark, and light themes

## Data Structures Used
- **Queue (task_queue):** Manages tasks in a First-In-First-Out order
- **Stack (undo_stack):** Enables undo functionality by tracking actions

## Error Handling
- Input validation prevents adding tasks without title or description
- Error messages guide users through potential issues
- Graceful handling of file operations

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Dependencies
- CustomTkinter: Modern UI library for Tkinter
- tkinter: Standard GUI library for Python
- json: For persistent storage

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Authors
- Group 16 DSA Project Team

## Acknowledgments
- CustomTkinter Library
- Python Software Foundation
- Tkinter Documentation
