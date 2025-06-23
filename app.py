from flask import Flask, request, render_template, jsonify, send_file, session
import os
import tempfile
import threading
import requests
import json
import re
from datetime import datetime
import yt_dlp
import instaloader
from werkzeug.utils import secure_filename
import zipfile
import shutil
import logging
from urllib.parse import urlparse
import uuid
import random
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-change-this-in-production'
app.config['SESSION_PERMANENT'] = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create downloads directory if it doesn't exist
DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

class UniversalDownloader:
    def __init__(self):
        self.session = requests.Session()
        
        # Rotate User Agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def detect_platform(self, url):
        """Detect the platform from URL"""
        url = url.lower()
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'instagram.com' in url:
            return 'instagram'
        elif 'facebook.com' in url or 'fb.watch' in url:
            return 'facebook'
        elif 'twitter.com' in url or 'x.com' in url:
            return 'twitter'
        elif 'tiktok.com' in url:
            return 'tiktok'
        elif 'pinterest.com' in url:
            return 'pinterest'
        elif 'linkedin.com' in url:
            return 'linkedin'
        elif 'snapchat.com' in url:
            return 'snapchat'
        elif 'reddit.com' in url:
            return 'reddit'
        elif 'twitch.tv' in url:
            return 'twitch'
        elif 'vimeo.com' in url:
            return 'vimeo'
        elif 'dailymotion.com' in url:
            return 'dailymotion'
        else:
            return 'unknown'

    def create_safe_filename(self, filename, max_length=100):
        """Create a safe filename"""
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename.strip()
        if len(filename) > max_length:
            filename = filename[:max_length]
        return filename

    def download_youtube_content(self, url, path):
        """Download YouTube videos with enhanced bot detection bypass"""
        try:
            # Enhanced yt-dlp options to bypass bot detection
            ydl_opts = {
                'outtmpl': os.path.join(path, '%(uploader)s - %(title)s.%(ext)s'),
                'format': 'best[height<=720]/best',  # Lower quality to reduce detection
                'writesubtitles': False,  # Disable to reduce requests
                'writeautomaticsub': False,
                'ignoreerrors': True,
                'no_warnings': True,
                'extractaudio': False,
                'audioformat': 'mp3',
                'audioquality': '128K',
                
                # Anti-bot detection headers
                'http_headers': {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Accept-Encoding': 'gzip,deflate',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                    'Keep-Alive': '300',
                    'Connection': 'keep-alive',
                },
                
                # Rate limiting to avoid detection
                'sleep_interval': 2,
                'max_sleep_interval': 5,
                'sleep_interval_requests': 1,
                
                # Retry settings
                'retries': 3,
                'fragment_retries': 3,
                'skip_unavailable_fragments': True,
                
                # Use different extractors
                'extractor_args': {
                    'youtube': {
                        'skip': ['hls', 'dash'],
                        'player_client': ['android', 'web']
                    }
                }
            }

            # Add random delay to mimic human behavior
            time.sleep(random.uniform(1, 3))

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=True)
                    if info is None:
                        return {'status': 'error', 'message': 'Failed to extract video information'}
                        
                    if 'entries' in info and info['entries']:  # Playlist
                        titles = [entry.get('title', 'Unknown') for entry in info['entries'] if entry]
                        return {
                            'status': 'success',
                            'message': f'Downloaded {len(titles)} videos from playlist',
                            'titles': titles[:5],
                            'type': 'playlist'
                        }
                    else:  # Single video
                        return {
                            'status': 'success',
                            'message': 'YouTube content downloaded successfully!',
                            'title': info.get('title', 'Unknown'),
                            'uploader': info.get('uploader', 'Unknown'),
                            'type': 'video'
                        }
                except Exception as extract_error:
                    logger.error(f"YouTube extraction error: {str(extract_error)}")
                    # Try alternative method with different settings
                    return self.download_youtube_fallback(url, path)
                    
        except Exception as e:
            logger.error(f"YouTube download error: {str(e)}")
            return {'status': 'error', 'message': f'YouTube temporarily unavailable. Please try again later.'}

    def download_youtube_fallback(self, url, path):
        """Fallback method for YouTube downloads with minimal settings"""
        try:
            ydl_opts = {
                'outtmpl': os.path.join(path, 'YouTube_%(title)s.%(ext)s'),
                'format': 'worst',  # Use worst quality to avoid restrictions
                'no_warnings': True,
                'ignoreerrors': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    'status': 'success',
                    'message': 'YouTube content downloaded (fallback mode)',
                    'title': info.get('title', 'YouTube Video') if info else 'Unknown',
                    'type': 'video'
                }
        except Exception as e:
            return {'status': 'error', 'message': 'YouTube download failed. Service may be temporarily blocked.'}

    def download_instagram_content(self, url, path):
        """Download Instagram content with enhanced authentication"""
        try:
            # Create Instaloader with anti-detection settings
            loader = instaloader.Instaloader(
                dirname_pattern=path,
                filename_pattern='{profile}_{mediaid}_{date_utc}',
                download_videos=True,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,  # Disable to reduce requests
                compress_json=False,
                user_agent=random.choice(self.user_agents),
                request_timeout=30,
                rate_controller=lambda query_type: time.sleep(random.uniform(2, 4))  # Rate limiting
            )

            # Add random delay
            time.sleep(random.uniform(1, 3))

            if '/stories/' in url:
                # Story URL
                username = self.extract_instagram_username(url)
                if username:
                    try:
                        profile = instaloader.Profile.from_username(loader.context, username)
                        story_count = 0
                        for story in loader.get_stories([profile.userid]):
                            for item in story.get_items():
                                loader.download_storyitem(item, target=username)
                                story_count += 1
                        return {
                            'status': 'success',
                            'message': f'Downloaded {story_count} Instagram stories for {username}',
                            'type': 'stories'
                        }
                    except Exception as story_error:
                        return {'status': 'error', 'message': f'Stories not accessible: {str(story_error)}'}
                        
            elif '/reel/' in url or '/p/' in url or '/tv/' in url:
                # Post, Reel, or IGTV
                shortcode = self.extract_instagram_shortcode(url)
                if not shortcode:
                    return {'status': 'error', 'message': 'Invalid Instagram URL format'}
                    
                try:
                    post = instaloader.Post.from_shortcode(loader.context, shortcode)
                    loader.download_post(post, target=post.owner_username)
                    
                    content_type = 'reel' if post.is_video else 'post'
                    if hasattr(post, 'typename') and post.typename == 'GraphSidecar':
                        content_type = 'carousel'
                    
                    return {
                        'status': 'success',
                        'message': f'Instagram {content_type} downloaded successfully!',
                        'username': post.owner_username,
                        'type': content_type
                    }
                except Exception as post_error:
                    return {'status': 'error', 'message': f'Post not accessible: {str(post_error)}'}
            else:
                # Profile URL - download recent posts
                username = self.extract_instagram_username(url)
                try:
                    profile = instaloader.Profile.from_username(loader.context, username)
                    count = 0
                    for post in profile.get_posts():
                        if count >= 5:  # Limit to 5 recent posts to avoid rate limiting
                            break
                        loader.download_post(post, target=username)
                        count += 1
                        time.sleep(random.uniform(2, 4))  # Rate limiting
                    
                    return {
                        'status': 'success',
                        'message': f'Downloaded {count} recent posts from {username}',
                        'type': 'profile'
                    }
                except Exception as profile_error:
                    return {'status': 'error', 'message': f'Profile not accessible: {str(profile_error)}'}

        except Exception as e:
            logger.error(f"Instagram download error: {str(e)}")
            return {'status': 'error', 'message': 'Instagram temporarily unavailable. Please try again later.'}

    def download_generic_content(self, url, path):
        """Download from any supported platform using yt-dlp with anti-detection"""
        try:
            ydl_opts = {
                'outtmpl': os.path.join(path, '%(extractor)s_%(title)s.%(ext)s'),
                'format': 'best[height<=720]/best',
                'no_warnings': True,
                'ignoreerrors': True,
                'http_headers': {
                    'User-Agent': random.choice(self.user_agents),
                },
                'sleep_interval': 1,
                'max_sleep_interval': 3,
                'retries': 2
            }

            time.sleep(random.uniform(1, 2))

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    'status': 'success',
                    'message': 'Content downloaded successfully!',
                    'title': info.get('title', 'Unknown') if info else 'Unknown',
                    'extractor': info.get('extractor', 'Unknown') if info else 'Unknown',
                    'type': 'media'
                }
        except Exception as e:
            logger.error(f"Generic download error: {str(e)}")
            return {'status': 'error', 'message': f'Download failed: Platform may be temporarily unavailable'}

    def extract_instagram_shortcode(self, url):
        """Extract shortcode from Instagram URL"""
        patterns = [
            r'/p/([^/?]+)',
            r'/reel/([^/?]+)',
            r'/tv/([^/?]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def extract_instagram_username(self, url):
        """Extract username from Instagram URL"""
        match = re.search(r'instagram\.com/([^/?]+)', url)
        if match:
            return match.group(1)
        return None

    def download_content(self, url, custom_path=None):
        """Main download function with enhanced error handling"""
        path = custom_path or DOWNLOAD_DIR
        platform = self.detect_platform(url)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_folder = os.path.join(path, f"{platform}_{timestamp}")
        os.makedirs(download_folder, exist_ok=True)

        try:
            if platform == 'youtube':
                return self.download_youtube_content(url, download_folder)
            elif platform == 'instagram':
                return self.download_instagram_content(url, download_folder)
            elif platform in ['tiktok', 'twitter', 'facebook', 'reddit', 'twitch', 'vimeo']:
                return self.download_generic_content(url, download_folder)
            else:
                return self.download_generic_content(url, download_folder)
        except Exception as e:
            logger.error(f"Unexpected download error: {str(e)}")
            return {'status': 'error', 'message': f'Service temporarily unavailable: {str(e)}'}

# Initialize downloader
downloader = UniversalDownloader()

def clear_all_downloads():
    """Clear all downloaded files and folders"""
    try:
        if os.path.exists(DOWNLOAD_DIR):
            shutil.rmtree(DOWNLOAD_DIR)
            os.makedirs(DOWNLOAD_DIR)
        logger.info("Downloads directory cleared due to page refresh")
        return True
    except Exception as e:
        logger.error(f"Error clearing downloads: {str(e)}")
        return False

@app.before_request
def check_session():
    """Check if this is a new session/page refresh and clear data"""
    if request.endpoint == 'index':
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            session['is_new_session'] = True
        else:
            if not session.get('is_new_session', False):
                clear_all_downloads()
            session['is_new_session'] = False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    """Handle download requests with enhanced error handling"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'status': 'error', 'message': 'URL is required'})

        # Validate URL
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return jsonify({'status': 'error', 'message': 'Invalid URL format'})
        except:
            return jsonify({'status': 'error', 'message': 'Invalid URL format'})

        platform = downloader.detect_platform(url)
        logger.info(f"Downloading from {platform}: {url}")

        result = downloader.download_content(url)
        result['platform'] = platform
        result['url'] = url

        return jsonify(result)

    except Exception as e:
        logger.error(f"Download endpoint error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Server error: Please try again later'})

# Keep all other routes the same as in the previous code...
# (bulk_download, list_downloads, download_file, download_folder, clear_downloads_endpoint)

@app.route('/bulk-download', methods=['POST'])
def bulk_download():
    """Handle bulk download requests"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'status': 'error', 'message': 'URLs list is required'})

        results = []
        for i, url in enumerate(urls):
            if url.strip():
                logger.info(f"Bulk downloading {i+1}/{len(urls)}: {url}")
                result = downloader.download_content(url.strip())
                result['url'] = url
                result['platform'] = downloader.detect_platform(url)
                results.append(result)
                
                # Add delay between downloads to avoid rate limiting
                if i < len(urls) - 1:
                    time.sleep(random.uniform(3, 6))

        success_count = len([r for r in results if r['status'] == 'success'])
        
        return jsonify({
            'status': 'success',
            'message': f'Processed {len(results)} URLs - {success_count} successful',
            'results': results,
            'success_count': success_count,
            'total_count': len(results)
        })

    except Exception as e:
        logger.error(f"Bulk download error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Bulk download error: {str(e)}'})

@app.route('/downloads')
def list_downloads():
    """List downloaded files and folders"""
    try:
        items = []
        if os.path.exists(DOWNLOAD_DIR):
            for item in os.listdir(DOWNLOAD_DIR):
                item_path = os.path.join(DOWNLOAD_DIR, item)
                if os.path.isfile(item_path):
                    items.append({
                        'name': item,
                        'type': 'file',
                        'size': os.path.getsize(item_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(item_path)).isoformat()
                    })
                elif os.path.isdir(item_path):
                    file_count = len([f for f in os.listdir(item_path) 
                                    if os.path.isfile(os.path.join(item_path, f))])
                    items.append({
                        'name': item,
                        'type': 'folder',
                        'file_count': file_count,
                        'modified': datetime.fromtimestamp(os.path.getmtime(item_path)).isoformat()
                    })
        
        items.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify({'items': items})

    except Exception as e:
        logger.error(f"List downloads error: {str(e)}")
        return jsonify({'error': str(e)})

@app.route('/download-file/<filename>')
def download_file(filename):
    """Download a specific file"""
    try:
        safe_filename = secure_filename(filename)
        file_path = os.path.join(DOWNLOAD_DIR, safe_filename)
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404

    except Exception as e:
        logger.error(f"Download file error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download-folder/<foldername>')
def download_folder(foldername):
    """Download a folder as ZIP"""
    try:
        safe_foldername = secure_filename(foldername)
        folder_path = os.path.join(DOWNLOAD_DIR, safe_foldername)
        
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            temp_zip.close()

            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, folder_path)
                        zipf.write(file_path, arcname)

            return send_file(temp_zip.name, as_attachment=True, 
                           download_name=f'{safe_foldername}.zip')
        else:
            return jsonify({'error': 'Folder not found'}), 404

    except Exception as e:
        logger.error(f"Download folder error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/clear-downloads', methods=['POST'])
def clear_downloads_endpoint():
    """Clear all downloaded files"""
    try:
        success = clear_all_downloads()
        if success:
            return jsonify({'status': 'success', 'message': 'Downloads cleared successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to clear downloads'})
    except Exception as e:
        logger.error(f"Clear downloads error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Error clearing downloads: {str(e)}'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Universal Downloader Server Starting...")
    print(f"📁 Downloads will be saved to: {DOWNLOAD_DIR}")
    print("🌐 Server running on http://localhost:5000")
    print("⚡ Enhanced anti-bot detection enabled")
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
