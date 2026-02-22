import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os

# --- FILE PATH ---
FILE_PATH = r'C:\Users\Mayur\OneDrive\Documents\Mumbai House Price Prediction\mumbai_house_price_pred.csv'

# Load Data for Lookup
try:
    df = pd.read_csv(FILE_PATH)
    df = df.dropna(subset=['Location', 'Building_Name', 'Price'])
except Exception:
    df = pd.DataFrame()

class MumbaiHousingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mumbai Housing Portal")
        self.geometry("550x800")

        # hold all frames
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill = "both", expand = True)

        self.frames = {}
        for F in (Lookup, Data):
            page_name = F.__name__
            frame = F(parent = self.container, controller = self)
            self.frames[page_name] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame("Lookup")

    def show_frame(self, page_name):
        """Switch to a different page."""
        frame = self.frames[page_name]
        frame.tkraise()

#  PRICE LOOKUP
class Lookup(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="PROPERTY PRICE LOOKUP", font=("Arial", 16, "bold")).pack(pady=10)

        # Location Dropdown
        tk.Label(self, text="Select Location:").pack()
        self.locations = sorted(df['Location'].unique().tolist()) if not df.empty else []
        self.location_cb = ttk.Combobox(self, values=self.locations, state="readonly", width=40)
        self.location_cb.pack(pady=5)
        self.location_cb.bind("<<ComboboxSelected>>", self.update_buildings)

        # Building Dropdown
        tk.Label(self, text="Select Building:").pack()
        self.building_cb = ttk.Combobox(self, state="readonly", width=40)
        self.building_cb.pack(pady=5)
        self.building_cb.bind("<<ComboboxSelected>>", self.update_bhk)

        # BHK Dropdown
        tk.Label(self, text="Select BHK:").pack()
        self.bhk_cb = ttk.Combobox(self, state="readonly", width=40)
        self.bhk_cb.pack(pady=5)

        # Show Details Button
        self.show_btn = tk.Button(self, text="Show Details", command=self.display_info, 
                                  bg="#2980b9", fg="white", font=("Arial", 10, "bold"), width=25)
        self.show_btn.pack(pady=10)

        # NEW BUTTON: Switch to Sell Data Page
        self.sell_btn = tk.Button(self, text="Add Your Data For Selling", command=lambda: controller.show_frame("Data"),
                                  bg="#e67e22", fg="white", font=("Arial", 10, "bold"), width=25)
        self.sell_btn.pack(pady=5)

        # Results area
        self.result_text = tk.Text(self, height=10, width=55, state="disabled")
        self.result_text.pack(pady=10)

    def update_buildings(self, event):
        selected_loc = self.location_cb.get()
        filtered = df[df['Location'] == selected_loc]
        self.building_cb.config(values=sorted(filtered['Building_Name'].unique().tolist()))
        self.building_cb.set('')

    def update_bhk(self, event):
        selected_loc = self.location_cb.get()
        selected_bldg = self.building_cb.get()
        filtered = df[(df['Location'] == selected_loc) & (df['Building_Name'] == selected_bldg)]
        self.bhk_cb.config(values=sorted(filtered['BHK'].dropna().unique().tolist()))
        self.bhk_cb.set('')

    def display_info(self):
        loc, bldg, bhk = self.location_cb.get(), self.building_cb.get(), self.bhk_cb.get()
        if not loc or not bldg or not bhk:
            messagebox.showwarning("Error", "Please select all fields")
            return
        
        match = df[(df['Location'] == loc) & (df['Building_Name'] == bldg) & (df['BHK'] == float(bhk))]
        if not match.empty:
            row = match.iloc[0]
            info = f"Building: {row['Building_Name']}\nLocation: {row['Location']}\nBHK: {row['BHK']}\n" \
                   f"Area: {row['Carpet_Area']} sqft\nFloor: {row['Floor_Number']}\n" \
                   f"Furnished: {row['Furnished']}\nType: {row['Type']}\n" \
                   f"Price: ₹ {row['Price']:,}"
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, info)
            self.result_text.config(state="disabled")

# DATA SUBMIT
class Data(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Back Button
        tk.Button(self, text="← Back to Lookup", command=lambda: controller.show_frame("Lookup"), 
                  bg="#95a5a6", fg="white").pack(anchor="nw", padx=10, pady=10)

        tk.Label(self, text="ADD PROPERTY FOR SELLING", font=("Arial", 16, "bold")).pack(pady=10)

        # Form fields
        self.entries = {}
        form_fields = [
            ("Building Name", "entry"), ("Carpet Area", "entry"), ("Location", "entry"),
            ("BHK", "combo", [1,2,3,4,5]), ("Floor Number", "combo", list(range(0,51))),
            ("Furnished", "combo", ['Furnished', 'Semi-Furnished', 'Unfurnished']),
            ("Type", "combo", ['Flat', 'Bungalow', 'Chawl']),
            ("Bathrooms", "combo", [1,2,3,4,5]), ("Parking", "combo", ['Yes', 'No']),
            ("Lift", "combo", ['Yes', 'No']), ("Railway Station (KM)", "combo", list(range(0,11))),
            ("Total Price", "entry"), ("Available for Rent", "combo", ['Yes', 'No']),
            ("Rented Price (Optional)", "entry")
        ]

        for label_text, type, *vals in form_fields:
            tk.Label(self, text=label_text + ":").pack()
            if type == "entry":
                widget = tk.Entry(self, width=40)
            else:
                widget = ttk.Combobox(self, values=vals[0], state="readonly", width=37)
            widget.pack(pady=2)
            self.entries[label_text] = widget

        # Submit Button
        tk.Button(self, text="Submit Data", command=self.save_to_csv, bg="#27ae60", fg="white", 
                  font=("Arial", 12, "bold"), width=20).pack(pady=20)

    def save_to_csv(self):
        data = {k: v.get().strip() for k, v in self.entries.items()}
        
        # Validation
        for k, v in data.items():
            if k != "Rented Price (Optional)" and v == "":
                messagebox.showwarning("Input Error", f"Field {k} is mandatory.")
                return

        try:
            # Formatting for CSV compatibility
            final_data = {
                'Building_Name': data['Building Name'], 'Carpet_Area': int(data['Carpet Area']),
                'BHK': data['BHK'], 'Floor_Number': data['Floor Number'], 'Location': data['Location'],
                'Furnished': data['Furnished'], 'Type': data['Type'], 'Bathrooms': data['Bathrooms'],
                'Parking': data['Parking'], 'Lift': data['Lift'], 'Railway_Station-KM': data['Railway Station (KM)'],
                'Price': int(data['Total Price']), 'Available_for_Rent': data['Available for Rent'],
                'Rented_Price': int(data['Rented Price (Optional)']) if data['Rented Price (Optional)'] else 0
            }
            
            new_df = pd.DataFrame([final_data])
            file_exists = os.path.isfile(FILE_PATH)
            new_df.to_csv(FILE_PATH, mode='a', header=not file_exists, index=False)
            messagebox.showinfo("Success", "Property data added!")
            self.controller.show_frame("Lookup") # for move back
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

if __name__ == "__main__":
    app = MumbaiHousingApp()
    app.mainloop()