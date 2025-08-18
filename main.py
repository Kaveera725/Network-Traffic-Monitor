import os
import time
import psutil
from prettytable import PrettyTable, DOUBLE_BORDER
from rich.console import Console
from rich.table import Table
import tkinter as tk
from tkinter import ttk
from datetime import datetime

# Units for size conversion
UNITS = ['bytes', 'KB', 'MB', 'GB', 'TB']

# Initialize Rich console for colorful output
console = Console()

def get_size(num_bytes):
    """Convert bytes to human-readable format (e.g., KB, MB)."""
    for unit in UNITS:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"  # For very large values

def clear_console():
    """Clear the console (cross-platform)."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_network_stats(prev_sent, prev_recv):
    """Print network stats in a PrettyTable."""
    net_stats = psutil.net_io_counters()
    upload_speed = net_stats.bytes_sent - prev_sent
    download_speed = net_stats.bytes_recv - prev_recv

    table = PrettyTable()
    table.set_style(DOUBLE_BORDER)
    table.field_names = ["Total Received", "Download Speed", "Total Sent", "Upload Speed"]
    table.add_row([
        get_size(net_stats.bytes_recv),
        f"{get_size(download_speed)}/s",
        get_size(net_stats.bytes_sent),
        f"{get_size(upload_speed)}/s"
    ])
    print(table)
    return net_stats.bytes_sent, net_stats.bytes_recv

def print_network_stats_color(prev_sent, prev_recv):
    """Print network stats in a Rich Table (colored)."""
    net_stats = psutil.net_io_counters()
    upload_speed = net_stats.bytes_sent - prev_sent
    download_speed = net_stats.bytes_recv - prev_recv

    table = Table(title="Network Monitor", show_header=True, header_style="bold magenta")
    table.add_column("Total Received", style="green")
    table.add_column("Download Speed", style="blue")
    table.add_column("Total Sent", style="yellow")
    table.add_column("Upload Speed", style="red")

    table.add_row(
        get_size(net_stats.bytes_recv),
        f"{get_size(download_speed)}/s",
        get_size(net_stats.bytes_sent),
        f"{get_size(upload_speed)}/s"
    )
    console.print(table)
    return net_stats.bytes_sent, net_stats.bytes_recv

def print_all_interfaces():
    """Show stats for all network interfaces (Wi-Fi, Ethernet, etc.)."""
    net_io = psutil.net_io_counters(pernic=True)
    table = PrettyTable()
    table.field_names = ["Interface", "Total Received", "Total Sent"]

    for interface, stats in net_io.items():
        table.add_row([
            interface,
            get_size(stats.bytes_recv),
            get_size(stats.bytes_sent)
        ])
    print(table)

def log_network_usage():
    """Log network usage to a file."""
    net_stats = psutil.net_io_counters()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("network_log.txt", "a") as f:
        f.write(f"{timestamp} | Upload: {get_size(net_stats.bytes_sent)} | Download: {get_size(net_stats.bytes_recv)}\n")

def print_system_stats():
    """Print CPU and RAM usage."""
    cpu_percent = psutil.cpu_percent()
    mem = psutil.virtual_memory()

    table = PrettyTable()
    table.field_names = ["CPU Usage", "RAM Usage", "Available RAM"]
    table.add_row([
        f"{cpu_percent}%",
        f"{get_size(mem.used)}",
        f"{get_size(mem.available)}"
    ])
    print(table)

def run_cli_monitor():
    """Run the CLI-based monitor."""
    prev_stats = psutil.net_io_counters()
    prev_sent, prev_recv = prev_stats.bytes_sent, prev_stats.bytes_recv

    try:
        while True:
            time.sleep(2)
            clear_console()
            print(" Real-Time Network Monitor (Ctrl+C to stop)\n")
            prev_sent, prev_recv = print_network_stats_color(prev_sent, prev_recv)  # Use Rich for colors
            print_system_stats()  # Show CPU/RAM
            log_network_usage()   # Log to file
    except KeyboardInterrupt:
        print("\n✅ Monitoring stopped.")

def run_gui_monitor():
    """Run a simple Tkinter GUI monitor."""
    root = tk.Tk()
    root.title("Network Monitor")

    upload_label = ttk.Label(root, text="Upload: N/A", font=('Arial', 12))
    download_label = ttk.Label(root, text="Download: N/A", font=('Arial', 12))
    cpu_label = ttk.Label(root, text="CPU: N/A", font=('Arial', 10))
    ram_label = ttk.Label(root, text="RAM: N/A", font=('Arial', 10))

    upload_label.pack(pady=5)
    download_label.pack(pady=5)
    cpu_label.pack(pady=5)
    ram_label.pack(pady=5)

    def update_gui():
        net_stats = psutil.net_io_counters()
        cpu_percent = psutil.cpu_percent()
        mem = psutil.virtual_memory()

        upload_label.config(text=f"Upload: {get_size(net_stats.bytes_sent)}")
        download_label.config(text=f"Download: {get_size(net_stats.bytes_recv)}")
        cpu_label.config(text=f"CPU Usage: {cpu_percent}%")
        ram_label.config(text=f"RAM Used: {get_size(mem.used)} / {get_size(mem.total)}")

        root.after(2000, update_gui)  # Update every 2 seconds

    update_gui()
    root.mainloop()

if __name__ == "__main__":
    print("Choose mode:")
    print("1. CLI Monitor (Rich Colors)")
    print("2. GUI Monitor (Tkinter)")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        run_cli_monitor()
    elif choice == "2":
        run_gui_monitor()
    else:
        print("Invalid choice. Exiting.")