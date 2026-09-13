# musicTK Media Lab

This folder is for learning media-processing architecture using files you own or have permission to process.

## Exercise 1: local media pipeline

1. Put a video you own in this folder locally (do not commit the video to GitHub).
2. Use a local backend to accept the file.
3. Extract an audio-only copy with ffmpeg.
4. Return the resulting audio file to the browser.
5. Import that audio into musicTK's IndexedDB library.

The production musicTK site stays static on GitHub Pages. The media-processing backend is intentionally a separate local service.

## YouTube-owned-video experiment

For a video you control, first use an authorized way to obtain your own source file (for example, YouTube Studio's download/export facilities). Then run that local source file through the same pipeline. This teaches the same upload -> process -> download -> player architecture without building a general-purpose YouTube downloader.
