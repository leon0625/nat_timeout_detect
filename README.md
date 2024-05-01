# 使用方法  
server端  
```
python3 server.py -p 12345
```

client端  
检测UDP：
```
python3 client.py -s your_server_ip -p 12345 --min_timeout=10 --max_timeout=300 --udp
```

检测TCP:  
```
python3 client.py -s your_server_ip -p 12345 --min_timeout=60 --max_timeout=1800
```

家里的电信网络：  
tcp超时：241s  
udp超时：29s  