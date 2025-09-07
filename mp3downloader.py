import yt_dlp
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy import Config



class MP3Downloader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=10, **kwargs)
        
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self.update_rect, pos=self.update_rect)
        
        self.output_folder = os.getcwd()
        
        self.url_input = TextInput(hint_text="Enter video URL", size_hint=(1, 0.2), background_color=(0, 1, 1, 1), foreground_color=(1, 1, 1, 1))
        self.add_widget(self.url_input)

        self.select_folder_button = Button(text=f"Folder: {os.path.basename(self.output_folder)} \nClick to select", size_hint=(1, 0.2), background_color=(1, 0, 1, 1))
        self.select_folder_button.bind(on_press=self.open_filechooser)
        self.add_widget(self.select_folder_button)

        self.download_button = Button(text="Download MP3", size_hint=(1, 0.2), background_color=(0, 1, 1, 1))
        self.download_button.bind(on_press=self.confirm_terms)
        self.add_widget(self.download_button)

        self.progress = ProgressBar(max=100, value=0, size_hint=(1, 0.2))
        self.add_widget(self.progress)

        self.status_label = Label(text="", size_hint=(1, 0.2), color=(0, 1, 0, 1))
        self.add_widget(self.status_label)
        
        self.show_startup_popup()

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def open_filechooser(self, instance):
        filechooser = FileChooserIconView()
        filechooser.dirselect = True
        filechooser.path = os.getcwd()
        
        popup = Popup(title="Select Download Folder", content=filechooser, size_hint=(0.9, 0.9))
        
        def on_selection(instance, selection):
            if selection:
                self.output_folder = selection[0]
                self.select_folder_button.text = f"Folder: {os.path.basename(self.output_folder)}"
                popup.dismiss()
        
        filechooser.bind(selection=on_selection)
        popup.open()
    
    def confirm_terms(self, instance):
        terms_text = ("By using this application, you agree to download only copyright-free or legally permitted content. \n "
                      "Downloading copyrighted material without permission is illegal and against platform Terms of Service. \n "
                      "The developer is not responsible for any misuse.")
        
        terms_popup = Popup(title="Terms of Use", content=Label(text=terms_text),
                            size_hint=(0.9, 0.5))
        accept_button = Button(text="Accept", size_hint=(1, 0.2))
        
        def accept(_):
            terms_popup.dismiss()
            self.start_download()
        
        accept_button.bind(on_press=accept)
        
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text=terms_text))
        layout.add_widget(accept_button)
        terms_popup.content = layout
        terms_popup.open()
    
    def show_startup_popup(self):
        startup_text = ("Welcome to the MP3 Downloader! Please use this application responsibly and adhere to all legal regulations. \n"
                        "Unauthorized downloading of copyrighted material is illegal.")
        
        startup_popup = Popup(title="Welcome", content=Label(text=startup_text), size_hint=(0.9, 0.5))
        close_button = Button(text="OK", size_hint=(1, 0.2))
        
        def close(_):
            startup_popup.dismiss()
        
        close_button.bind(on_press=close)
        
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text=startup_text))
        layout.add_widget(close_button)
        startup_popup.content = layout
        startup_popup.open()

    def start_download(self):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = "Please enter a valid URL."
            return
            
        if not os.path.exists(self.output_folder):
            self.status_label.text = "Selected folder does not exist!"
            return
            
        self.status_label.text = "Starting download..."
        self.progress.value = 0
        self.download_button.disabled = True
        
        try:
            self.download_mp3(url)
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"
            self.progress.value = 0
        finally:
            self.download_button.disabled = False

    def download_mp3(self, video_url):
        def progress_hook(d):
            if d['status'] == 'downloading':
                if 'total_bytes' in d and d['total_bytes']:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    self.progress.value = percent
                    self.status_label.text = f"Downloading... {percent:.1f}%"
            elif d['status'] == 'finished':
                self.status_label.text = "Converting to MP3..."
                self.progress.value = 90
            elif d['status'] == 'error':
                self.status_label.text = f"Download error: {d.get('error', 'Unknown error')}"
                self.progress.value = 0

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f"{self.output_folder}/%(title)s.%(ext)s",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [progress_hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            
        self.status_label.text = "Download Complete!"
        self.progress.value = 100

class MP3DownloaderApp(App):
    def build(self):
        return MP3Downloader()

if __name__ == "__main__":
    MP3DownloaderApp().run()
