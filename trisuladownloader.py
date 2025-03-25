import os
import re
import json
import yt_dlp
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from tkinter import ttk

# Variabel global
download_destination = None
facebook_cookie_file = None
selected_platform = None  # Platform yang dipilih pengguna

# === Fungsi Pendukung ===

def extract_username_from_tiktok(url):
    """
    Mengambil username dari URL TikTok.
    Contoh URL: https://www.tiktok.com/@0827moeha/video/7406669884186184965
    Akan mengembalikan: @0827moeha
    """
    pattern = r"tiktok\.com/@([^/]+)/video/"
    match = re.search(pattern, url)
    if match:
        return '@' + match.group(1)
    return None

def get_platform_folder(url):
    """
    Menentukan subfolder berdasarkan platform dari URL.
    Jika username tidak dapat diekstrak, digunakan nama default untuk tiap platform.
    """
    if "tiktok.com" in url:
        username = extract_username_from_tiktok(url)
        return username if username else "unknown_tiktok"
    elif "instagram.com" in url:
        return "Instagram"
    elif "facebook.com" in url:
        return "Facebook"
    elif "pinterest.com" in url:
        return "Pinterest"
    else:
        return "Other"

def download_media(url):
    """
    Mendownload konten dari URL yang diberikan dan menyimpannya ke folder yang sesuai.
    Jika platform adalah Facebook dan cookies sudah di-set, maka akan menggunakan cookies.
    """
    global download_destination, facebook_cookie_file
    base_folder = download_destination if download_destination else os.getcwd()
    folder = os.path.join(base_folder, get_platform_folder(url))
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    ydl_opts = {
        'outtmpl': os.path.join(folder, '%(title).80B.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
        'restrictfilenames': True,
    }
    
    # Jika URL adalah Facebook dan cookies sudah di-set, gunakan cookiefile
    if "facebook.com" in url and facebook_cookie_file:
        ydl_opts['cookiefile'] = facebook_cookie_file
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan saat mendownload {url}:\n{e}")
        return False

# === Fungsi GUI Download ===

def on_download():
    """
    Fungsi yang dipanggil saat tombol Download ditekan.
    Mengambil URL dari text area dan mendownload konten.
    """
    urls = url_text.get("1.0", tk.END).strip().splitlines()
    if not urls or urls == ['']:
        messagebox.showwarning("Warning", "Masukkan minimal satu URL!")
        return

    status_text.config(state='normal')
    status_text.delete("1.0", tk.END)

    for url in urls:
        if url.strip() == "":
            continue
        status_text.insert(tk.END, f"Mendownload: {url}\n")
        status_text.see(tk.END)
        root.update()
        success = download_media(url)
        if success:
            status_text.insert(tk.END, f"Berhasil mendownload {url}\n\n")
        else:
            status_text.insert(tk.END, f"Gagal mendownload {url}\n\n")
        status_text.see(tk.END)
    
    messagebox.showinfo("Info", "Proses download selesai!")
    status_text.config(state='disabled')

def choose_download_folder():
    """
    Membuka dialog untuk memilih folder tujuan download.
    """
    global download_destination
    folder = filedialog.askdirectory(title="Pilih Folder Tujuan Download")
    if folder:
        download_destination = folder
        folder_entry.config(state='normal')
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, download_destination)
        folder_entry.config(state='readonly')

def show_url_guidelines():
    """
    Menampilkan ketentuan URL yang didukung berdasarkan platform.
    """
    guidelines = ""
    if selected_platform == "Facebook":
        guidelines = (
            "Facebook:\nURL harus berasal dari facebook.com dan merupakan konten publik (video atau image)."
        )
    elif selected_platform == "Instagram":
        guidelines = (
            "Instagram:\nURL harus dalam format:\n   https://www.instagram.com/p/postID/\n"
            "   atau https://www.instagram.com/tv/postID/\n   atau https://www.instagram.com/reel/postID/"
        )
    elif selected_platform == "TikTok":
        guidelines = (
            "TikTok:\nURL harus dalam format:\n   https://www.tiktok.com/@username/video/videoid"
        )
    elif selected_platform == "Pinterest":
        guidelines = (
            "Pinterest:\nURL harus berasal dari pinterest.com dan merupakan gambar atau video."
        )
    else:
        guidelines = "Pilih platform terlebih dahulu."
    messagebox.showinfo("Ketentuan URL", guidelines)

def login_facebook():
    """
    Menampilkan window untuk input cookies Facebook dalam format JSON.
    (Saat ini tidak ditampilkan di UI, jika dibutuhkan bisa ditambahkan kembali.)
    """
    def submit_cookies():
        global facebook_cookie_file
        cookies_str = fb_cookies_text.get("1.0", tk.END).strip()
        if not cookies_str:
            messagebox.showwarning("Warning", "Input cookies tidak boleh kosong!")
            return
        try:
            cookies = json.loads(cookies_str)
        except Exception as e:
            messagebox.showerror("Error", f"Format cookies tidak valid!\n{e}")
            return
        
        cookies_text_content = "# Netscape HTTP Cookie File\n"
        for cookie in cookies:
            domain = cookie.get("domain", "")
            flag = "TRUE" if domain.startswith('.') else "FALSE"
            path = cookie.get("path", "/")
            secure = "TRUE" if cookie.get("secure", False) else "FALSE"
            expiration = str(int(cookie.get("expirationDate", 0))) if not cookie.get("session", True) else "0"
            name = cookie.get("name", "")
            value = cookie.get("value", "")
            cookies_text_content += "\t".join([domain, flag, path, secure, expiration, name, value]) + "\n"
        
        cookie_file_path = os.path.join(os.getcwd(), "facebook_cookies.txt")
        try:
            with open(cookie_file_path, "w", encoding="utf-8") as f:
                f.write(cookies_text_content)
            messagebox.showinfo("Info", "Berhasil login ke Facebook menggunakan cookies!")
            facebook_cookie_file = cookie_file_path
            fb_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan cookies:\n{e}")

    fb_window = tk.Toplevel(root)
    fb_window.title("Input Cookies Facebook")
    fb_window.geometry("550x350")
    fb_window.resizable(False, False)
    
    frame = ttk.Frame(fb_window, padding="20")
    frame.pack(expand=True, fill="both")
    
    label = ttk.Label(frame, text="Masukkan cookies Facebook (dalam format JSON):", font=("Helvetica", 11))
    label.pack(anchor="w", pady=(0, 10))
    
    fb_cookies_text = scrolledtext.ScrolledText(frame, width=60, height=10, font=("Helvetica", 10))
    fb_cookies_text.pack(pady=(0, 15))
    
    submit_btn = ttk.Button(frame, text="Submit", command=submit_cookies)
    submit_btn.pack()

# === Fungsi untuk mengubah tampilan berdasarkan pilihan platform ===

def show_download_ui():
    """
    Mengambil pilihan platform, menyembunyikan tampilan awal, dan menampilkan UI download.
    """
    global selected_platform
    selected_platform = platform_var.get()
    if not selected_platform:
        messagebox.showwarning("Warning", "Pilih salah satu platform!")
        return
    # Sembunyikan frame pemilihan platform dan tampilkan frame download
    selection_frame.pack_forget()
    download_frame.pack(expand=True, fill="both")
    
    # Ubah judul sesuai platform yang dipilih
    platform_label.config(text=f"Platform: {selected_platform}")

def back_to_menu():
    """
    Fungsi untuk kembali ke menu pemilihan platform.
    """
    download_frame.pack_forget()
    selection_frame.pack(expand=True, fill="both")
    # Bersihkan isian
    url_text.delete("1.0", tk.END)
    status_text.config(state='normal')
    status_text.delete("1.0", tk.END)
    status_text.config(state='disabled')
    folder_entry.config(state='normal')
    folder_entry.delete(0, tk.END)
    folder_entry.config(state='readonly')
    # Reset selected_platform
    global selected_platform
    selected_platform = None

# === Tampilan Utama ===

root = tk.Tk()
root.title("TRISULA Downloader")
root.geometry("900x700")
root.minsize(700, 600)

style = ttk.Style(root)
style.theme_use('clam')

# --- Frame Pemilihan Platform (Menu Awal) ---
selection_frame = ttk.Frame(root, padding="30")
selection_frame.pack(expand=True, fill="both")

sel_title = ttk.Label(selection_frame, text="Pilih Platform Download", font=("Helvetica", 26, "bold"))
sel_title.pack(pady=(0, 30))

platform_var = tk.StringVar()

platforms = [("Facebook", "Facebook"),
             ("Instagram", "Instagram"),
             ("TikTok", "TikTok"),
             ("Pinterest", "Pinterest")]

for text, value in platforms:
    rb = ttk.Radiobutton(selection_frame, text=text, variable=platform_var, value=value)
    rb.pack(anchor="w", pady=5, padx=20)

next_btn = ttk.Button(selection_frame, text="Next", command=show_download_ui)
next_btn.pack(pady=30)

# --- Frame Download (akan ditampilkan setelah pemilihan platform) ---
download_frame = ttk.Frame(root, padding="20")

# Header
header_frame = ttk.Frame(download_frame)
header_frame.pack(fill="x", pady=(0, 20))
platform_label = ttk.Label(header_frame, text="", font=("Helvetica", 24, "bold"))
platform_label.pack()

# Frame Input URL (tanpa label "Input URL")
input_frame = ttk.Frame(download_frame, padding="15")
input_frame.pack(fill="both", expand=False, pady=(0, 15))

# Baris atas input URL: Label instruksi (kiri), tombol Ketentuan URL & tombol Kembali (kanan)
top_input_frame = ttk.Frame(input_frame)
top_input_frame.pack(fill="x")

instruksi_label = ttk.Label(top_input_frame, text="Masukkan URL (satu URL per baris):", font=("Helvetica", 11))
instruksi_label.pack(side="left")

# Tambahkan tombol Kembali & tombol Ketentuan URL di sisi kanan
back_button = ttk.Button(top_input_frame, text="Kembali", command=back_to_menu)
back_button.pack(side="right", padx=(5, 0))

url_guidelines_button = ttk.Button(top_input_frame, text="Ketentuan URL", command=show_url_guidelines)
url_guidelines_button.pack(side="right")

# Kolom untuk memasukkan URL
url_text = scrolledtext.ScrolledText(input_frame, width=80, height=8, font=("Helvetica", 10))
url_text.pack(fill="both", expand=True)

# Frame Kontrol (hanya dua tombol: Path dan Download Konten)
control_frame = ttk.Frame(download_frame, padding="15")
control_frame.pack(fill="x", pady=(0, 15))

# Tombol Path (pilih folder) + Entry
path_button = ttk.Button(control_frame, text="Path", command=choose_download_folder)
path_button.pack(side="left", padx=8)

folder_entry = ttk.Entry(control_frame, width=50, state='readonly')
folder_entry.pack(side="left", padx=8)

# Tombol Download Konten
download_button = ttk.Button(control_frame, text="Download Konten", command=on_download)
download_button.pack(side="left", padx=8)

# Frame Status
status_frame = ttk.LabelFrame(download_frame, text="Status", padding="15")
status_frame.pack(fill="both", expand=True)

status_text = scrolledtext.ScrolledText(status_frame, width=80, height=15, font=("Helvetica", 10), state='disabled')
status_text.pack(fill="both", expand=True)

# Jalankan aplikasi
root.mainloop()
