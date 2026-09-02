import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from ytmusicapi import YTMusic
import yt_dlp

class MusicApp(App):
    def build(self):
        self.ytmusic = YTMusic()
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Search Bar
        search_box = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=5)
        self.search_input = TextInput(hint_text="Search song or artist...", multiline=False)
        search_btn = Button(text="Search", size_hint_x=0.3, background_color=(0.2, 0.6, 1, 1))
        search_btn.bind(on_press=self.start_search)
        
        search_box.add_widget(self.search_input)
        search_box.add_widget(search_btn)
        self.layout.add_widget(search_box)

        # Status Label
        self.status_label = Label(text="Welcome to Nova Music!", size_hint_y=0.1)
        self.layout.add_widget(self.status_label)

        # Scrollable Results List
        self.scroll = ScrollView(size_hint=(1, 0.75))
        self.results_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.results_list.bind(minimum_height=self.results_list.setter('height'))
        self.scroll.add_widget(self.results_list)
        self.layout.add_widget(self.scroll)

        return self.layout

    def start_search(self, instance):
        query = self.search_input.text.strip()
        if not query:
            return
        self.status_label.text = f"Searching for '{query}'..."
        threading.Thread(target=self.run_search, args=(query,), daemon=True).start()

    def run_search(self, query):
        try:
            results = self.ytmusic.search(query, filter="songs", limit=6)
            self.results_list.clear_widgets()

            for item in results:
                title = item.get("title", "Unknown")
                artists = ", ".join([a["name"] for a in item.get("artists", [])])
                video_id = item.get("videoId")

                btn_text = f"▶ {title} - {artists}"
                btn = Button(text=btn_text, size_hint_y=None, height=60)
                btn.bind(on_press=lambda inst, v=video_id, t=title: self.play_song(v, t))
                self.results_list.add_widget(btn)

            self.status_label.text = "Select a song to play:"
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"

    def play_song(self, video_id, title):
        self.status_label.text = f"Loading stream for: {title}..."
        threading.Thread(target=self._extract_and_play, args=(video_id, title), daemon=True).start()

    def _extract_and_play(self, video_id, title):
        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {'format': 'bestaudio/best', 'quiet': True}

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                stream_url = info['url']

            self.status_label.text = f"Playing: {title}"
            from kivy.core.audio import SoundLoader
            sound = SoundLoader.load(stream_url)
            if sound:
                sound.play()
        except Exception as e:
            self.status_label.text = f"Playback Error: {str(e)}"

if __name__ == "__main__":
    MusicApp().run()
