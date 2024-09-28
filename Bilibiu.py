# coding=utf-8
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import webbrowser
import threading
import os
import re
import urllib.parse
import json
import subprocess
import sys


class YouTubeDownloader:
    def __init__(self, master):
        self.master = master
        master.title("Bilibiu下载神器！")
        master.geometry("600x650")  # 增加窗口高度以容纳新的选项
        master.resizable(False, False)
        master.configure(bg="#f5f5f5")

        # 尝试设置图标，如果失败则忽略
        try:
            master.iconbitmap("\\icons\\bilibili.ico")
        except tk.TclError:
            pass  # 如果图标文件不存在或无法加载，则忽略错误

        # 创建主框架
        main_frame = ttk.Frame(master, padding="20 20 20 20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        # 创建并布置界面元素
        ttk.Label(main_frame, text="视频链接:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.url_entry = scrolledtext.ScrolledText(main_frame, width=100, height=3, wrap=tk.WORD)
        self.url_entry.grid(row=0, column=1, padx=5, pady=10, columnspan=3, sticky="nswe")
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        ttk.Separator(main_frame, orient='horizontal').grid(row=1, column=0, columnspan=4, sticky='ew', pady=5)

        # 创建一个框架来容纳这三个元素
        format_quality_frame = ttk.Frame(main_frame)
        format_quality_frame.grid(row=2, column=0, columnspan=5, padx=5, pady=10, sticky="w")

        # 下载格式
        ttk.Label(format_quality_frame, text="下载格式:").pack(side=tk.LEFT, padx=(0, 5))
        self.format_var = tk.StringVar(value="mp4")
        formats = ["mp4", "webm", "mkv", "mp3", "m4a"]
        self.format_combobox = ttk.Combobox(format_quality_frame, textvariable=self.format_var, values=formats,
                                            width=10, height=10)
        self.format_combobox.pack(side=tk.LEFT, padx=(0, 20))

        # 画质选择
        ttk.Label(format_quality_frame, text="画质选择:").pack(side=tk.LEFT, padx=(0, 5))
        self.quality_var = tk.StringVar(value="高清4K")
        qualities = ["高清8K", "高清4K", "1080p", "720p", "480p", "360p"]
        self.quality_combobox = ttk.Combobox(format_quality_frame, textvariable=self.quality_var, values=qualities,
                                             width=10, height=10)
        self.quality_combobox.pack(side=tk.LEFT, padx=(0, 20))

        # 查看支持的视频清晰度按钮
        self.check_quality_button = ttk.Button(format_quality_frame, text="查看可下载画质",
                                               command=self.check_supported_qualities, style="TButton")
        self.check_quality_button.configure(padding=(7, 2))  # 降低按钮高度
        self.check_quality_button.pack(side=tk.RIGHT, padx=(0, 5))  # 布局在最右侧

        ttk.Separator(main_frame, orient='horizontal').grid(row=3, column=0, columnspan=4, sticky='ew', pady=5)

        ttk.Label(main_frame, text="高清下载必选参数:").grid(row=4, column=0, padx=5, pady=10, sticky="w")
        self.use_cookies = tk.BooleanVar(value=True)
        self.use_cookies_checkbox = ttk.Checkbutton(main_frame, variable=self.use_cookies, text="浏览器：",
                                                    command=self.toggle_browser_selection)
        self.use_cookies_checkbox.grid(row=4, column=1, padx=5, pady=10, sticky="w")

        self.browser_var = tk.StringVar(value="firefox")
        browsers = ["firefox", "chrome", "brave", "chromium", "edge", "opera", "safari", "vivaldi", "whale"]
        self.browser_combobox = ttk.Combobox(main_frame, textvariable=self.browser_var, values=browsers, width=10,
                                             state="disabled")
        self.browser_combobox.grid(row=4, column=2, padx=5, pady=10, sticky="w")

        # 添加说明提示
        ttk.Label(main_frame, text="当用户登录后下载1080P和4K画质(自备大\n会员)请选择firefox，并安装firefox浏览器", foreground="red").grid(row=4,
                                                                                                                 column=3,
                                                                                                                 padx=5,
                                                                                                                 pady=10,
                                                                                                                 sticky="w")

        ttk.Separator(main_frame, orient='horizontal').grid(row=5, column=0, columnspan=4, sticky='ew', pady=5)

        ttk.Label(main_frame, text="保存位置:").grid(row=6, column=0, padx=5, pady=10, sticky="w")
        self.save_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.save_path, width=50).grid(row=6, column=1, padx=5, pady=10,
                                                                          columnspan=2, sticky="we")
        ttk.Button(main_frame, text="浏览", command=self.browse_save_path, style="TButton").grid(row=6, column=3, padx=5,
                                                                                               pady=10, sticky="e")

        ttk.Separator(main_frame, orient='horizontal').grid(row=7, column=0, columnspan=4, sticky='ew', pady=5)

        self.download_button = ttk.Button(main_frame, text="下载", command=self.start_download, style="TButton")
        self.download_button.grid(row=8, column=0, columnspan=2, padx=5, pady=20, sticky="we")

        self.pause_button = ttk.Button(main_frame, text="暂停", command=self.pause_download, state=tk.DISABLED,
                                       style="TButton")
        self.pause_button.grid(row=8, column=2, padx=5, pady=20, sticky="we")

        self.cancel_button = ttk.Button(main_frame, text="取消", command=self.cancel_download, state=tk.DISABLED,
                                        style="TButton")
        self.cancel_button.grid(row=8, column=3, padx=5, pady=20, sticky="we")

        ttk.Separator(main_frame, orient='horizontal').grid(row=9, column=0, columnspan=4, sticky='ew', pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100, length=500)
        self.progress_bar.grid(row=10, column=0, columnspan=4, padx=5, pady=10, sticky="we")

        self.progress_label = ttk.Label(main_frame, text="0%")
        self.progress_label.grid(row=11, column=0, columnspan=4, padx=5, pady=5)

        ttk.Separator(main_frame, orient='horizontal').grid(row=12, column=0, columnspan=4, sticky='ew', pady=5)

        self.log_text = scrolledtext.ScrolledText(main_frame, width=70, height=10, bg="black", fg="white")
        self.log_text.grid(row=13, column=0, columnspan=4, padx=5, pady=10)

        ttk.Separator(main_frame, orient='horizontal').grid(row=14, column=0, columnspan=4, sticky='ew', pady=5)

        # ttk.Button(main_frame, text="打开视频", command=self.open_video_link, style="TButton").grid(row=15, column=0, columnspan=4, padx=5, pady=10)

        # 配置样式
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#000000", foreground="#000000", borderwidth=0)
        style.map("TButton", background=[("active", "#000000")])

        # 下载控制变量
        self.download_process = None
        self.is_paused = False
        self.is_cancelled = False

        # 加载保存路径缓存
        self.load_save_path_cache()

    def toggle_browser_selection(self):
        if self.use_cookies.get():
            self.browser_combobox.config(state="readonly")
        else:
            self.browser_combobox.config(state="disabled")

    def check_supported_qualities(self):
        url = self.url_entry.get('1.0', tk.END).strip()
        if not url:
            messagebox.showerror("错误", "请先输入视频链接")
            return

        # 检查是否安装了Firefox浏览器
        if not self.is_firefox_installed():
            result = messagebox.askquestion("安装 Firefox", "未检测到Firefox浏览器。是否下载并安装Firefox浏览器？")
            if result == 'yes':
                self.download_firefox()
            return

        # 如果已安装Firefox，则自动打开
        self.open_firefox()

        yt_dlp_path = self.get_yt_dlp_path()
        if not yt_dlp_path:
            messagebox.showerror("错误", "无法找到 yt-dlp 执行文件")
            return

        # 使用yt-dlp判断是否为播放列表
        playlist_check_command = [yt_dlp_path, "--flat-playlist", "--dump-json", url]
        try:
            playlist_result = subprocess.run(playlist_check_command, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            playlist_output = playlist_result.stdout
            is_playlist = len(playlist_output.strip().split('\n')) > 1
        except Exception as e:
            messagebox.showerror("错误", f"检查播放列表失败: {str(e)}")
            return

        if is_playlist:
            # 如果是播放列表，获取第一个视频的URL
            first_video_json = json.loads(playlist_output.strip().split('\n')[0])
            url = first_video_json.get('url', url)

        command = [yt_dlp_path, "-F", url]

        # 如果选择了使用cookies，添加相应的参数
        if self.use_cookies.get():
            command.extend(["--cookies-from-browser", self.browser_var.get()])

        try:
            result = subprocess.run(command, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            output = result.stdout
            print(output)

            # 检查输出中是否包含"Extracted"
            if "Extracted" not in output:
                messagebox.showinfo("提示", "未找到可下载内容。请确保已在Firefox中登录并访问过相关网站。")
                return

            # 解析输出，提取清晰度信息
            qualities = []
            best_qualitys = []
            for line in output.split('\n'):
                match = re.search(r'(\d+)\s+(\w+)\s+(\d+x\d+)\s+(\d+)', line)
                if match:
                    id, ext, resolution, fps = match.groups()
                    width, height = map(int, resolution.split('x'))
                    if width >= 7680 or height >= 4320:
                        quality = "高清8K"
                    elif width >= 3840 or height >= 1920:
                        quality = "高清4K"
                    elif width >= 1920 or height >= 1080:
                        quality = "1080p"
                    elif width >= 1280 or height >= 720:
                        quality = "720p"
                    elif width >= 854 or height >= 480:
                        quality = "480p"
                    elif width >= 640 or height >= 360:
                        quality = "360p"
                    else:
                        quality = "低清晰度"
                    qualities.append(f"{id} {ext} {resolution} {fps}fps - {quality}")
                    best_qualitys.append(quality)

            print(qualities)
            # 如果没有找到清晰度信息，显示完整输出
            if not qualities:
                messagebox.showinfo("支持的清晰度", output)
            else:
                messagebox.showinfo("支持的清晰度", "\n".join(qualities))
                
            # 更新画质选择框
            if best_qualitys:
                best_quality = best_qualitys[-1]
                self.quality_var.set(best_quality)
                quality_order = ["高清8K", "高清4K", "1080p", "720p", "480p", "360p"]
                self.quality_combobox['values'] = [q for q in quality_order if quality_order.index(q) >= quality_order.index(best_quality)]
        except Exception as e:
            messagebox.showerror("错误", f"获取清晰度信息失败: {str(e)}")

    def compare_quality(self, q1, q2):
        quality_order = ["高清8K", "高清4K", "1080p", "720p", "480p", "360p", "低清晰度"]
        return quality_order.index(q1) - quality_order.index(q2)

    def is_firefox_installed(self):
        # 检查Firefox是否安装的逻辑
        # 这里使用一个简单的方法，检查默认安装路径
        firefox_path = os.path.join(os.environ.get('ProgramFiles'), 'Mozilla Firefox', 'firefox.exe')
        return os.path.exists(firefox_path)

    def open_firefox(self):
        url = self.url_entry.get("1.0", tk.END).strip()
        if not url:
            url = 'https://www.bilibili.com'
        try:
            # 首先尝试使用webbrowser模块打开Firefox
            webbrowser.get('firefox').open(url)
        except webbrowser.Error:
            try:
                # 如果webbrowser模块失败，尝试直接启动Firefox进程
                firefox_path = self.get_firefox_path()
                if firefox_path:
                    subprocess.Popen([firefox_path, url])
                else:
                    raise FileNotFoundError("无法找到Firefox可执行文件")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开 Firefox 浏览器：{str(e)}。请确保已正确安装 Firefox。")
        except Exception as e:
            messagebox.showerror("错误", f"打开 Firefox 时发生未知错误：{str(e)}")

    def get_firefox_path(self):
        # 检查常见的Firefox安装路径
        possible_paths = [
            os.path.join(os.environ.get('ProgramFiles', ''), 'Mozilla Firefox', 'firefox.exe'),
            os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'Mozilla Firefox', 'firefox.exe'),
            os.path.expanduser('~\\AppData\\Local\\Mozilla Firefox\\firefox.exe'),
            # 添加更多可能的路径
            'C:\\Program Files\\Mozilla Firefox\\firefox.exe',
            'C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe'
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # 如果上述路径都不存在，尝试使用注册表查找Firefox路径
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe") as key:
                return winreg.QueryValue(key, None)
        except:
            pass
        
        return None

    def download_firefox(self):
        firefox_url = "https://www.mozilla.org/firefox/new/"
        webbrowser.open(firefox_url)

    def load_save_path_cache(self):
        try:
            with open('save_path_cache.json', 'r') as f:
                cache = json.load(f)
                self.save_path.set(cache.get('last_save_path', ''))
        except FileNotFoundError:
            pass

    def save_save_path_cache(self):
        cache = {'last_save_path': self.save_path.get()}
        with open('save_path_cache.json', 'w') as f:
            json.dump(cache, f)

    def browse_save_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_path.set(directory)
            self.save_save_path_cache()

    def start_download(self):
        self.is_paused = False
        self.is_cancelled = False
        threading.Thread(target=self.check_and_download, daemon=True).start()
        self.download_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.NORMAL)

    def check_and_download(self):
        try:
            print(self.url_entry)
            url = self.url_entry.get('1.0', tk.END).strip()
            if "list=" in url:
                if messagebox.askyesno("下载列表", "检测到列表链接，是否下载列表中所有视频？"):
                    self.download_playlist(url)
                else:
                    self.download_video(url)
            else:
                self.download_video(url)
        except AttributeError:
            messagebox.showerror("错误", "无法获取URL。请确保URL输入框正确初始化。")
        except Exception as e:
            messagebox.showerror("错误", f"发生未知错误：{str(e)}")

    def download_playlist(self, url):
        encoded_url = url
        format = self.format_var.get()
        quality = self.quality_var.get()
        save_path = self.save_path.get()
        browser = self.browser_var.get()

        if not save_path:
            messagebox.showerror("错误", "请选择保存位置")
            return

        yt_dlp_path = self.get_yt_dlp_path()
        if not yt_dlp_path:
            messagebox.showerror("错误", "无法找到 yt-dlp 执行文件")
            return

        ffmpeg_path = self.get_ffmpeg_path()
        if not ffmpeg_path:
            messagebox.showerror("错误", "无法找到 ffmpeg 执行文件")
            return

        command = [
            yt_dlp_path,
            "-o", f'{save_path}/%(playlist_title)s/%(title)s.%(ext)s',
            "--user-agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
            "--ffmpeg-location", ffmpeg_path,
        ]

        if self.use_cookies.get():
            command.extend(["--cookies-from-browser", browser])
        print("下载命令：", command)
        if format in ['mp3', 'm4a']:
            command.extend([
                "-x",
                "--audio-format", format,
                "--audio-quality", "192K"
            ])
        else:
            if quality == "高清8K":
                command.extend(["-f", f'bestvideo[height>=4320][ext={format}]+bestaudio/best[height>=4320][ext={format}]/best'])
            elif quality == "高清4K":
                command.extend(["-f", f'bestvideo[height>=2160][ext={format}]+bestaudio/best[height>=2160][ext={format}]/best'])
            else:
                command.extend(["-f", f'bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]/best'])
            command.extend(["--merge-output-format", format])

        command.append(encoded_url)
        print("下载命令：", command)
        try:

            self.download_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                     universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
            for line in self.download_process.stdout:
                if self.is_cancelled:
                    break
                while self.is_paused:
                    if self.is_cancelled:
                        break
                self.update_log(line.strip())
                self.update_progress_from_log(line)

            if not self.is_cancelled:
                self.progress_var.set(100)
                self.progress_label.config(text="100%")
                messagebox.showinfo("成功", f"播放列表已成功下载为 {format} 格式")
                self.open_download_folder(save_path)
        except Exception as e:
            if not self.is_cancelled:
                error_message = f"下载失败: {str(e)}"
                self.update_log(error_message)
                messagebox.showerror("错误", error_message)
        finally:
            self.progress_var.set(0)
            self.progress_label.config(text="0%")
            self.download_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.cancel_button.config(state=tk.DISABLED)

    def pause_download(self):
        if self.is_paused:
            self.is_paused = False
            self.pause_button.config(text="暂停")
        else:
            self.is_paused = True
            self.pause_button.config(text="继续")

    def cancel_download(self):
        self.is_cancelled = True
        if self.download_process:
            self.download_process.terminate()
        self.download_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)

    def download_video(self, url):
        format = self.format_var.get()
        quality = self.quality_var.get()
        save_path = self.save_path.get()
        browser = self.browser_var.get()

        if not url or not save_path:
            messagebox.showerror("错误", "请填写视频链接和保存位置")
            return

        yt_dlp_path = self.get_yt_dlp_path()
        if not yt_dlp_path:
            messagebox.showerror("错误", "无法找到 yt-dlp 执行文件")
            return

        ffmpeg_path = self.get_ffmpeg_path()
        if not ffmpeg_path:
            messagebox.showerror("错误", "无法找到 ffmpeg 执行文件")
            return

        command = [
            yt_dlp_path,
            "-o", f'{save_path}/%(title)s.%(ext)s',
            "--user-agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
            "--ffmpeg-location", ffmpeg_path,
        ]

        if self.use_cookies.get():
            command.extend(["--cookies-from-browser", browser])

        if format in ['mp3', 'm4a']:
            command.extend([
                "-x",
                "--audio-format", format,
                "--audio-quality", "192K"
            ])
        else:
            if quality == "高清8K":
                command.extend(["-f", f'bestvideo[height>=4320][ext={format}]+bestaudio/best[height>=4320][ext={format}]/best'])
            elif quality == "高清4K":
                command.extend(["-f", f'bestvideo[height>=2160][ext={format}]+bestaudio/best[height>=2160][ext={format}]/best'])
            else:
                command.extend(["-f", f'bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]/best'])
            command.extend(["--merge-output-format", format])

        command.append(url)

        try:
            print("下载命令:", command)
            self.download_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                     universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
            for line in self.download_process.stdout:
                if self.is_cancelled:
                    break
                while self.is_paused:
                    if self.is_cancelled:
                        break
                self.update_log(line.strip())
                self.update_progress_from_log(line)

            if not self.is_cancelled:
                self.progress_var.set(100)
                self.progress_label.config(text="100%")
                messagebox.showinfo("成功", f"视频已成功下载为 {format} 格式")
                self.open_download_folder(save_path)
        except Exception as e:
            if not self.is_cancelled:
                error_message = f"下载失败: {str(e)}"
                self.update_log(error_message)
                messagebox.showerror("错误", error_message)
        finally:
            self.progress_var.set(0)
            self.progress_label.config(text="0%")
            self.download_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.cancel_button.config(state=tk.DISABLED)

    def update_progress_from_log(self, log_line):
        progress_match = re.search(r'(\d+\.\d+)%', log_line)
        if progress_match:
            progress = float(progress_match.group(1))
            self.master.after(0, self.update_progress_ui, progress)

    def update_progress_ui(self, progress):
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{progress:.1f}%")

    def open_video_link(self):
        url = self.url_entry.get()
        if url:
            webbrowser.open(url)
        else:
            messagebox.showerror("错误", "请先输入视频链接")

    def open_download_folder(self, path):
        os.startfile(path)

    def update_log(self, msg):
        self.log_text.insert(tk.END, msg + '\n')
        self.log_text.see(tk.END)

    def get_yt_dlp_path(self):
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            return os.path.join(sys._MEIPASS, "yt-dlp.exe")
        else:
            # 如果是开发环境
            return os.path.join(os.getcwd(), "yt-dlp.exe")

    def get_ffmpeg_path(self):
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            return os.path.join(sys._MEIPASS, "ffmpeg.exe")
        else:
            # 如果是开发环境
            return os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
