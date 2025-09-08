"""
Bilibili音频下载器 - 重构后的主应用文件
"""
import os
import time
from io import BytesIO
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, session, flash
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from dotenv import load_dotenv

# 导入自定义模块
from utils.logger import Logger
from utils.exceptions import ValidationError, DownloadError, TagEditError, AuthenticationError
from controllers.download_controller import DownloadController
from controllers.tag_controller import TagController
from controllers.auth_controller import AuthController
from services.auth_service import AuthService
from config import LOGIN_REQUIRED, DOWNLOAD_PATH, TEMP_PATH

# 加载环境变量
load_dotenv()

# 初始化Flask应用
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
app.config.from_pyfile('config.py')

# 初始化日志
logger = Logger(app)

# 初始化控制器
download_controller = DownloadController()
tag_controller = TagController()
auth_controller = AuthController()
auth_service = AuthService()

# 错误处理装饰器
def handle_errors(f):
    """错误处理装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.log_warning(f"验证错误: {str(e)}")
            return render_template('error.html', 
                                 message="输入验证失败",
                                 details=str(e)), 400
        except DownloadError as e:
            logger.log_error(f"下载错误: {str(e)}")
            return render_template('error.html', 
                                 message="下载失败",
                                 details=str(e)), 500
        except TagEditError as e:
            logger.log_error(f"标签编辑错误: {str(e)}")
            return render_template('error.html', 
                                 message="标签编辑失败",
                                 details=str(e)), 500
        except AuthenticationError as e:
            logger.log_warning(f"认证错误: {str(e)}")
            return render_template('error.html', 
                                 message="认证失败",
                                 details=str(e)), 401
        except Exception as e:
            logger.log_error(f"未处理的错误: {str(e)}")
            return render_template('error.html', 
                                 message="服务器内部错误",
                                 details="请查看日志获取更多信息"), 500
    return decorated_function

# 错误处理器
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

# 路由定义
@app.route('/')
@auth_service.login_required_decorator
def index():
    """主页"""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
@auth_service.login_required_decorator
@handle_errors
def download():
    """下载Bilibili音频"""
    result = download_controller.handle_download_request()
    
    if result['success']:
        return redirect(result['redirect_url'])
    else:
        return render_template('error.html', 
                             message=result['message'],
                             details="请检查输入后重试"), result.get('status_code', 500)

@app.route('/edit/<filename>')
@auth_service.login_required_decorator
@handle_errors
def edit_tags(filename):
    """音频标签编辑页面"""
    result = tag_controller.get_edit_page_data(filename)
    
    if result['success']:
        data = result['data']
        return render_template('edit.html', 
                             filename=data['filename'],
                             tags=data['tags'],
                             has_cover=data['has_cover'])
    else:
        return render_template('error.html', 
                             message=result['message'],
                             details="请检查文件名后重试"), result.get('status_code', 500)

@app.route('/save_tags', methods=['POST'])
@auth_service.login_required_decorator
@handle_errors
def save_tags():
    """保存音频标签"""
    result = tag_controller.save_tags()
    
    if result['success']:
        return jsonify({
            "success": True,
            "message": result['message']
        })
    else:
        return jsonify({
            "success": False,
            "message": result['message']
        }), result.get('status_code', 500)

@app.route('/cover')
@auth_service.login_required_decorator
def get_cover():
    """获取封面图片"""
    result = tag_controller.get_cover_image()
    
    if result['success']:
        if result['type'] == 'file':
            timestamp = result.get('timestamp', int(time.time()))
            return send_file(result['path'], mimetype='image/jpeg', last_modified=timestamp)
        elif result['type'] == 'embedded':
            timestamp = result.get('timestamp', int(time.time()))
            return send_file(BytesIO(result['data']), mimetype='image/jpeg', last_modified=timestamp)
    
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
    result = download_controller.check_ffmpeg_status()
    return jsonify(result)

@app.route('/install_ffmpeg')
def install_ffmpeg():
    """FFmpeg安装指南页面"""
    return render_template('install_ffmpeg.html')

@app.route('/upload_cookies', methods=['POST'])
@auth_service.login_required_decorator
@handle_errors
def upload_cookies():
    """上传cookies文件"""
    from utils.validators import FileValidator
    import os
    
    cookies_file = request.files.get('cookies')
    if not cookies_file or not cookies_file.filename:
        return jsonify({"success": False, "message": "未提供cookies文件"}), 400
    
    # 验证文件类型
    file_validator = FileValidator()
    if not file_validator.is_valid_cookies_file(cookies_file.filename):
        return jsonify({"success": False, "message": "只支持.txt格式的cookies文件"}), 400
    
    # 验证文件大小（限制为1MB）
    if hasattr(cookies_file, 'content_length') and cookies_file.content_length > 1024 * 1024:
        return jsonify({"success": False, "message": "cookies文件过大，请选择小于1MB的文件"}), 400
    
    # 确保临时目录存在
    os.makedirs(TEMP_PATH, exist_ok=True)
    
    cookies_path = os.path.join(TEMP_PATH, 'cookies.txt')
    cookies_file.save(cookies_path)
    
    # 验证文件内容（简单检查）
    try:
        with open(cookies_path, 'r', encoding='utf-8') as f:
            content = f.read(100)  # 只读取前100个字符
            if not content.strip():
                os.remove(cookies_path)
                return jsonify({"success": False, "message": "cookies文件为空"}), 400
    except Exception:
        os.remove(cookies_path)
        return jsonify({"success": False, "message": "cookies文件格式错误"}), 400
    
    return jsonify({"success": True, "message": "Cookies文件上传成功"})

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        result = auth_controller.handle_login_request()
        
        if result['success']:
            return redirect(result['redirect_url'])
        else:
            flash(result['message'])
            return redirect(result['redirect_url'])
    
    # GET请求
    result = auth_controller.get_login_page_data()
    
    if result['success'] and 'redirect_url' in result:
        return redirect(result['redirect_url'])
    
    return render_template('login.html')

@app.route('/logout')
@auth_service.login_required_decorator
def logout():
    """登出"""
    result = auth_controller.handle_logout_request()
    
    if result['success']:
        return redirect(result['redirect_url'])
    else:
        flash(result['message'])
        return redirect(url_for('index'))

if __name__ == '__main__':
    debug = os.environ.get('DEBUG', 'False') == 'True'
    app.run(host='0.0.0.0', port=5000, debug=debug)
