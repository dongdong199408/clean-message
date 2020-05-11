FROM python:3.6-slim

MAINTAINER 976344083@qq.com
LABEL author="miaoxudong"
#用ubuntu国内源替换默认源
RUN rm /etc/apt/sources.list
COPY sources.list /etc/apt/sources.list
WORKDIR /app
ADD . /app
# 安装依赖
#RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
# 声明镜像内服务监听的端口
EXPOSE 5100
CMD ["python3"]
#CMD ["gunicorn", "app:app", "-c", "./gunicor.con.py"]