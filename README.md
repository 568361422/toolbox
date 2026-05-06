# 开发者工具箱 (Developer Toolbox)

一个功能全面的开发者辅助工具，支持离线运行。

## 功能特性

### 文本工具
- JSON 格式化/压缩/校验/转义
- XML 格式化/压缩
- 字符串编解码（URL、Base64、Unicode、Hex、ASCII）
- 大小写转换、驼峰/下划线互转
- 正则表达式测试
- 随机字符串生成（密码、UUID、邀请码）

### 时间日期
- 时间戳 ↔ 北京时间 互转
- 时间差计算
- Unix 时间戳

### 加解密 & 哈希
- MD5、SHA1/SHA256/SHA512 哈希
- AES 加解密
- RSA 密钥生成与加解密
- 二维码生成
- JWT 解析

### 网络工具
- 本机IP/公网IP查询
- Ping 测试
- 端口检测
- DNS 查询
- HTTP 请求调试

### 编码转换
- 2/8/10/16 进制互转
- RGB ↔ HEX 颜色转换
- 字节单位换算
- HTML 转义

### 前端工具
- CSS 格式化/压缩
- JS 格式化/压缩
- User-Agent 解析

### 后端工具
- SQL 格式化/压缩
- 随机数据生成（姓名、手机号、身份证、地址）
- Java 实体类生成

### 运维工具
- 文件哈希校验（MD5/SHA256）
- 端口占用查询
- Linux 常用命令速查

### 效率工具
- 常用代码片段仓库
- 防抖/节流代码模板

### 额外功能
- 深色/浅色主题切换
- 历史记录保存
- 我的收藏
- 离线运行（无需联网）

## 安装

```bash
# 安装依赖（可选，主要功能无需依赖）
pip install -r requirements.txt
```

## 运行

```bash
python dev_toolbox.py
```

## 依赖

- Python 3.x（内置 tkinter，无需额外安装）
- 可选：pycryptodome（增强加密功能）
- 可选：qrcode（二维码生成）

## 文件结构

```
dev_toolbox/
├── dev_toolbox.py    # 主程序
├── requirements.txt   # 依赖
└── README.md         # 说明文档
```