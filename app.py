import subprocess
import time
from venv import logger
from flask import Flask, flash, render_template, request, jsonify, redirect, url_for, send_file, session
from utils.downloader import check_ffmpeg_installed, download_bilibili_audio
from utils.navidrome import trigger_navidrome_scan
from utils.tag_editor import get_audio_tags, update_audio_tags
from config import ALLOWED_DOMAINS, DOWNLOAD_PATH, TEMP_PATH
import os
import re
import logging
import traceback
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from io import BytesIO
from pathlib import Path
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from config import LOGIN_REQUIRED, ADMIN_USERNAME, ADMIN_PASSWORD, SESSION_TIMEOUT
from dotenv import load_dotenv
load_dotenv()  # 加载.env文件

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 确保有安全的密钥
app.config['PERMANENT_SESSION_LIFETIME'] = SESSION_TIMEOUT
app.config.from_pyfile('config.py')
app.secret_key = os.urandom(24)  # 添加密钥用于session

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if LOGIN_REQUIRED and not session.get('logged_in'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# 配置日志
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

def is_valid_bilibili_url(url):
    """验证B站URL"""
    pattern = r'^https?://(www\.)?(bilibili\.com|b23\.tv)/'
    return re.match(pattern, url) is not None

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', 
                           message="页面未找到",
                           details="您访问的页面不存在"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', 
                           message="服务器内部错误",
                           details="请查看日志获取更多信息"), 500

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
@login_required
def download():
    try:
        url = request.form['url']
        
        if not is_valid_bilibili_url(url):
            return render_template('error.html', 
                                  message="无效的Bilibili URL",
                                  details="请确保URL来自bilibili.com或b23.tv"), 400
        # 提前检查FFmpeg安装
        if not check_ffmpeg_installed():
            return render_template('error.html', 
                                  message="FFmpeg未安装",
                                  details="请安装FFmpeg并添加到系统PATH"), 500
        
        result = download_bilibili_audio(url)
        
        if result['status'] == 'error':
            return render_template('error.html', 
                                  message=result['message'],
                                  details="请检查URL是否正确或稍后再试"), 500
        
        # 保存当前文件名到session
        session['current_filename'] = result['filename']
        
        # 重定向到编辑页面
        return redirect(url_for('edit_tags', filename=result['filename']))
            
    except Exception as e:
        logger.error(f"下载过程中出错: {str(e)}")
        return render_template('error.html', 
                              message="下载过程中发生错误",
                              details=str(e)), 500

@app.route('/edit/<filename>')
def edit_tags(filename):
    """音频标签编辑页面"""
    try:
        filepath = os.path.join(DOWNLOAD_PATH, filename)
        
        if not os.path.exists(filepath):
            return render_template('error.html', 
                                  message="文件不存在",
                                  details=f"找不到文件: {filename}"), 404
        
        # 获取标签信息
        tags = get_audio_tags(filepath)
        
        # 检查封面是否存在
        base_name = os.path.splitext(filename)[0]
        cover_path = os.path.join(DOWNLOAD_PATH, f"{base_name}.jpg")
        has_cover = os.path.exists(cover_path)
        
        # 如果没有外部封面，检查音频文件内嵌封面
        if not has_cover:
            try:
                audio = MP3(filepath, ID3=ID3)
                if 'APIC:' in audio:
                    has_cover = True
            except:
                pass
        
        # 保存当前文件名到session
        session['current_filename'] = filename
        
        return render_template('edit.html', 
                              filename=filename,
                              tags=tags,
                              has_cover=has_cover)
    except Exception as e:
        app.logger.error(f"编辑标签页面出错: {str(e)}\n{traceback.format_exc()}")
        return render_template('error.html', 
                              message="加载编辑页面时出错",
                              details=str(e)), 500

@app.route('/save_tags', methods=['POST'])
def save_tags():
    try:
        filename = request.form['filename']
        filepath = os.path.join(DOWNLOAD_PATH, filename)
        
        if not os.path.exists(filepath):
            return jsonify({"success": False, "message": "文件不存在"}), 404
        
        # 获取表单数据
        tags = {
            'title': request.form.get('title', ''),
            'artist': request.form.get('artist', ''),
            'album': request.form.get('album', ''),
            'albumartist': request.form.get('albumartist', ''),
            'date': request.form.get('date', ''),
            'tracknumber': request.form.get('tracknumber', ''),
            'genre': request.form.get('genre', '')
        }
        
        # 处理封面图片
        cover_file = request.files.get('cover')
        cover_path = None
        
        if cover_file and cover_file.filename != '':
            # 保存到临时目录
            cover_path = os.path.join(TEMP_PATH, "new_cover.jpg")
            cover_file.save(cover_path)
        
        # 更新标签
        success = update_audio_tags(filepath, tags, cover_path)
        
        if not success:
            return jsonify({"success": False, "message": "标签更新失败"}), 500
        
        # 触发Navidrome扫描
        scan_success = trigger_navidrome_scan()
        scan_message = "，曲库更新成功" if scan_success else "，但曲库更新失败"
        
        return jsonify({
            "success": True,
            "message": f"标签更新成功{scan_message}"
        })
        
    except Exception as e:
        logger.error(f"保存标签过程中出错: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/cover')
def get_cover():
    """获取封面图片"""
    try:
        # 从session获取当前文件名
        filename = session.get('current_filename')
        if not filename:
            return get_empty_image()
        
        # 尝试从音频文件同目录获取封面
        base_name = os.path.splitext(filename)[0]
        cover_path = os.path.join(DOWNLOAD_PATH, f"{base_name}.jpg")
        
        if os.path.exists(cover_path):
            # 添加时间戳参数防止浏览器缓存
            timestamp = int(time.time())
            return send_file(cover_path, mimetype='image/jpeg', last_modified=timestamp)
        
        # 尝试从音频文件内嵌封面获取
        audio_path = os.path.join(DOWNLOAD_PATH, filename)
        audio = MP3(audio_path, ID3=ID3)
        
        if 'APIC:' in audio:
            cover_data = audio['APIC:'].data
            # 添加时间戳参数防止浏览器缓存
            timestamp = int(time.time())
            return send_file(BytesIO(cover_data), mimetype='image/jpeg', last_modified=timestamp)
        
        # 返回默认封面
        return send_file('static/default_cover.jpg', mimetype='image/jpeg')
    except Exception as e:
        logger.error(f"获取封面失败: {str(e)}")
        return get_empty_image()

def get_empty_image():
    """返回一个透明的1x1像素图片作为占位符"""
    empty_image = BytesIO()
    empty_image.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82')
    empty_image.seek(0)
    response = app.make_response(empty_image.getvalue())
    response.headers.set('Content-Type', 'image/png')
    return response

@app.route('/check_ffmpeg')
def check_ffmpeg():
    """检查FFmpeg安装状态"""
    try:
        # 使用更可靠的方式检查FFmpeg
        result = subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5  # 添加超时防止卡死
        )
        installed = 'ffmpeg version' in result.stdout or 'ffmpeg version' in result.stderr
        return jsonify({"installed": installed})
    except Exception as e:
        return jsonify({"installed": False, "error": str(e)})

@app.route('/install_ffmpeg')
def install_ffmpeg():
    """FFmpeg安装指南页面"""
    return render_template('install_ffmpeg.html')

@app.route('/upload_cookies', methods=['POST'])
def upload_cookies():
    """上传cookies文件"""
    try:
        cookies_file = request.files.get('cookies')
        if cookies_file and cookies_file.filename != '':
            cookies_path = os.path.join(TEMP_PATH, 'cookies.txt')
            cookies_file.save(cookies_path)
            return jsonify({"success": True, "message": "Cookies文件上传成功"})
        else:
            return jsonify({"success": False, "message": "未提供cookies文件"}), 400
    except Exception as e:
        logger.error(f"上传cookies失败: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

# 添加登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if not LOGIN_REQUIRED:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            session.permanent = True
            app.permanent_session_lifetime = SESSION_TIMEOUT
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('用户名或密码错误')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# 添加登出路由
@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    debug = os.environ.get('DEBUG', 'False') == 'True'
    app.run(host='0.0.0.0', port=5000, debug=debug)