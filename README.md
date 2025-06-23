
# ✨ Universal Social Media Downloader

A powerful, modern web application that allows you to download content from multiple social media platforms including YouTube, Instagram, TikTok, Twitter, Facebook, Reddit, and more. Built with Flask backend and featuring a beautiful glassmorphism UI design with animated backgrounds.

![Universal Downloader](https://img.shields.io/badge/Platform-Multi--Social--Media-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Features

### 🎯 **Smart Platform Detection**
- Automatically detects platform and content type from any supported URL
- Intelligent algorithms for URL parsing and content identification
- Support for shortened URLs and various link formats

### 📱 **All Content Types**
- **Videos**: HD videos, shorts, reels, stories
- **Photos**: High-resolution images and carousels
- **Playlists**: Complete YouTube playlists and collections
- **Stories**: Instagram and Facebook stories
- **Metadata**: Subtitles, descriptions, and timestamps

### 📦 **Bulk Processing**
- Download multiple URLs simultaneously
- Real-time progress tracking for each download
- Batch management with detailed status reports
- Error handling for failed downloads

### 🔒 **Privacy First**
- All processing done locally on your server
- Automatic data cleanup on page refresh
- No permanent storage of user data
- Session-based temporary file management

### ⚡ **Lightning Fast**
- Optimized download speeds with parallel processing
- Intelligent compression and file management
- Minimal waiting time with progress visualization
- Asynchronous processing for better performance

### 🌐 **Cross-Platform**
- Works on Windows, macOS, Linux, and mobile devices
- Responsive glassmorphism design
- Modern UI with animated backgrounds
- Touch-friendly interface for mobile users

## 🎨 **Modern UI Design**
- **Glassmorphism Effects**: Transparent glass design with backdrop blur
- **Animated Backgrounds**: Floating shapes and gradient animations
- **Social Media Integration**: Platform-specific icons and colors
- **Smooth Transitions**: Elegant hover effects and animations
- **Dark Theme**: Eye-friendly dark interface with glowing elements

## 🔧 **Supported Platforms**

### Video Platforms
- **YouTube** 📺 - Videos, Shorts, Playlists, Live streams
- **TikTok** 🎵 - Videos, compilations
- **Twitch** 🎮 - VODs, clips, highlights
- **Vimeo** 🎬 - HD videos, private content
- **Dailymotion** 📹 - Videos and playlists

### Social Media Platforms
- **Instagram** 📷 - Posts, Reels, Stories, IGTV, Carousels
- **Twitter/X** 🐦 - Videos, images, threads, spaces
- **Facebook** 👥 - Videos, posts, stories, reels
- **Reddit** 🔴 - Videos, images, GIFs, posts
- **LinkedIn** 💼 - Videos, posts, articles
- **Pinterest** 📌 - Images, pins, boards
- **Snapchat** 👻 - Public stories and highlights

## 📋 **Requirements**

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 1GB free space for dependencies
- **Internet**: Stable internet connection for downloads

### Python Dependencies
```
Flask==2.3.3
requests==2.31.0
yt-dlp==2023.10.13
instaloader==4.10.3
Werkzeug==2.3.7
```

## 🛠️ **Installation**

### 1. Clone the Repository
```
git clone https://github.com/ocean-master0/Universal-Video-Downloader.git
cd universal-social-media-downloader
```

### 2. Create Virtual Environment

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate


### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Run the Application
```
python app.py
```

### 5. Access the Application
Open your web browser and navigate to:
```
http://localhost:5000
```

## 📖 **Usage**

### Single Download
1. **Enter URL**: Paste the social media URL in the input field
2. **Detect Platform**: Click "Detect Platform" to identify the source
3. **Download**: Click "Download Now" to start the process
4. **Monitor Progress**: Watch the real-time progress bar
5. **Access Files**: Download completed files from "My Downloads" tab

### Bulk Download
1. **Multiple URLs**: Enter multiple URLs (one per line) in the bulk textarea
2. **Start Batch**: Click "Download All" to process all URLs
3. **Track Progress**: Monitor individual download status
4. **Review Results**: Check success/failure summary
5. **Download Files**: Access all downloaded content in bulk

### File Management
- **View Downloads**: Browse all downloaded files and folders
- **Download Files**: Click download button for individual files
- **Folder Archives**: Folders are automatically zipped for download
- **Clear Data**: Use "Clear All Downloads" for cleanup
- **Auto-Cleanup**: Data automatically cleared on page refresh

## 🎯 **Quick Start Examples**

### YouTube Video
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### Instagram Post
```
https://www.instagram.com/p/ABC123xyz/
```

### TikTok Video
```
https://www.tiktok.com/@username/video/1234567890
```

### Bulk Download
```
https://www.youtube.com/watch?v=example1
https://www.instagram.com/p/example2/
https://www.tiktok.com/@user/video/example3
```

## 🔧 **Configuration**

### Environment Variables
Create a `.env` file in the project root:
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-super-secret-key-here
DOWNLOAD_DIR=./downloads
MAX_DOWNLOAD_SIZE=1000  # MB
CLEANUP_INTERVAL=3600   # seconds
```

### Advanced Settings
Edit `app.py` to modify:
- Download quality settings
- File naming patterns
- Supported platforms
- Rate limiting
- Error handling

## 🤝 **Contributing**

We welcome contributions! Please follow these steps:

### 1. Fork the Repository
```
git fork https://github.com/ocean-master0/Universal-Video-Downloader.git
```

### 2. Create Feature Branch
```
git checkout -b feature/amazing-feature
```

### 3. Make Changes
- Follow Python PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed

### 4. Test Your Changes
```
python -m pytest tests/
```

### 5. Submit Pull Request
- Provide clear description of changes
- Include screenshots for UI changes
- Reference any related issues
- Ensure all tests pass

### 📝 **Contribution Guidelines**
- **Code Style**: Follow PEP 8 standards
- **Documentation**: Update README and docstrings
- **Testing**: Add tests for new features
- **Commits**: Use conventional commit messages
- **Issues**: Use provided issue templates

## 🐛 **Troubleshooting**

### Common Issues

#### **Download Failures**
- **Solution**: Check internet connection and URL validity
- **Platform Issues**: Some platforms may block automated downloads
- **Rate Limiting**: Wait between downloads to avoid restrictions

#### **Installation Problems**
- **Python Version**: Ensure Python 3.8+ is installed
- **Dependencies**: Try updating pip: `pip install --upgrade pip`
- **Permissions**: Run with administrator/sudo privileges if needed

#### **Performance Issues**
- **Memory**: Close other applications to free up RAM
- **Storage**: Ensure sufficient disk space for downloads
- **Network**: Use stable internet connection for large files

### Debug Mode
Enable debug mode for detailed error messages:
```
export FLASK_DEBUG=1
python app.py
```

### Log Files
Check logs for detailed error information:
```
tail -f logs/app.log
```

## 📊 **Performance**

### Benchmarks
- **Single Download**: 2-10 seconds average
- **Bulk Downloads**: 10-50 URLs per minute
- **Memory Usage**: 100-500MB depending on content
- **Disk Space**: Varies by content size

### Optimization Tips
- **Batch Size**: Limit bulk downloads to 20 URLs max
- **Quality Settings**: Lower quality for faster downloads
- **Cleanup**: Regular cleanup to maintain performance
- **Updates**: Keep dependencies updated

## 🔮 **Roadmap**

### Upcoming Features
- [ ] **Mobile App**: React Native mobile application
- [ ] **Cloud Storage**: Google Drive, Dropbox integration
- [ ] **Scheduled Downloads**: Cron-like scheduling system
- [ ] **User Accounts**: Multi-user support with authentication
- [ ] **API Endpoints**: RESTful API for external integration
- [ ] **Browser Extension**: Chrome/Firefox extension
- [ ] **Docker Support**: Containerized deployment
- [ ] **Download Queue**: Advanced queue management

### Version History
- **v1.0.0**: Initial release with basic functionality
- **v1.1.0**: Added glassmorphism UI and animations
- **v1.2.0**: Bulk download support and improved error handling
- **v1.3.0**: Auto-cleanup and session management

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **yt-dlp**: Amazing tool for video downloads
- **Instaloader**: Instagram content downloading
- **Flask**: Lightweight web framework
- **Font Awesome**: Beautiful icons
- **Contributors**: All the amazing people who helped

---

**⭐ If you find this project helpful, please consider giving it a star on GitHub!**

Made with ❤️ by [Abhishek Kumar](https://github.com/ocean-master0)
```

## 🚀 Live Demo

You can try the application live here:

🔗 [Live Website](https://universal-video-downloader-78zw.onrender.com)

## ⚠️ Notice: If the Live Site Doesn't Work

If the live demo doesn’t function correctly for some platforms like **YouTube** or **Instagram**, it’s likely due to restrictions on cloud-hosted environments such as Render. These platforms actively detect and block automated usage from datacenter IPs.

### 🛠 Root Cause Analysis

The application may fail to download content from certain sites when hosted on Render or similar cloud services. Common reasons include:

- **YouTube**: Detects requests from datacenter IP addresses (like those used by Render) and blocks them, considering them as bot traffic.

- **Instagram**: Returns **401 Unauthorized** errors because it blocks unauthenticated or automated requests coming from cloud/VPS IPs.

- **Platform Protections**: Many websites have implemented strict anti-bot measures that detect and block scraping or automated downloads from shared or virtual servers.

## 💻 Recommended Solution

To ensure the program works correctly, it's best to **clone and run the project locally** on your own computer:

```bash
git clone https://github.com/ocean-master0/Universal-Video-Downloader.git
cd Universal-Video-Downloader
pip install -r requirements.txt
python app.py
```
---
