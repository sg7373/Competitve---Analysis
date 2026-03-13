import tkinter as tk
from tkinter import ttk
import styles  # Import the styles module

class ExampleDashboard:
    def __init__(self, master):
        # Apply custom styling
        self.style_manager = styles.AppStyles()
        self.style = self.style_manager.configure_styles(master)
        
        # Create a gradient background canvas
        self.canvas = tk.Canvas(master, width=800, height=600)
        self.canvas.pack(fill='both', expand=True)
        
        # Create gradient background
        styles.GradientBackground.create_gradient_background(
            self.canvas, 800, 600, 
            self.style_manager.PRIMARY_COLOR, 
            '#ffffff'
        )
        
        # Create main frame with white background
        main_frame = tk.Frame(self.canvas, bg='white')
        self.canvas.create_window(400, 300, window=main_frame, width=750, height=550)
        
        # Use custom buttons
        custom_button = styles.AnimatedButton(
            main_frame, 
            text="Custom Dashboard Button", 
            style='TButton'
        )
        custom_button.pack(pady=20)
        
        # Use custom message box
        styles.create_custom_messagebox(
            "Welcome", 
            "This is a custom styled dashboard!"
        )