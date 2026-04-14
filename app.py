import streamlit as st
import yt_dlp
import imageio_ffmpeg as ffmpeg
from pathlib import Path
import tempfile
import subprocess
from mutagen import File as MutagenFile

st.set_page_config(page_title="Media Downloader & MP3 Trimmer", page_icon="🎬", layout="centered")

download_folder = Path("downloads")
download_folder.mkdir(exist_ok=True)

try:
    FFMPEG_PATH = ffmpeg.get_ffmpeg_exe()
except Exception as e:
    st.error(f"FFmpeg failed to load: {e}")
    st.stop()

st.title("Media Downloader And MP3 Trimmer")

tab1, tab2 = st.tabs(["Download", "Trim Audio"])

with tab1:
    url = st.text_input("Enter URL")

    quality_options = {
        "Best Quality": "best",
        "1080p": "1080",
        "720p": "720",
        "480p": "480",
        "360p": "360"
    }
    selected_label = st.selectbox("Select Quality", list(quality_options.keys()))
    resolution = quality_options[selected_label]

    format_options = {
        "Video (MP4)": "mp4",
        "Audio (MP3)": "mp3"
    }
    format_label = st.selectbox("Output Format", list(format_options.keys()))
    output_format = format_options[format_label]

    if st.button("Start Download") and url:
        with st.spinner("Fetching media info..."):
            ydl_opts = {
                'outtmpl': str(download_folder / '%(title)s.%(ext)s'),
                'ffmpeg_location': FFMPEG_PATH,
                'noplaylist': True,
                'quiet': False,
                'http_headers': {'User-Agent': 'Mozilla/5.0'},
            }

            if output_format == 'mp3':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '0'
                    }],
                    'keepvideo': False,
                })
            else:
                ydl_opts.update({
                    'format': (
                        f'bestvideo[height<={resolution}]+bestaudio/best'
                        if resolution != 'best' else
                        'bestvideo[height<=2160]+bestaudio/best'
                    ),
                    'merge_output_format': 'mp4',
                })

            def hook(d):
                if d['status'] == 'downloading':
                    pct = d.get('_percent_str', '0%').replace('%', '')
                    try:
                        progress = float(pct) / 100
                    except:
                        progress = 0
                    bar.progress(min(progress, 1.0))
                elif d['status'] == 'finished':
                    status.text("Finalizing file...")

            ydl_opts['progress_hooks'] = [hook]
            bar = st.progress(0)
            status = st.empty()

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                pattern = "*.mp3" if output_format == "mp3" else "*.mp4"
                files = list(download_folder.glob(pattern))
                final_file = max(files, key=lambda f: f.stat().st_mtime)

                st.success(f"{final_file.name} is ready. Click download to save the file.")

                with open(final_file, "rb") as f:
                    st.download_button(
                        label="Download File",
                        data=f,
                        file_name=final_file.name,
                        mime="audio/mpeg" if output_format == "mp3" else "video/mp4"
                    )
            except Exception as e:
                st.error(str(e))

with tab2:
    uploaded = st.file_uploader("Upload audio", type=["mp3", "wav", "ogg", "m4a", "aac", "flac"])

    def get_duration_seconds(path):
        m = MutagenFile(path)
        return float(m.info.length)

    def ffmpeg_trim_bytes(in_path, start_s, end_s):
        cmd = [
            FFMPEG_PATH,
            "-hide_banner", "-loglevel", "error",
            "-ss", str(start_s),
            "-to", str(end_s),
            "-i", in_path,
            "-vn",
            "-c:a", "libmp3lame",
            "-q:a", "2",
            "-f", "mp3",
            "pipe:1",
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return proc.stdout

    if uploaded:
        suffix = "." + uploaded.name.split(".")[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.read())
            path = tmp.name

        st.audio(path)

        duration = get_duration_seconds(path)

        if "start_sec" not in st.session_state:
            st.session_state.start_sec = 0.0
        if "end_sec" not in st.session_state:
            st.session_state.end_sec = min(30.0, duration)

        start_input = st.text_input("Start (seconds)", value=str(st.session_state.start_sec))
        end_input = st.text_input("End (seconds)", value=str(st.session_state.end_sec))

        try:
            st.session_state.start_sec = float(start_input)
            st.session_state.end_sec = float(end_input)
        except:
            st.error("Invalid input")
            st.stop()

        slider_vals = st.slider(
            "Select range",
            0.0,
            float(duration),
            (float(st.session_state.start_sec), float(st.session_state.end_sec)),
            0.1
        )

        st.session_state.start_sec, st.session_state.end_sec = slider_vals

        if st.session_state.start_sec < st.session_state.end_sec:
            if st.button("Trim"):
                out = ffmpeg_trim_bytes(path, st.session_state.start_sec, st.session_state.end_sec)
                st.audio(out)
                st.download_button(
                    label="Download Trimmed MP3",
                    data=out,
                    file_name="trimmed.mp3",
                    mime="audio/mpeg"
                )
