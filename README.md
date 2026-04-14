# Universal Media Downloader & MP3 Trimmer

Streamlit-based application for downloading media from multiple platforms and trimming audio files locally.

## Features

- Download media from:
  - YouTube
  - Instagram
  - Vimeo
  - Twitter
  - Other supported sites via yt-dlp

- Output formats:
  - MP4 (video)
  - MP3 (audio)

- Quality selection for video downloads

- Audio trimming:
  - Upload local audio files
  - Set precise start and end times
  - Interactive range selector
  - Export trimmed MP3

## Requirements

Install the required Python packages:

```bash
pip install streamlit yt-dlp imageio-ffmpeg mutagen
```
After installing the required Python packages, run:

```bash
streamlit run app.py
```

### Authors

* **Chay** - [ChayScripts](https://github.com/ChayScripts)

### Contributing

Please follow [github flow](https://guides.github.com/introduction/flow/index.html) for contributing.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
