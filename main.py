import tkinter as tk
from gui.main_window import StockChartApp  # Changed back to relative import

def main():
    root = tk.Tk()
    app = StockChartApp(root)
    root.geometry("1000x600")
    root.mainloop()

if __name__ == "__main__":
    main()
