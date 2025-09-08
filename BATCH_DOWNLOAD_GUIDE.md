# 批量下载功能使用指南

## 功能概述

批量下载功能允许用户一次性下载多个Bilibili视频的音频文件，大大提高了下载效率。支持多种URL格式，自动验证和提取，并提供实时进度监控。

## 主要特性

### 1. 多格式URL支持
- **完整URL**: `https://www.bilibili.com/video/BV1xxx`
- **短链接**: `https://b23.tv/xxx`
- **BV号**: `BV1xxx`
- **分享文本**: 自动从分享内容中提取URL

### 2. 智能验证
- 自动验证URL有效性
- 支持从分享文本中提取链接
- 显示验证结果和错误信息

### 3. 任务管理
- 创建、启动、取消、删除批量下载任务
- 实时进度监控
- 任务状态跟踪（等待中、下载中、已完成、失败、已取消）

### 4. 统计信息
- 总任务数、完成数、失败数
- 成功率统计
- 历史记录查看

## 使用步骤

### 1. 访问批量下载页面
- 点击导航栏中的"批量下载"链接
- 或直接访问 `/batch` 页面

### 2. 创建批量下载任务
1. **输入任务名称**: 为批量下载任务起一个有意义的名称
2. **选择自动编辑标签**: 是否自动编辑音频标签
3. **输入URL列表**: 在文本框中输入要下载的URL，每行一个
4. **验证URL** (可选): 点击"验证URL"按钮检查URL有效性
5. **创建任务**: 点击"创建批量下载"按钮

### 3. 管理下载任务
- **启动任务**: 点击播放按钮开始下载
- **取消任务**: 点击停止按钮取消正在进行的下载
- **查看详情**: 点击眼睛按钮查看任务详情
- **删除任务**: 点击垃圾桶按钮删除任务

### 4. 监控进度
- 实时查看下载进度
- 查看每个子任务的状态
- 查看成功和失败的任务数量

## URL格式示例

### 支持的URL格式
```
https://www.bilibili.com/video/BV1xx411c7mD
https://b23.tv/BV1xx411c7mD
BV1xx411c7mD
【视频标题】https://www.bilibili.com/video/BV1xx411c7mD
[视频标题] https://b23.tv/BV1xx411c7mD
```

### 批量输入示例
```
https://www.bilibili.com/video/BV1xx411c7mD
https://b23.tv/BV1xx411c7mD
BV1xx411c7mD
【音乐合集】https://www.bilibili.com/video/BV1xx411c7mD
[UP主分享] https://b23.tv/BV1xx411c7mD
```

## 技术特性

### 1. 异步处理
- 使用多线程处理批量下载
- 不阻塞用户界面
- 支持并发下载

### 2. 错误处理
- 单个任务失败不影响其他任务
- 详细的错误信息记录
- 自动重试机制

### 3. 数据持久化
- 任务状态自动保存
- 支持应用重启后恢复
- 自动清理过期任务

### 4. 资源管理
- 自动管理临时文件
- 内存使用优化
- 磁盘空间监控

## API接口

### 创建批量下载任务
```http
POST /api/batch/create
Content-Type: application/json

{
    "name": "我的音乐收藏",
    "urls": "https://www.bilibili.com/video/BV1xxx\nhttps://b23.tv/xxx",
    "auto_edit_tags": true,
    "default_tags": {}
}
```

### 获取任务列表
```http
GET /api/batch/list
```

### 启动任务
```http
POST /api/batch/{batch_id}/start
```

### 取消任务
```http
POST /api/batch/{batch_id}/cancel
```

### 获取任务进度
```http
GET /api/batch/{batch_id}/progress
```

### 验证URL
```http
POST /api/batch/validate-urls
Content-Type: application/json

{
    "urls": "https://www.bilibili.com/video/BV1xxx\nhttps://b23.tv/xxx"
}
```

## 配置选项

### 环境变量
```bash
# 批量下载配置
BATCH_MAX_TASKS=50          # 最大任务数量
BATCH_CLEANUP_DAYS=7        # 自动清理天数
BATCH_STORAGE_PATH=batch_storage  # 存储路径
```

### 限制说明
- 单个批量下载任务最多支持50个URL
- 自动清理7天前的任务记录
- 支持同时运行多个批量下载任务

## 故障排除

### 常见问题

1. **URL验证失败**
   - 检查URL格式是否正确
   - 确保URL来自Bilibili
   - 尝试使用完整的URL格式

2. **下载失败**
   - 检查网络连接
   - 确认FFmpeg已正确安装
   - 查看错误日志获取详细信息

3. **任务卡住**
   - 尝试取消并重新创建任务
   - 检查服务器资源使用情况
   - 重启应用服务

### 日志查看
```bash
# 查看应用日志
tail -f app.log

# 查看批量下载相关日志
grep "batch" app.log
```

## 性能优化建议

### 1. 服务器配置
- 确保有足够的内存和磁盘空间
- 配置合适的并发下载数量
- 定期清理临时文件

### 2. 网络优化
- 使用稳定的网络连接
- 考虑使用代理服务器
- 避免在网络高峰期进行大量下载

### 3. 存储管理
- 定期清理下载目录
- 监控磁盘空间使用
- 考虑使用SSD提高I/O性能

## 安全注意事项

1. **URL验证**: 只处理Bilibili相关的URL
2. **文件安全**: 限制文件类型和大小
3. **访问控制**: 需要登录才能使用批量下载功能
4. **资源限制**: 防止恶意大量下载请求

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的批量下载功能
- 提供Web界面和API接口
- 支持多种URL格式
- 实时进度监控

## 技术支持

如果遇到问题或需要帮助，请：
1. 查看本文档的故障排除部分
2. 检查应用日志文件
3. 联系技术支持团队
