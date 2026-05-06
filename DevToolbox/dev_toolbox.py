#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发者工具箱 - Developer Toolbox
使用 CustomTkinter 构建现代化 Windows GUI
"""

import customtkinter as ctk
from tkinter import messagebox
import json
import base64
import hashlib
import urllib.parse
import re
import os
import sys
import time
import uuid
import random
import string
import datetime
import socket
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from io import BytesIO

try:
    from Crypto.Cipher import AES, DES
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    CRYPTO_AVAILABLE = True
except:
    CRYPTO_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except:
    QRCODE_AVAILABLE = False

VERSION = "1.0.0"
CONFIG_FILE = "dev_toolbox_config.json"
HISTORY_FILE = "dev_toolbox_history.json"

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ThemeManager:
    def __init__(self):
        self.dark_mode = True
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.dark_mode = config.get('dark_mode', True)
        except:
            pass

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({'dark_mode': self.dark_mode}, f)
        except:
            pass

    def toggle(self):
        self.dark_mode = not self.dark_mode
        self.save_config()
        ctk.set_appearance_mode("dark" if self.dark_mode else "light")
        return self.dark_mode

class HistoryManager:
    def __init__(self):
        self.history = []
        self.load_history()

    def load_history(self):
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                    self.history = self.history[:100]
        except:
            self.history = []

    def save_history(self):
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except:
            pass

    def add(self, category, tool, input_data, output_data):
        entry = {
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'category': category,
            'tool': tool,
            'input': input_data[:200] if len(input_data) > 200 else input_data,
            'output': output_data[:200] if len(output_data) > 200 else output_data
        }
        self.history.insert(0, entry)
        if len(self.history) > 100:
            self.history = self.history[:100]
        self.save_history()

    def get_recent(self, count=20):
        return self.history[:count]

class DevToolbox(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"开发者工具箱 v{VERSION}")
        self.geometry("1200x800")
        
        self.theme = ThemeManager()
        self.history_mgr = HistoryManager()
        self.favorites = []
        self.current_category = None
        self.load_favorites()
        
        if self.theme.dark_mode:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        
        self.setup_ui()

    def load_favorites(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.favorites = config.get('favorites', [])
        except:
            self.favorites = []

    def save_favorites(self):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
        config['favorites'] = self.favorites
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f)

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="🛠️ 开发者工具箱", 
                                        font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20)

        self.sidebar_button = ctk.CTkButton(self.sidebar, text="切换主题", command=self.toggle_theme)
        self.sidebar_button.pack(pady=10, padx=20, fill="x")

        self.sidebar_button2 = ctk.CTkButton(self.sidebar, text="历史记录", command=self.show_history)
        self.sidebar_button2.pack(pady=5, padx=20, fill="x")

        self.category_list = ctk.CTkScrollableFrame(self.sidebar, label_text="功能分类")
        self.category_list.pack(fill="both", expand=True, padx=10, pady=10)

        categories = [
            ("📝 文本工具", "text"),
            ("⏰ 时间日期", "datetime"),
            ("🔐 加解密", "crypto"),
            ("🌐 网络工具", "network"),
            ("🔄 编码转换", "encoding"),
            ("🎨 前端工具", "frontend"),
            ("⚙️ 后端工具", "backend"),
            ("🖥️ 运维工具", "system"),
            ("⚡ 效率工具", "efficiency"),
            ("⭐ 我的收藏", "favorites")
        ]

        for name, key in categories:
            btn = ctk.CTkButton(self.category_list, text=name, command=lambda k=key: self.show_tools(k),
                               fg_color="transparent", border_width=1, anchor="w")
            btn.pack(pady=2, fill="x")

        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.notebook = ctk.CTkTabview(self.main_frame)
        self.notebook.pack(fill="both", expand=True)

    def toggle_theme(self):
        self.theme.toggle()

    def show_history(self):
        win = ctk.CTkToplevel(self)
        win.title("历史记录")
        win.geometry("700x500")

        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        history = self.history_mgr.get_recent()
        for h in history:
            frame = ctk.CTkFrame(scroll)
            frame.pack(fill="x", pady=5)
            ctk.CTkLabel(frame, text=f"[{h['time']}] {h['category']} - {h['tool']}", 
                        font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=2)
            ctk.CTkLabel(frame, text=f"输入: {h['input']}", font=ctk.CTkFont(size=10)).pack(anchor="w", padx=10)
            ctk.CTkLabel(frame, text=f"输出: {h['output']}", font=ctk.CTkFont(size=10)).pack(anchor="w", padx=10)

    def show_tools(self, category):
        for tab in self.notebook._tab_dict.keys():
            self.notebook.delete(tab)
        
        if category == "text":
            self.create_text_tools()
        elif category == "datetime":
            self.create_datetime_tools()
        elif category == "crypto":
            self.create_crypto_tools()
        elif category == "network":
            self.create_network_tools()
        elif category == "encoding":
            self.create_encoding_tools()
        elif category == "frontend":
            self.create_frontend_tools()
        elif category == "backend":
            self.create_backend_tools()
        elif category == "system":
            self.create_system_tools()
        elif category == "efficiency":
            self.create_efficiency_tools()
        elif category == "favorites":
            self.show_favorites()

    def show_favorites(self):
        tab = self.notebook.add("⭐ 我的收藏")
        if self.favorites:
            for i, fav in enumerate(self.favorites):
                ctk.CTkLabel(tab, text=f"{i+1}. {fav}", anchor="w").pack(pady=5, padx=10, fill="x")
        else:
            ctk.CTkLabel(tab, text="暂无收藏的工具").pack(pady=20)

    def create_tool_tab(self, title):
        return self.notebook.add(title)

    def create_io_frame(self, parent):
        input_frame = ctk.CTkFrame(parent)
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(input_frame, text="输入").pack(anchor="w", padx=10, pady=5)
        input_text = ctk.CTkTextbox(input_frame, height=100)
        input_text.pack(fill="both", expand=True, padx=10, pady=5)

        output_frame = ctk.CTkFrame(parent)
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(output_frame, text="输出").pack(anchor="w", padx=10, pady=5)
        output_text = ctk.CTkTextbox(output_frame, height=100)
        output_text.pack(fill="both", expand=True, padx=10, pady=5)

        return input_text, output_text

    def add_to_history(self, category, tool, input_data, output_data):
        self.history_mgr.add(category, tool, input_data, output_data)

    # ==================== 文本工具 ====================
    def create_text_tools(self):
        tab = self.create_tool_tab("📝 文本工具")
        
        sub_notebook = ctk.CTkTabview(tab)
        sub_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        json_tab = sub_notebook.add("JSON")
        input_text, output_text = self.create_io_frame(json_tab)
        
        def format_json():
            try:
                data = json.loads(input_text.get("1.0", "end").strip())
                result = json.dumps(data, indent=2, ensure_ascii=False)
                output_text.delete("1.0", "end")
                output_text.insert("1.0", result)
                self.add_to_history("文本工具", "JSON格式化", input_text.get("1.0", "end"), result)
            except Exception as e:
                messagebox.showerror("错误", f"JSON格式错误: {e}")
        
        def compress_json():
            try:
                data = json.loads(input_text.get("1.0", "end").strip())
                result = json.dumps(data, separators=(',', ':'))
                output_text.delete("1.0", "end")
                output_text.insert("1.0", result)
            except Exception as e:
                messagebox.showerror("错误", f"JSON格式错误: {e}")
        
        def validate_json():
            try:
                json.loads(input_text.get("1.0", "end").strip())
                messagebox.showinfo("验证", "JSON格式有效!")
            except Exception as e:
                messagebox.showerror("错误", f"JSON无效: {e}")

        btn_frame = ctk.CTkFrame(json_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="格式化", command=format_json).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="压缩", command=compress_json).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="校验", command=validate_json).pack(side="left", padx=5)
        
        str_tab = sub_notebook.add("字符串")
        input_text, output_text = self.create_io_frame(str_tab)
        
        def url_encode():
            text = input_text.get("1.0", "end").strip()
            result = urllib.parse.quote(text)
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
        
        def url_decode():
            text = input_text.get("1.0", "end").strip()
            result = urllib.parse.unquote(text)
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
        
        def base64_encode():
            text = input_text.get("1.0", "end").strip()
            result = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
        
        def base64_decode():
            try:
                text = input_text.get("1.0", "end").strip()
                result = base64.b64decode(text).decode('utf-8')
                output_text.delete("1.0", "end")
                output_text.insert("1.0", result)
            except:
                messagebox.showerror("错误", "Base64解码失败")
        
        def to_camel():
            text = input_text.get("1.0", "end").strip()
            words = re.split(r'[_\s]+', text)
            result = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
        
        def to_snake():
            text = input_text.get("1.0", "end").strip()
            result = re.sub(r'([A-Z])', r'_\1', text).lower().strip('_')
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)

        btn_frame = ctk.CTkFrame(str_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        for text, cmd in [("URL编码", url_encode), ("URL解码", url_decode),
                          ("Base64编码", base64_encode), ("Base64解码", base64_decode),
                          ("驼峰", to_camel), ("下划线", to_snake)]:
            ctk.CTkButton(btn_frame, text=text, command=cmd).pack(side="left", padx=5)
        
        rand_tab = sub_notebook.add("随机生成")
        input_frame = ctk.CTkFrame(rand_tab)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="长度:").pack(side="left", padx=5)
        length_entry = ctk.CTkEntry(input_frame, width=80)
        length_entry.insert(0, "16")
        length_entry.pack(side="left", padx=5)
        
        _, output_text = self.create_io_frame(rand_tab)
        
        def gen_password():
            length = int(length_entry.get() or 16)
            pool = string.ascii_letters + string.digits + string.punctuation
            result = ''.join(random.choice(pool) for _ in range(length))
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
        
        def gen_uuid():
            result = str(uuid.uuid4())
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)

        btn_frame = ctk.CTkFrame(rand_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="密码", command=gen_password).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="UUID", command=gen_uuid).pack(side="left", padx=5)

    # ==================== 时间日期 ====================
    def create_datetime_tools(self):
        tab = self.create_tool_tab("⏰ 时间日期")
        
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(input_frame, text="输入时间戳或日期:").pack(side="left", padx=10)
        input_entry = ctk.CTkEntry(input_frame, width=300)
        input_entry.pack(side="left", padx=10)
        
        output_text = ctk.CTkTextbox(tab, height=200)
        output_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        def ts_to_datetime():
            ts = input_entry.get().strip()
            try:
                if len(ts) == 10:
                    dt = datetime.datetime.fromtimestamp(int(ts))
                elif len(ts) == 13:
                    dt = datetime.datetime.fromtimestamp(int(ts)/1000)
                else:
                    raise ValueError("时间戳格式错误")
                result = f"时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n时间戳(秒): {int(dt.timestamp())}\n毫秒: {int(dt.timestamp()*1000)}"
                output_text.delete("1.0", "end")
                output_text.insert("1.0", result)
            except Exception as e:
                messagebox.showerror("错误", str(e))
        
        def now_time():
            now = datetime.datetime.now()
            result = f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\nUnix时间戳: {int(now.timestamp())}\n毫秒: {int(now.timestamp()*1000)}"
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)

        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="时间戳转时间", command=ts_to_datetime).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="当前时间", command=now_time).pack(side="left", padx=5)

    # ==================== 加解密 ====================
    def create_crypto_tools(self):
        tab = self.create_tool_tab("🔐 加解密")
        
        sub_notebook = ctk.CTkTabview(tab)
        sub_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        hash_tab = sub_notebook.add("哈希")
        input_text, output_text = self.create_io_frame(hash_tab)
        
        def hash_md5():
            text = input_text.get("1.0", "end").strip()
            result = hashlib.md5(text.encode()).hexdigest()
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
        
        def hash_sha256():
            text = input_text.get("1.0", "end").strip()
            result = hashlib.sha256(text.encode()).hexdigest()
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)

        btn_frame = ctk.CTkFrame(hash_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="MD5", command=hash_md5).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="SHA256", command=hash_sha256).pack(side="left", padx=5)
        
        if CRYPTO_AVAILABLE:
            aes_tab = sub_notebook.add("AES")
            key_frame = ctk.CTkFrame(aes_tab)
            key_frame.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(key_frame, text="密钥:").pack(side="left", padx=5)
            key_entry = ctk.CTkEntry(key_frame, width=250, show="*")
            key_entry.pack(side="left", padx=5)
            
            input_text, output_text = self.create_io_frame(aes_tab)
            
            def aes_encrypt():
                text = input_text.get("1.0", "end").strip()
                key = key_entry.get().encode()[:32].ljust(32, b'0')
                try:
                    cipher = AES.new(key, AES.MODE_CBC)
                    ct = cipher.encrypt(text.encode())
                    result = base64.b64encode(cipher.iv + ct).decode()
                    output_text.delete("1.0", "end")
                    output_text.insert("1.0", result)
                except Exception as e:
                    messagebox.showerror("错误", str(e))
            
            btn_frame = ctk.CTkFrame(aes_tab)
            btn_frame.pack(fill="x", padx=10, pady=5)
            ctk.CTkButton(btn_frame, text="加密", command=aes_encrypt).pack(side="left", padx=5)

        if QRCODE_AVAILABLE:
            qr_tab = sub_notebook.add("二维码")
            input_text, output_text = self.create_io_frame(qr_tab)
            
            def gen_qr():
                text = input_text.get("1.0", "end").strip()
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(text)
                qr.make(fit=True)
                img = qr.make_image()
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                result = f"[二维码图片已生成，数据长度: {len(buffer.getvalue())} 字节]"
                output_text.delete("1.0", "end")
                output_text.insert("1.0", result)
            
            btn_frame = ctk.CTkFrame(qr_tab)
            btn_frame.pack(fill="x", padx=10, pady=5)
            ctk.CTkButton(btn_frame, text="生成二维码", command=gen_qr).pack(side="left", padx=5)

    # ==================== 网络工具 ====================
    def create_network_tools(self):
        tab = self.create_tool_tab("🌐 网络工具")
        
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(input_frame, text="输入地址:").pack(side="left", padx=10)
        input_entry = ctk.CTkEntry(input_frame, width=300)
        input_entry.pack(side="left", padx=10)
        
        output_text = ctk.CTkTextbox(tab, height=300)
        output_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        def get_local_ip():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                output_text.delete("1.0", "end")
                output_text.insert("1.0", f"本机IP: {ip}")
            except:
                output_text.insert("1.0", "获取失败")
        
        def get_public_ip():
            try:
                req = urllib.request.Request('https://api.ipify.org')
                response = urllib.request.urlopen(req, timeout=5)
                ip = response.read().decode()
                output_text.delete("1.0", "end")
                output_text.insert("1.0", f"公网IP: {ip}")
            except Exception as e:
                output_text.insert("1.0", f"获取失败: {e}")
        
        def ping_host():
            host = input_entry.get().strip()
            if not host:
                messagebox.showinfo("提示", "请输入主机地址")
                return
            param = '-n' if sys.platform == 'win32' else '-c'
            result = os.popen(f'ping {param} 1 {host}').read()
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
        
        def check_port():
            host_port = input_entry.get().strip()
            if ':' not in host_port:
                messagebox.showinfo("提示", "请输入 主机:端口 格式")
                return
            host, port = host_port.split(':')
            port = int(port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            try:
                result = sock.connect_ex((host, port))
                status = "开放" if result == 0 else "关闭"
                output_text.delete("1.0", "end")
                output_text.insert("1.0", f"端口 {port} 状态: {status}")
            except Exception as e:
                output_text.insert("1.0", f"错误: {e}")
            finally:
                sock.close()
        
        def dns_lookup():
            domain = input_entry.get().strip()
            try:
                ip = socket.gethostbyname(domain)
                output_text.delete("1.0", "end")
                output_text.insert("1.0", f"域名 {domain} 的IP: {ip}")
            except Exception as e:
                output_text.insert("1.0", f"DNS解析失败: {e}")

        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        for text, cmd in [("本机IP", get_local_ip), ("公网IP", get_public_ip),
                          ("Ping", ping_host), ("端口检测", check_port), ("DNS查询", dns_lookup)]:
            ctk.CTkButton(btn_frame, text=text, command=cmd).pack(side="left", padx=5)

    # ==================== 编码转换 ====================
    def create_encoding_tools(self):
        tab = self.create_tool_tab("🔄 编码转换")
        
        input_text, output_text = self.create_io_frame(tab)
        
        def bin_to_dec():
            text = input_text.get("1.0", "end").strip()
            result = str(int(text, 2))
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
        
        def dec_to_bin():
            text = input_text.get("1.0", "end").strip()
            result = bin(int(text))[2:]
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
        
        def hex_to_dec():
            text = input_text.get("1.0", "end").strip()
            result = str(int(text, 16))
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
        
        def dec_to_hex():
            text = input_text.get("1.0", "end").strip()
            result = hex(int(text))[2:]
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
        
        def rgb_to_hex():
            text = input_text.get("1.0", "end").strip()
            rgb = re.findall(r'\d+', text)
            if len(rgb) >= 3:
                r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
                result = f"#{r:02x}{g:02x}{b:02x}"
                output_text.delete("1.0", "end")
                output_text.insert("1.0", result)
        
        def hex_to_rgb():
            text = input_text.get("1.0", "end").strip().lstrip('#')
            if len(text) == 6:
                r = int(text[0:2], 16)
                g = int(text[2:4], 16)
                b = int(text[4:6], 16)
                result = f"rgb({r}, {g}, {b})"
                output_text.delete("1.0", "end")
                output_text.insert("1.0", result)

        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        for text, cmd in [("2→10", bin_to_dec), ("10→2", dec_to_bin),
                          ("16→10", hex_to_dec), ("10→16", dec_to_hex),
                          ("RGB→HEX", rgb_to_hex), ("HEX→RGB", hex_to_rgb)]:
            ctk.CTkButton(btn_frame, text=text, command=cmd).pack(side="left", padx=5)

    # ==================== 前端工具 ====================
    def create_frontend_tools(self):
        tab = self.create_tool_tab("🎨 前端工具")
        
        input_text, output_text = self.create_io_frame(tab)
        
        def css_minify():
            text = input_text.get("1.0", "end").strip()
            result = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
            result = re.sub(r'\s+', ' ', result).strip()
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
        
        def js_format():
            text = input_text.get("1.0", "end").strip()
            output_text.delete("1.0", "end")
            output_text.insert("1.0", text)
        
        def ua_parse():
            text = input_text.get("1.0", "end").strip()
            result = "User-Agent解析:\n"
            if "Chrome" in text:
                result += "浏览器: Chrome\n"
            if "Firefox" in text:
                result += "浏览器: Firefox\n"
            if "Windows" in text:
                result += "系统: Windows\n"
            elif "Mac" in text:
                result += "系统: macOS\n"
            elif "Linux" in text:
                result += "系统: Linux\n"
            if "Mobile" in text:
                result += "设备: 移动设备"
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)

        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        for text, cmd in [("CSS压缩", css_minify), ("JS格式化", js_format), ("UA解析", ua_parse)]:
            ctk.CTkButton(btn_frame, text=text, command=cmd).pack(side="left", padx=5)

    # ==================== 后端工具 ====================
    def create_backend_tools(self):
        tab = self.create_tool_tab("⚙️ 后端工具")
        
        sub_notebook = ctk.CTkTabview(tab)
        sub_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        sql_tab = sub_notebook.add("SQL")
        input_text, output_text = self.create_io_frame(sql_tab)
        
        def sql_format():
            text = input_text.get("1.0", "end").strip()
            keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY', 'LIMIT']
            result = text.strip()
            for kw in keywords:
                result = result.replace(kw, '\n' + kw)
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)

        btn_frame = ctk.CTkFrame(sql_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="格式化", command=sql_format).pack(side="left", padx=5)
        
        gen_tab = sub_notebook.add("随机数据")
        _, output_text = self.create_io_frame(gen_tab)
        
        def gen_name():
            surnames = ['张', '李', '王', '刘', '陈', '杨', '赵', '黄', '周', '吴']
            names = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋']
            result = random.choice(surnames) + random.choice(names)
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
        
        def gen_phone():
            prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                       '150', '151', '152', '153', '155', '156', '157', '158', '159',
                       '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
            result = random.choice(prefixes) + ''.join([str(random.randint(0, 9)) for _ in range(8)])
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)

        btn_frame = ctk.CTkFrame(gen_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="姓名", command=gen_name).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="手机号", command=gen_phone).pack(side="left", padx=5)

    # ==================== 运维工具 ====================
    def create_system_tools(self):
        tab = self.create_tool_tab("🖥️ 运维工具")
        
        output_text = ctk.CTkTextbox(tab, height=400)
        output_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        def file_hash_md5():
            from tkinter import filedialog
            filepath = filedialog.askopenfilename()
            if filepath:
                try:
                    with open(filepath, 'rb') as f:
                        result = hashlib.md5(f.read()).hexdigest()
                    output_text.delete("1.0", "end")
                    output_text.insert("1.0", f"MD5: {result}")
                except Exception as e:
                    messagebox.showerror("错误", str(e))
        
        def find_port():
            param = '-ano' if sys.platform == 'win32' else '-tulpn'
            result = os.popen(f'netstat {param}').read()[:3000]
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
        
        def linux_cmds():
            cmds = {
                '查看进程': 'ps aux | head -20',
                '内存使用': 'free -h',
                '磁盘使用': 'df -h',
                '网络状态': 'netstat -tuln',
                '当前用户': 'whoami',
            }
            result = '\n'.join([f"{k}: {v}" for k, v in cmds.items()])
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)

        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        for text, cmd in [("MD5校验", file_hash_md5), ("端口查询", find_port), ("Linux命令", linux_cmds)]:
            ctk.CTkButton(btn_frame, text=text, command=cmd).pack(side="left", padx=5)

    # ==================== 效率工具 ====================
    def create_efficiency_tools(self):
        tab = self.create_tool_tab("⚡ 效率工具")
        
        output_text = ctk.CTkTextbox(tab, height=500)
        output_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        snippets = {
            "Python读文件": "with open('file.txt', 'r', encoding='utf-8') as f:\n    content = f.read()",
            "Python写文件": "with open('file.txt', 'w', encoding='utf-8') as f:\n    f.write('content')",
            "Python HTTP": "import requests\nresponse = requests.get('url')\nprint(response.text)",
            "JS防抖": "function debounce(fn, delay) {\n  let timer;\n  return function(...args) {\n    clearTimeout(timer);\n    timer = setTimeout(() => fn(...args), delay);\n  }\n}",
            "JS节流": "function throttle(fn, delay) {\n  let flag = true;\n  return function(...args) {\n    if (!flag) return;\n    flag = false;\n    setTimeout(() => { fn(...args); flag = true; }, delay);\n  }\n}",
            "SQL分页": "SELECT * FROM table LIMIT offset, size",
        }
        
        for name, code in snippets.items():
            output_text.insert("end", f"--- {name} ---\n{code}\n\n")
        
        def copy_all():
            text = output_text.get("1.0", "end").strip()
            self.clipboard_clear()
            self.clipboard_append(text)
        
        ctk.CTkButton(tab, text="复制全部", command=copy_all).pack(pady=10)

def main():
    app = DevToolbox()
    app.mainloop()

if __name__ == "__main__":
    main()