#!/usr/bin/env python3
# Prevent __pycache__ creation
import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from patch_manager import PatchManager

class PatchManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows Patch Manager")
        self.root.geometry("1000x700")
        
        self.patch_manager = PatchManager()
        self.programs = []
        self.selected_programs = {}  # Track selected programs for updates
        self.checkbox_vars = {}  # Store checkbox variables
        self.program_frames = []  # Store program frame widgets
        
        self.setup_ui()
        self.initial_scan()
        
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Windows Patch Manager", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons
        ttk.Button(buttons_frame, text="Scan Programs", command=self.scan_programs).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(buttons_frame, text="Check Updates", command=self.check_updates).grid(row=0, column=1, padx=5)
        ttk.Button(buttons_frame, text="Update Selected", command=self.update_selected).grid(row=0, column=2, padx=5)
        ttk.Button(buttons_frame, text="Update All", command=self.update_all).grid(row=0, column=3, padx=5)
        ttk.Button(buttons_frame, text="Export List", command=self.export_list).grid(row=0, column=4, padx=5)
        ttk.Button(buttons_frame, text="Settings", command=self.show_settings).grid(row=0, column=5, padx=(5, 0))
        
        # Selection frame
        selection_frame = ttk.Frame(main_frame)
        selection_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(selection_frame, text="Select All", command=self.select_all).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(selection_frame, text="Select None", command=self.select_none).grid(row=0, column=1, padx=5)
        ttk.Button(selection_frame, text="Select Updates Only", command=self.select_updates_only).grid(row=0, column=2, padx=5)
        
        # Program list frame
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # Header frame for column labels
        header_frame = ttk.Frame(list_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        header_frame.columnconfigure(1, weight=1)
        
        # Column headers
        ttk.Label(header_frame, text="Select", width=8, font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(5, 10))
        ttk.Label(header_frame, text="Program Name", width=35, font=('Arial', 9, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Label(header_frame, text="Current Version", width=18, font=('Arial', 9, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        ttk.Label(header_frame, text="Update Available", width=15, font=('Arial', 9, 'bold')).grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        ttk.Label(header_frame, text="New Version", width=18, font=('Arial', 9, 'bold')).grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        ttk.Label(header_frame, text="Source", width=10, font=('Arial', 9, 'bold')).grid(row=0, column=5, sticky=tk.W)
        
        # Add separator line
        separator = ttk.Separator(header_frame, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Scrollable frame for program list
        canvas = tk.Canvas(list_frame, height=300, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # Configure scrollable frame
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self._on_frame_configure()
        )
        
        # Create window with proper configuration
        self.canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind canvas resize to update window width
        def _on_canvas_configure(event):
            # Update the width of the scrollable frame to match canvas width
            canvas_width = event.width
            canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        canvas.bind("<Configure>", _on_canvas_configure)
        
        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Store canvas reference for scrolling
        self.canvas = canvas
        
        # Improved mousewheel handling
        def _on_mousewheel(event):
            # Check if the canvas can scroll
            if self.canvas.winfo_exists():
                # More responsive scrolling
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mousewheel to both canvas and scrollable frame
        canvas.bind("<MouseWheel>", _on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Also bind to the main window when mouse is over the list area
        def _bind_to_mousewheel(event):
            self.root.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.root.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Status and progress frame
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(status_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Log Output", padding="5")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for the main frame
        main_frame.rowconfigure(5, weight=1)
    
    def _on_frame_configure(self):
        """Update scroll region when frame size changes"""
        if self.canvas.winfo_exists():
            # Update the scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            # Ensure the canvas window width matches the canvas width
            canvas_width = self.canvas.winfo_width()
            if canvas_width > 1:  # Make sure canvas has been drawn
                self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def initial_scan(self):
        """Perform initial scan when GUI starts"""
        self.log_message("Starting initial program scan...")
        threading.Thread(target=self._initial_scan_worker, daemon=True).start()
    
    def _initial_scan_worker(self):
        """Worker thread for initial scan"""
        try:
            self.start_progress()
            self.update_status("Scanning installed programs...")
            
            self.programs = self.patch_manager.scan_programs()
            
            self.root.after(0, self.update_programs_display, self.programs)
            self.root.after(0, self.stop_progress)
            self.root.after(0, self.update_status, f"Found {len(self.programs)} installed programs")
            self.root.after(0, self.log_message, f"Initial scan complete. Found {len(self.programs)} programs.")
            
        except Exception as e:
            self.root.after(0, self.stop_progress)
            self.root.after(0, self.show_error, f"Initial scan failed: {e}")
            self.root.after(0, self.log_message, f"Initial scan error: {e}")
    
    def scan_programs(self):
        """Rescan for programs"""
        self.log_message("Rescanning programs...")
        threading.Thread(target=self._scan_worker, daemon=True).start()
    
    def _scan_worker(self):
        """Worker thread for program scanning"""
        try:
            self.start_progress()
            self.update_status("Scanning installed programs...")
            
            self.programs = self.patch_manager.scan_programs(force_rescan=True)
            
            self.root.after(0, self.update_programs_display, self.programs)
            self.root.after(0, self.stop_progress)
            self.root.after(0, self.update_status, f"Found {len(self.programs)} installed programs")
            self.root.after(0, self.log_message, f"Program scan complete. Found {len(self.programs)} programs.")
            
        except Exception as e:
            self.root.after(0, self.stop_progress)
            self.root.after(0, self.show_error, f"Program scan failed: {e}")
            self.root.after(0, self.log_message, f"Program scan error: {e}")
    
    def check_updates(self):
        """Check for updates"""
        if not self.programs:
            self.show_error("No programs found. Please scan for programs first.")
            return
            
        self.log_message("Checking for updates...")
        threading.Thread(target=self._check_updates_worker, daemon=True).start()
    
    def _check_updates_worker(self):
        """Worker thread for update checking"""
        try:
            self.start_progress()
            self.update_status("Checking for updates...")
            
            # Update the programs with check results
            updated_programs = self.patch_manager.check_updates()
            self.programs = self.patch_manager.programs  # Get the updated programs list
            updates_available = sum(1 for p in self.programs if p.update_available)
            
            self.root.after(0, self.update_programs_display, self.programs)
            self.root.after(0, self.stop_progress)
            self.root.after(0, self.update_status, f"Found {updates_available} updates available")
            self.root.after(0, self.log_message, f"Update check complete. {updates_available} updates available.")
            
        except Exception as e:
            self.root.after(0, self.stop_progress)
            self.root.after(0, self.show_error, f"Update check failed: {e}")
            self.root.after(0, self.log_message, f"Update check error: {e}")
    
    def update_all(self):
        """Update all programs with available updates"""
        programs_to_update = [p for p in self.programs if p.update_available]
        if not programs_to_update:
            self.show_error("No updates available.")
            return
            
        if messagebox.askyesno("Confirm Update", f"Update {len(programs_to_update)} programs?"):
            self.log_message(f"Starting update for {len(programs_to_update)} programs...")
            threading.Thread(target=self._update_worker, args=(programs_to_update,), daemon=True).start()
    
    def update_selected(self):
        """Update only selected programs"""
        selected_programs = [p for p in self.programs if self.selected_programs.get(p.name, False) and p.update_available]
        
        if not selected_programs:
            self.show_error("No selected programs with updates available.")
            return
            
        if messagebox.askyesno("Confirm Update", f"Update {len(selected_programs)} selected programs?"):
            self.log_message(f"Starting update for {len(selected_programs)} selected programs...")
            threading.Thread(target=self._update_worker, args=(selected_programs,), daemon=True).start()
    
    def _update_worker(self, programs_to_update):
        """Worker thread for updating programs"""
        try:
            self.start_progress()
            self.update_status(f"Updating {len(programs_to_update)} programs...")
            
            # Update programs one by one
            success_count = 0
            for program in programs_to_update:
                try:
                    self.patch_manager.update_program(program.name)
                    success_count += 1
                    self.root.after(0, self.log_message, f"✓ Updated {program.name}")
                except Exception as e:
                    self.root.after(0, self.log_message, f"✗ Failed to update {program.name}: {e}")
            
            self.root.after(0, self.stop_progress)
            self.root.after(0, self.update_status, f"Updates complete: {success_count}/{len(programs_to_update)} successful")
            self.root.after(0, self.log_message, f"Update process complete. {success_count}/{len(programs_to_update)} successful.")
            
            # Refresh the program list
            self.root.after(0, self.check_updates)
            
        except Exception as e:
            self.root.after(0, self.stop_progress)
            self.root.after(0, self.show_error, f"Update failed: {e}")
            self.root.after(0, self.log_message, f"Update error: {e}")
    
    def export_list(self):
        """Export program list to JSON"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Program List",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                self.patch_manager.export_program_list(filename)
                self.log_message(f"Program list exported to {filename}")
                messagebox.showinfo("Export Complete", f"Program list exported to {filename}")
                
        except Exception as e:
            self.show_error(f"Export failed: {e}")
    
    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog not implemented yet.\nEdit config.json manually for now.")
    
    def on_checkbox_toggle(self, program_name):
        """Handle checkbox toggle"""
        is_selected = self.checkbox_vars[program_name].get()
        self.selected_programs[program_name] = is_selected
    
    def select_all(self):
        """Select all programs"""
        for program in self.programs:
            self.selected_programs[program.name] = True
            if program.name in self.checkbox_vars:
                self.checkbox_vars[program.name].set(True)
    
    def select_none(self):
        """Deselect all programs"""
        self.selected_programs.clear()
        for var in self.checkbox_vars.values():
            var.set(False)
    
    def select_updates_only(self):
        """Select only programs with available updates"""
        self.selected_programs.clear()
        for program in self.programs:
            should_select = program.update_available
            self.selected_programs[program.name] = should_select
            if program.name in self.checkbox_vars:
                self.checkbox_vars[program.name].set(should_select)
    
    def update_programs_display(self, programs):
        """Update the program list display"""
        self.programs = programs
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the program list display with checkboxes"""
        # Clear existing program frames
        for frame in self.program_frames:
            frame.destroy()
        self.program_frames.clear()
        self.checkbox_vars.clear()
        
        # Configure the scrollable frame columns
        self.scrollable_frame.columnconfigure(0, weight=1)
        
        # Create checkbox widgets for each program
        for i, program in enumerate(self.programs):
            # Create frame for this program row
            program_frame = ttk.Frame(self.scrollable_frame)
            program_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=1, padx=5)
            program_frame.columnconfigure(1, weight=1)
            self.program_frames.append(program_frame)
            
            # Bind mousewheel to program frame for better scrolling
            def _on_mousewheel_frame(event):
                if self.canvas.winfo_exists():
                    self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            program_frame.bind("<MouseWheel>", _on_mousewheel_frame)
            
            # Alternate row colors for better readability
            bg_color = '#f0f0f0' if i % 2 == 0 else '#ffffff'
            
            # Create checkbox variable
            var = tk.BooleanVar()
            var.set(self.selected_programs.get(program.name, False))
            self.checkbox_vars[program.name] = var
            
            # Checkbox
            checkbox = ttk.Checkbutton(
                program_frame, 
                variable=var,
                command=lambda pname=program.name: self.on_checkbox_toggle(pname)
            )
            checkbox.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            
            # Program name - make it bold if update is available
            name_font = ('Arial', 9, 'bold') if program.update_available else ('Arial', 9)
            name_label = ttk.Label(program_frame, text=program.name, width=35, anchor='w', font=name_font)
            name_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
            
            # Current version
            version_label = ttk.Label(program_frame, text=program.version, width=18, anchor='w')
            version_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
            
            # Update available - use different styling
            update_text = "✓ Yes" if program.update_available else "No"
            update_color = 'blue' if program.update_available else 'gray'
            update_label = ttk.Label(program_frame, text=update_text, width=15, anchor='w', foreground=update_color)
            update_label.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
            
            # Available version
            available_version = program.available_version if program.update_available else ""
            available_font = ('Arial', 9, 'bold') if program.update_available else ('Arial', 9)
            available_label = ttk.Label(program_frame, text=available_version, width=18, anchor='w', font=available_font)
            available_label.grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
            
            # Source
            source_label = ttk.Label(program_frame, text=program.source, width=10, anchor='w')
            source_label.grid(row=0, column=5, sticky=tk.W)
            
            # Set foreground color for update available items
            if program.update_available:
                available_label.configure(foreground='blue')
        
        # Update scroll region with better timing
        self.scrollable_frame.update_idletasks()
        # Force immediate update and then schedule another one
        self._on_frame_configure()
        self.root.after(10, self._on_frame_configure)
    
    def update_status(self, message):
        """Update status label"""
        self.progress_var.set(message)
    
    def start_progress(self):
        """Start progress bar animation"""
        self.progress_bar.start(10)
    
    def stop_progress(self):
        """Stop progress bar animation"""
        self.progress_bar.stop()
    
    def log_message(self, message):
        """Add message to log output"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)

def main():
    try:
        root = tk.Tk()
        app = PatchManagerGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Startup Error", f"Failed to start GUI: {e}")

if __name__ == "__main__":
    main()
