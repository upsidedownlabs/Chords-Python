import tkinter as tk 
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import plotly.graph_objects as go

class CSVPlotterApp:
    def __init__(self, root):                 # Initialize the main application window
        self.root = root
        self.root.title("CSV Plotter GUI")
        self.filename = None                  # Variable to store the selected CSV file name
        self.data = None                      # Variable to store the loaded data
        self.create_widgets()                 # Call the method to create widgets

    def create_widgets(self):
        # Create a frame for buttons and file name display
        self.control_frame = tk.Frame(self.root, padx=10, pady=10)
        self.control_frame.pack(pady=10)

        # Button to load CSV file
        self.load_button = tk.Button(self.control_frame, text="Load CSV", command=self.load_csv, bg='#4CAF50', fg='white', font=('Arial', 12))
        self.load_button.pack(side=tk.LEFT, padx=5)

        # Label to display the name of the selected CSV file
        self.file_label = tk.Label(self.control_frame, text="No file selected", font=('Arial', 12))
        self.file_label.pack(side=tk.LEFT, padx=5)

        # Frame for dropdown menu
        self.dropdown_frame = tk.Frame(self.root, padx=10, pady=10)
        self.dropdown_frame.pack(pady=10)

        self.dropdown_label = tk.Label(self.dropdown_frame, text="Select Channel to Plot:", font=('Arial', 12))
        self.dropdown_label.pack(side=tk.LEFT)

        # Dropdown menu for channel selection
        self.channel_selection = tk.StringVar()
        self.dropdown_menu = ttk.Combobox(self.dropdown_frame, textvariable=self.channel_selection, state="normal", font=('Arial', 12))
        self.dropdown_menu.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Button to plot data
        self.plot_button = tk.Button(self.root, text="Plot Data", command=self.plot_data, bg='#2196F3', fg='white', font=('Arial', 12))
        self.plot_button.pack(pady=10)

    def load_csv(self):
        self.filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])   # Open file dialog to select CSV file
        if self.filename:
            try:
                with open(self.filename, "r", encoding="utf-8") as f:                    # Open the selected CSV file
                    lines = f.readlines()                                                # Read all lines into a list for header detection

                header_index = None                                                      # Initialize the variable to track where (Header)'Counter' appears
                for i, line in enumerate(lines):                                         # Iterate through lines to find the header line
                    if "Counter" in line:
                        header_index = i                                                 # Store the index of the line containing 'Counter'
                        break                                                            # If found, break the loop

                if header_index is None:                                                 # If no header row with 'Counter' was found, show error and exit
                    messagebox.showerror("Error", "CSV file must contain a 'Counter' column.")
                    return

                # Now read CSV again, skipping metadata lines before the header
                self.data = pd.read_csv(self.filename, skiprows=header_index, header=0)

                # Ensure 'Counter' column is present
                if 'Counter' not in self.data.columns:
                    messagebox.showerror("Error", "CSV file must contain a 'Counter' column.")
                    return

                # Setup dropdown based on available channels
                self.setup_dropdown_menu()
                self.file_label.config(text=f"File: {self.filename.split('/')[-1]}")

            except Exception as e:
                messagebox.showerror("Error", f"Could not load CSV file: {e}")

    def setup_dropdown_menu(self):
        # Get available channel columns
        channel_columns = [col for col in self.data.columns if 'Channel' in col]

        # Populate dropdown menu with available channels
        self.dropdown_menu['values'] = channel_columns
        if channel_columns:
            self.channel_selection.set(channel_columns[0])  # Default selection to the first channel

    def plot_data(self):
        """Creates an interactive plot of the selected data channel using Plotly."""
        selected_channel = self.channel_selection.get()   # Get the selected channel
        if not selected_channel:
            messagebox.showerror("Error", "No channel selected for plotting")
            return

        fig = go.Figure()  # Plot the selected channel using Plotly
        fig.add_trace(go.Scatter(x=self.data.index, y=self.data[selected_channel], mode='lines', name=selected_channel))
        
        fig.update_layout(
            title=f"Channel: {selected_channel}",
            xaxis_title="Index",
            yaxis_title="Value",
            template="plotly_white"
        )
        fig.show()               # Display the plot in a new window

if __name__ == "__main__":
    root = tk.Tk()               # Create the main Tkinter root window
    app = CSVPlotterApp(root)    # Create an instance of the CSVPlotterApp class
    root.mainloop()              # Start the Tkinter main loop