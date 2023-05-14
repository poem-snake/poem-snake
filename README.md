[![Website](https://img.shields.io/website?url=https%3A%2F%2Fpoem.rotriw.com%2F)](https://poem.rotriw.com/)
![GitHub](https://img.shields.io/github/license/poem-snake/poem-snake)
![](https://img.shields.io/badge/QQ%20%E7%BE%A4-637873933-blue)
[![爱发电](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.swo.moe%2Fstats%2Fafdian%2Fsonghongyi&query=count&color=282c34&label=%E7%88%B1%E5%8F%91%E7%94%B5&labelColor=946ce6&suffix=+%E5%8F%91%E7%94%B5%E4%BA%BA%E6%AC%A1+%2F+%E6%9C%88&cacheSeconds=3600)](https://afdian.net/@songhongyi)
[![wakatime](https://wakatime.com/badge/github/poem-snake/poem-snake.svg)](https://wakatime.com/badge/github/poem-snake/poem-snake)

# 🐍 Poem Snake - 古诗（）迷 📜

Poem Snake 是一款开源的古诗小游戏，其中文名称为：”古诗（）迷“。

## 🎮 游戏玩法

游戏玩法类似于飞花令，玩家需要回答出来包括给定字的诗句。但是该字不固定，而是从抽取的诗歌中得到。更多关于游戏玩法的内容请访问 [游玩指南](https://www.luogu.com.cn/paste/iz42nphu)。

## 🌐 官方部署版

官方部署版链接为：<https://poem.rotriw.com/>，有数百名玩家。欢迎大家来挑战自己的古诗词水平！

## 🚀 技术栈

- [Flask](https://github.com/pallets/flask)：Python Web 框架，提供后端支持。
- [Fomantic UI](https://github.com/fomantic/Fomantic-UI)：美观的 UI 库，提供前端界面设计。
- [socket.io](https://github.com/socketio/socket.io)：实现实时通信。

##  💻安装

1. 克隆仓库到本地：

   ```
   git clone https://github.com/poem-snake/poem-snake.git
   ```

2. 进入项目目录并安装依赖：

   ```
   cd poem-snake
   pip install -r requirements.txt
   ```

3. 运行项目：

   ```
   python app.py
   ```

4. 在浏览器中访问 http://localhost:5000/ 即可开始游戏。

## 💻 部署

Poem Snake 已经部署于官方服务器上，您也可以自行部署。

1. 将代码上传至服务器。

2. 安装依赖：

   ```
   pip install -r requirements.txt
   ```

3. 安装 Nginx 和 Gunicorn。

4. 配置 Nginx，在 /etc/nginx/sites-available 目录下创建一个新文件，文件名为 poem-snake：

   ```
   server {
       listen 80;
       server_name your_domain.com;
   
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

5. 创建一个 Gunicorn 配置文件，比如 gunicorn.conf：

   ```
   workers = 4
   bind = '127.0.0.1:8000'
   ```

6. 启动 Gunicorn：

   ```
   gunicorn app:app -c gunicorn.conf
   ```

7. 启动 Nginx：

   ```
   sudo service nginx start
   ```

现在，您就可以在您的域名上访问 Poem Snake 了！

## 💰 捐款通道

如果您觉得游戏很有趣，可以通过以下捐款通道来支持我们的开发：

<img height="300" src="https://github.com/poem-snake/poem-snake/raw/main/1646552417.jpg"/>

- [爱发电](https://afdian.net/a/songhongyi)

## 📝 许可证

项目使用 MIT License 进行开源，详情请查看 [LICENSE](./LICENSE) 文件

## 👥 贡献者

- [William Song](https://github.com/william-song-shy)

## 🐍 持续开发

游戏仍在持续开发迭代，欢迎大家来一起参与开发，让这个游戏变得更加完善！

