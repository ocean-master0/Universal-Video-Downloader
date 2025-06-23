from flask import Flask, request, render_template, jsonify, send_file, session
import os
import tempfile
import threading
import requests
import json
import re
from datetime import datetime, timedelta
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
from functools import wraps
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-change-this-in-production'
app.config['SESSION_PERMANENT'] = False

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create downloads directory
DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Rate limiting storage
rate_limit_storage = {}

def rate_limit(max_requests=10, window=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '127.0.0.1'))
            current_time = time.time()
            
            if client_ip not in rate_limit_storage:
                rate_limit_storage[client_ip] = []
            
            # Clean old requests
            rate_limit_storage[client_ip] = [
                req_time for req_time in rate_limit_storage[client_ip] 
                if current_time - req_time < window
            ]
            
            if len(rate_limit_storage[client_ip]) >= max_requests:
                return jsonify({
                    'status': 'error', 
                    'message': f'Rate limit exceeded. Please wait {window} seconds.'
                }), 429
            
            rate_limit_storage[client_ip].append(current_time)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class AdvancedUniversalDownloader:
    def __init__(self):
        self.session = requests.Session()
        
        # Enhanced User Agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
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
        """Enhanced platform detection"""
        url_lower = url.lower()
        
        platform_patterns = {
            'youtube': [r'youtube\.com', r'youtu\.be', r'm\.youtube\.com'],
            'instagram': [r'instagram\.com', r'instagr\.am'],
            'tiktok': [r'tiktok\.com', r'vm\.tiktok\.com'],
            'twitter': [r'twitter\.com', r'x\.com', r't\.co'],
            'facebook': [r'facebook\.com', r'fb\.watch'],
            'reddit': [r'reddit\.com', r'redd\.it'],
            'twitch': [r'twitch\.tv'],
            'vimeo': [r'vimeo\.com'],
            'dailymotion': [r'dailymotion\.com']
        }
        
        for platform, patterns in platform_patterns.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    return platform
        
        return 'unknown'

    def safe_instaloader_operation(self, operation, *args, **kwargs):
        """Safely execute Instaloader operations with proper error handling"""
        max_retries = 3
        base_delay = 5
        
        for attempt in range(max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                error_str = str(e).lower()
                
                # Handle specific Instagram errors
                if 'wait_before_query' in error_str or 'nonetype' in error_str:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt) + random.uniform(1, 5)
                        logger.warning(f"Instagram rate limit hit, waiting {delay:.1f} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        return {'status': 'error', 'message': 'Instagram is temporarily blocking requests. Please try again later.'}
                
                elif '401' in error_str or 'unauthorized' in error_str:
                    return {'status': 'error', 'message': 'Instagram access denied. Content may be private or restricted.'}
                
                elif '429' in error_str or 'too many requests' in error_str:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt) + random.uniform(5, 15)
                        logger.warning(f"Rate limited, waiting {delay:.1f} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        return {'status': 'error', 'message': 'Instagram rate limit exceeded. Please wait 15-30 minutes before trying again.'}
                
                elif 'badresponse' in error_str or 'fetching post metadata failed' in error_str:
                    return {'status': 'error', 'message': 'Instagram post not accessible. It may be private, deleted, or restricted.'}
                
                else:
                    if attempt < max_retries - 1:
                        delay = random.uniform(3, 8)
                        logger.warning(f"Instagram error: {str(e)}, retrying in {delay:.1f} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        return {'status': 'error', 'message': f'Instagram download failed: {str(e)}'}
        
        return {'status': 'error', 'message': 'All retry attempts failed'}

    def download_instagram_content(self, url, path):
        """Enhanced Instagram downloader with comprehensive error handling"""
        try:
            # Create custom rate controller to avoid wait_before_query issues
            def custom_rate_controller(query_type):
                """Custom rate controller that handles None objects safely"""
                try:
                    delay = random.uniform(3, 8)
                    time.sleep(delay)
                except Exception:
                    time.sleep(5)  # Fallback delay
            
            # Create Instaloader with enhanced settings
            loader_config = {
                'dirname_pattern': path,
                'filename_pattern': '{profile}_{mediaid}_{date_utc}',
                'download_videos': True,
                'download_video_thumbnails': False,
                'download_geotags': False,
                'download_comments': False,
                'save_metadata': False,
                'compress_json': False,
                'user_agent': random.choice(self.user_agents),
                'request_timeout': 30
            }
            
            # Safely create Instaloader instance
            try:
                loader = instaloader.Instaloader(**loader_config)
                # Set custom rate controller
                loader.context.rate_controller = custom_rate_controller
            except Exception as e:
                logger.error(f"Failed to create Instaloader instance: {str(e)}")
                return {'status': 'error', 'message': 'Instagram service initialization failed'}

            # Add delay to mimic human behavior
            time.sleep(random.uniform(2, 5))

            # Handle different Instagram URL types
            if '/stories/' in url:
                username = self.extract_instagram_username(url)
                if not username:
                    return {'status': 'error', 'message': 'Invalid Instagram stories URL'}
                
                def download_stories():
                    profile = instaloader.Profile.from_username(loader.context, username)
                    story_count = 0
                    for story in loader.get_stories([profile.userid]):
                        for item in story.get_items():
                            loader.download_storyitem(item, target=username)
                            story_count += 1
                            if story_count >= 10:  # Limit stories
                                break
                    return {
                        'status': 'success',
                        'message': f'Downloaded {story_count} Instagram stories for {username}',
                        'type': 'stories'
                    }
                
                return self.safe_instaloader_operation(download_stories)
                
            elif any(pattern in url for pattern in ['/reel/', '/p/', '/tv/']):
                shortcode = self.extract_instagram_shortcode(url)
                if not shortcode:
                    return {'status': 'error', 'message': 'Invalid Instagram URL format'}
                
                def download_post():
                    # Add extra safety checks
                    try:
                        post = instaloader.Post.from_shortcode(loader.context, shortcode)
                        if post is None:
                            raise Exception("Post not found")
                        
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
                    except AttributeError as e:
                        if 'wait_before_query' in str(e):
                            raise Exception("Rate limit exceeded")
                        else:
                            raise e
                
                return self.safe_instaloader_operation(download_post)
            
            else:
                # Profile URL
                username = self.extract_instagram_username(url)
                if not username:
                    return {'status': 'error', 'message': 'Invalid Instagram profile URL'}
                
                def download_profile():
                    profile = instaloader.Profile.from_username(loader.context, username)
                    count = 0
                    for post in profile.get_posts():
                        if count >= 5:  # Limit to prevent issues
                            break
                        loader.download_post(post, target=username)
                        count += 1
                        time.sleep(random.uniform(4, 8))  # Rate limiting
                    
                    return {
                        'status': 'success',
                        'message': f'Downloaded {count} recent posts from {username}',
                        'type': 'profile'
                    }
                
                return self.safe_instaloader_operation(download_profile)

        except Exception as e:
            logger.error(f"Instagram download error: {str(e)}")
            error_message = str(e).lower()
            
            if 'wait_before_query' in error_message or 'nonetype' in error_message:
                return {'status': 'error', 'message': 'Instagram temporarily blocked. Please wait 15-30 minutes and try again.'}
            elif '401' in error_message or 'unauthorized' in error_message:
                return {'status': 'error', 'message': 'Instagram content is private or restricted.'}
            elif '429' in error_message:
                return {'status': 'error', 'message': 'Instagram rate limit exceeded. Please wait before trying again.'}
            else:
                return {'status': 'error', 'message': 'Instagram service temporarily unavailable. Please try again later.'}

    def download_youtube_content(self, url, path):
        """Enhanced YouTube downloader with multiple fallback strategies"""
        strategies = [
            {
                'format': 'best[height<=1080]/best',
                'writesubtitles': False,
                'writeautomaticsub': False,
            },
            {
                'format': 'best[height<=720]/best',
                'writesubtitles': False,
                'writeautomaticsub': False,
            },
            {
                'format': 'worst/best',
                'writesubtitles': False,
                'writeautomaticsub': False,
            }
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                ydl_opts = {
                    'outtmpl': os.path.join(path, '%(uploader)s - %(title)s.%(ext)s'),
                    'ignoreerrors': True,
                    'no_warnings': True,
                    'extractaudio': False,
                    'http_headers': {
                        'User-Agent': random.choice(self.user_agents),
                    },
                    'sleep_interval': random.uniform(1, 3),
                    'max_sleep_interval': 5,
                    'retries': 3,
                    'fragment_retries': 3,
                    'skip_unavailable_fragments': True,
                    **strategy
                }

                time.sleep(random.uniform(1, 3))

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                    if info is None:
                        continue
                        
                    if 'entries' in info and info['entries']:
                        valid_entries = [entry for entry in info['entries'] if entry]
                        titles = [entry.get('title', 'Unknown') for entry in valid_entries]
                        return {
                            'status': 'success',
                            'message': f'Downloaded {len(valid_entries)} videos from playlist',
                            'titles': titles[:5],
                            'type': 'playlist'
                        }
                    else:
                        return {
                            'status': 'success',
                            'message': 'YouTube content downloaded successfully!',
                            'title': info.get('title', 'Unknown'),
                            'uploader': info.get('uploader', 'Unknown'),
                            'type': 'video'
                        }
                        
            except Exception as e:
                logger.warning(f"YouTube strategy {i + 1} failed: {str(e)}")
                continue
        
        return {'status': 'error', 'message': 'YouTube download failed. Service may be temporarily blocked.'}

    def download_generic_content(self, url, path):
        """Enhanced generic downloader"""
        try:
            ydl_opts = {
                'outtmpl': os.path.join(path, '%(extractor)s_%(title)s.%(ext)s'),
                'format': 'best[height<=720]/best',
                'no_warnings': True,
                'ignoreerrors': True,
                'http_headers': {
                    'User-Agent': random.choice(self.user_agents),
                },
                'sleep_interval': random.uniform(1, 3),
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
            return {'status': 'error', 'message': 'Download failed: Platform may be temporarily unavailable'}

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
            username = match.group(1)
            # Filter out paths
            if username not in ['p', 'reel', 'tv', 'stories']:
                return username
        return None

    def download_content(self, url, custom_path=None):
        """Enhanced main download function"""
        path = custom_path or DOWNLOAD_DIR
        platform = self.detect_platform(url)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        download_folder = os.path.join(path, f"{platform}_{timestamp}_{safe_url_hash}")
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
            return {'status': 'error', 'message': f'Service temporarily unavailable'}

# Initialize downloader
downloader = AdvancedUniversalDownloader()

def clear_all_downloads():
    """Clear all downloaded files and folders"""
    try:
        if os.path.exists(DOWNLOAD_DIR):
            shutil.rmtree(DOWNLOAD_DIR)
            os.makedirs(DOWNLOAD_DIR)
        logger.info("Downloads directory cleared")
        return True
    except Exception as e:
        logger.error(f"Error clearing downloads: {str(e)}")
        return False

@app.before_request
def check_session():
    """Enhanced session management"""
    if request.endpoint == 'index':
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            session['is_new_session'] = True
            session['created_at'] = datetime.now().isoformat()
        else:
            if not session.get('is_new_session', False):
                created_at = datetime.fromisoformat(session.get('created_at', datetime.now().isoformat()))
                if datetime.now() - created_at > timedelta(hours=1):
                    clear_all_downloads()
                    session['created_at'] = datetime.now().isoformat()
            session['is_new_session'] = False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
@rate_limit(max_requests=5, window=60)
def download():
    """Enhanced download endpoint"""
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
        result['timestamp'] = datetime.now().isoformat()

        return jsonify(result)

    except Exception as e:
        logger.error(f"Download endpoint error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Server error: Please try again later'})

@app.route('/bulk-download', methods=['POST'])
@rate_limit(max_requests=2, window=300)
def bulk_download():
    """Enhanced bulk download"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'status': 'error', 'message': 'URLs list is required'})

        if len(urls) > 10:
            return jsonify({'status': 'error', 'message': 'Maximum 10 URLs allowed per bulk download'})

        results = []
        for i, url in enumerate(urls):
            if url.strip():
                logger.info(f"Bulk downloading {i+1}/{len(urls)}: {url}")
                result = downloader.download_content(url.strip())
                result['url'] = url
                result['platform'] = downloader.detect_platform(url)
                results.append(result)
                
                if i < len(urls) - 1:
                    time.sleep(random.uniform(5, 10))

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

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.1.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
