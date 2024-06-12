#!/bin/bash

# 激活虚拟环境
source venv/bin/activate

# 获取当前目录的全路径
BASE_DIR=$(pwd)

# 1. 执行git pull 下载最新代码
echo "Pulling the latest code..."
git pull origin main

# 2. 检查8090和7860端口，如果有程序运行，关闭它们
echo "Checking and killing processes on ports 8090 and 7860..."
for port in 8090 7860; do
  pid=$(lsof -t -i:$port)
  if [ -n "$pid" ]; then
    echo "Killing process $pid on port $port..."
    kill -9 $pid
  else
    echo "No process found on port $port."
  fi
done

# 3. 后台执行python file_server.py ，日志输出到 fileserver.log
echo "Starting file_server.py in the background..."
nohup python "$BASE_DIR/file_server.py" > fileserver.log 2>&1 &

# 4. 后台执行streamlit run Main.py，日志输出到main.log
echo "Starting Main.py with Streamlit in the background..."
nohup streamlit run "$BASE_DIR/Main.py" > main.log 2>&1 &

echo "Script execution completed."
