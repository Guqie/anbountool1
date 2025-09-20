# Heroku 部署指导

## 第一步：完成Heroku登录认证

由于自动登录遇到问题，请手动完成以下步骤：

1. 打开浏览器访问：https://signup.heroku.com/ 
2. 注册或登录您的Heroku账户
3. 在终端中运行以下命令：

```powershell
# 方法1：浏览器登录（推荐）
heroku login

# 方法2：如果浏览器登录失败，使用交互式登录
heroku login -i
```

## 第二步：创建Heroku应用

```powershell
# 创建新应用（应用名称必须全局唯一）
heroku create your-csv-word-converter

# 或者让Heroku自动生成应用名称
heroku create
```

## 第三步：验证部署配置

确保以下文件存在且配置正确：

- `Procfile`: 已存在
- `runtime.txt`: 已存在  
- `requirements.txt`: 已更新

## 第四步：部署到Heroku

```powershell
# 添加Heroku远程仓库（如果尚未添加）
heroku git:remote -a your-app-name

# 推送代码到Heroku
git push heroku main

# 打开应用
heroku open
```

## 故障排除

如果遇到问题，可以查看日志：
```powershell
heroku logs --tail
```