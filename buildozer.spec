[app]
title = TRISULA Downloader
package.name = trisuladownloader
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,ttf
version = 0.1
requirements = python3,kivy,yt_dlp,plyer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
