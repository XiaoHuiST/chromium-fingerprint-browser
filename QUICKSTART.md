# 🚀 快速开始指南

> 3步开始使用Chromium指纹浏览器

---

## 第1步: 上传到GitHub (5分钟)

```bash
# 在此目录下执行
cd "F:\dsh work\指纹浏览器制作内核\github-repo"

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Chromium Fingerprint Browser - Initial Commit"

# 关联远程仓库(替换为您的仓库地址)
git remote add origin https://github.com/your-username/chromium-fingerprint-browser.git

# 推送
git push -u origin main
```

---

## 第2步: 触发GitHub Actions编译 (22小时)

### 在GitHub网站操作:

1. 访问: `https://github.com/your-username/chromium-fingerprint-browser/actions`

2. **运行Stage 1** (5小时)
   - 点击 "Stage 1 - Download Chromium Source"
   - 点击 "Run workflow" → "Run workflow"
   - 等待完成

3. **运行Stage 2** (6小时)
   - 点击 "Stage 2 - Compile Base Modules"
   - 点击 "Run workflow" → "Run workflow"
   - 等待完成

4. **运行Stage 3** (6小时)
   - 点击 "Stage 3 - Compile Blink and V8"
   - 点击 "Run workflow" → "Run workflow"
   - 等待完成

5. **运行Stage 4** (5小时)
   - 点击 "Stage 4 - Link Chrome"
   - 点击 "Run workflow" → "Run workflow"
   - 等待完成

6. **下载编译产物**
   - 在Stage 4的运行页面
   - 下载 Artifacts: `chrome-fingerprint-browser.zip` (~500MB)

**总耗时**: 约22小时

---

## 第3步: 本地使用 (立即可用)

### 解压编译产物

```bash
# 解压下载的文件
unzip chrome-fingerprint-browser.zip

# 目录结构:
chrome-fingerprint-browser/
├── chrome.exe
├── chrome.dll
├── locales/
└── resources/
```

### 安装Python依赖(如果还没安装)

```bash
pip install psutil
```

### 创建第一个配置

```bash
python launcher.py --chrome=./chrome-fingerprint-browser/chrome.exe --profile=test001 --create
```

**输出示例**:
```
✅ 配置文件已创建: profiles/test001/fingerprint-config.json
   CPU: AMD Ryzen 7 5800X 8-Core Processor
   GPU: NVIDIA GeForce RTX 4070
   内存: 32GB
   分辨率: 2560x1440
```

### 启动浏览器

```bash
python launcher.py --chrome=./chrome-fingerprint-browser/chrome.exe --profile=test001
```

**输出示例**:
```
🚀 启动浏览器...
   配置: profiles/test001/fingerprint-config.json
   用户数据: profiles/test001
✅ 浏览器已启动 (PID: 12345)
```

### 使用代理

```bash
python launcher.py --chrome=./chrome-fingerprint-browser/chrome.exe --profile=test001 --proxy=http://127.0.0.1:7890
```

---

## 📋 常用命令

### 列出所有配置

```bash
python launcher.py --chrome=./chrome-fingerprint-browser/chrome.exe --list
```

### 创建多个配置

```bash
# 批量创建
for i in {1..10}; do
  python launcher.py --chrome=./chrome.exe --profile=account_$(printf "%03d" $i) --create
done
```

### 运行验收测试

```bash
python tests/acceptance_test.py --chrome=./chrome-fingerprint-browser/chrome.exe
```

---

## 🧪 测试指纹

启动浏览器后,访问以下网站验证:

1. **BrowserLeaks** - https://browserleaks.com
   - 检查WebGL/Canvas/Audio指纹
   - 确认无webdriver标记

2. **Whoer.net** - https://whoer.net
   - 综合评分应达到95+
   - 检查时区和代理

3. **CreepJS** - https://abrahamjuliot.github.io/creepjs/
   - 信任度应为High
   - 无异常标记

4. **PixelScan** - https://pixelscan.net
   - 综合评分95+
   - 无automation特征

---

## 📖 更多文档

- [README.md](README.md) - 项目总览
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - 完整部署文档
- [DELIVERY.md](DELIVERY.md) - 交付说明
- [FINAL_REPORT.md](FINAL_REPORT.md) - 最终报告

---

## ❓ 遇到问题?

### Q: GitHub Actions失败了?

**A**: 查看失败的日志,常见原因:
- 网络超时: 重新运行workflow
- 缓存问题: 清除缓存后重新运行
- 空间不足: 检查GitHub Actions配额

### Q: chrome.exe无法启动?

**A**: 检查:
- 是否解压完整
- 是否在Windows系统
- 是否有杀毒软件拦截

### Q: 指纹没有生效?

**A**: 确认:
- 使用了 `--fingerprint-config` 参数
- 配置文件路径正确
- 配置文件格式正确(JSON)

---

## 🎉 开始使用!

现在您已经准备好了!

1. ✅ 上传到GitHub
2. ⏳ 等待22小时编译
3. ✅ 下载chrome.exe
4. ✅ 开始使用!

**祝您使用愉快!** 🚀
