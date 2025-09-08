#!/usr/bin/env python3
"""
打包测试脚本 - 验证各种打包方式
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def test_python_imports():
    """测试Python模块导入"""
    print("测试Python模块导入...")
    
    modules = [
        'flask',
        'mutagen',
        'yt_dlp',
        'dotenv',
        'werkzeug',
        'jinja2'
    ]
    
    failed_modules = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_modules.append(module)
    
    if failed_modules:
        print(f"\n缺少模块: {', '.join(failed_modules)}")
        print("请运行: pip install " + " ".join(failed_modules))
        return False
    
    return True

def test_project_structure():
    """测试项目结构"""
    print("测试项目结构...")
    
    required_files = [
        'app.py',
        'config.py',
        'requirements.txt',
        'templates/index.html',
        'templates/layout.html',
        'templates/batch_download.html',
        'models/__init__.py',
        'services/__init__.py',
        'controllers/__init__.py',
        'utils/__init__.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n缺少文件: {', '.join(missing_files)}")
        return False
    
    return True

def test_config_loading():
    """测试配置加载"""
    print("测试配置加载...")
    
    try:
        import config
        print("✅ config.py 加载成功")
        
        # 检查关键配置
        required_configs = [
            'DOWNLOAD_PATH',
            'TEMP_PATH',
            'LOGIN_REQUIRED',
            'ADMIN_USERNAME',
            'ADMIN_PASSWORD'
        ]
        
        for config_name in required_configs:
            if hasattr(config, config_name):
                print(f"✅ {config_name}")
            else:
                print(f"❌ {config_name}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_app_initialization():
    """测试应用初始化"""
    print("测试应用初始化...")
    
    try:
        # 设置测试环境
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['DEBUG'] = 'False'
        
        # 导入应用
        from app import app
        
        print("✅ Flask应用创建成功")
        
        # 测试路由
        with app.test_client() as client:
            # 测试主页（需要登录）
            response = client.get('/')
            if response.status_code in [200, 302]:  # 200或重定向到登录页
                print("✅ 主页路由正常")
            else:
                print(f"❌ 主页路由异常: {response.status_code}")
                return False
            
            # 测试登录页
            response = client.get('/login')
            if response.status_code == 200:
                print("✅ 登录页路由正常")
            else:
                print(f"❌ 登录页路由异常: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 应用初始化失败: {e}")
        return False

def test_batch_functionality():
    """测试批量下载功能"""
    print("测试批量下载功能...")
    
    try:
        from models.batch_download import BatchDownload, DownloadTask, BatchStatus
        from services.batch_download_service import BatchDownloadService
        from controllers.batch_controller import BatchController
        
        print("✅ 批量下载模块导入成功")
        
        # 测试数据模型
        batch = BatchDownload(
            id="test-id",
            name="测试批量下载",
            urls=["https://www.bilibili.com/video/BV1xx411c7mD"]
        )
        
        print("✅ 批量下载数据模型创建成功")
        
        # 测试服务
        service = BatchDownloadService()
        print("✅ 批量下载服务创建成功")
        
        # 测试控制器
        controller = BatchController()
        print("✅ 批量下载控制器创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 批量下载功能测试失败: {e}")
        return False

def test_docker_files():
    """测试Docker文件"""
    print("测试Docker文件...")
    
    docker_files = [
        'dockerfile',
        'docker-compose.yml',
        '.dockerignore'
    ]
    
    for file_name in docker_files:
        if os.path.exists(file_name):
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name}")
            return False
    
    return True

def test_build_scripts():
    """测试构建脚本"""
    print("测试构建脚本...")
    
    build_scripts = [
        'build.py',
        'docker-build.py',
        'install.py',
        'app.spec'
    ]
    
    for script_name in build_scripts:
        if os.path.exists(script_name):
            print(f"✅ {script_name}")
        else:
            print(f"❌ {script_name}")
            return False
    
    return True

def test_documentation():
    """测试文档文件"""
    print("测试文档文件...")
    
    doc_files = [
        'DEPLOYMENT_GUIDE.md',
        'BATCH_DOWNLOAD_GUIDE.md',
        'PROJECT_STRUCTURE.md',
        'README.md'
    ]
    
    for doc_name in doc_files:
        if os.path.exists(doc_name):
            print(f"✅ {doc_name}")
        else:
            print(f"❌ {doc_name}")
            return False
    
    return True

def run_quick_build_test():
    """运行快速构建测试"""
    print("运行快速构建测试...")
    
    try:
        # 检查PyInstaller
        result = subprocess.run(['pyinstaller', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PyInstaller已安装")
        else:
            print("❌ PyInstaller未安装")
            return False
        
        # 运行构建测试（不实际构建）
        print("✅ 构建环境检查通过")
        return True
        
    except FileNotFoundError:
        print("❌ PyInstaller未安装")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("Bilibili2Navidrome 打包测试")
    print("=" * 60)
    
    tests = [
        ("Python模块导入", test_python_imports),
        ("项目结构", test_project_structure),
        ("配置加载", test_config_loading),
        ("应用初始化", test_app_initialization),
        ("批量下载功能", test_batch_functionality),
        ("Docker文件", test_docker_files),
        ("构建脚本", test_build_scripts),
        ("文档文件", test_documentation),
        ("构建环境", run_quick_build_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有测试通过！项目可以正常打包部署")
        print("\n可用的打包方式:")
        print("1. 独立可执行文件: python build.py")
        print("2. Docker容器: python docker-build.py")
        print("3. 一键安装: python install.py")
    else:
        print("❌ 部分测试失败，请检查项目配置")
        print("建议先运行: python install.py")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
