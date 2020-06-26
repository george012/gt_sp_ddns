<font size=20>目录：</font>
<!-- TOC -->

- [依赖环境](#依赖环境)
- [设置开机自启服务 （支持 CentOS7.x以上  及Ubuntu18.04.x以上）](#设置开机自启服务-支持-centos7x以上--及ubuntu1804x以上)

<!-- /TOC -->

#   依赖环境
*   方法1（新手或者 python虚拟环境 建议）
    ```
    pip install aliyun-python-sdk-core-v3
    pip install aliyun-python-sdk-ecs
    pip install aliyun-python-sdk-alidns
    ```

*   通用建议
    ```
    pip install -r requirements.txt
    ```
 
#   设置开机自启服务 （支持 CentOS7.x以上  及Ubuntu18.04.x以上）
*   编辑文件“/usr/lib/systemd/system/gt_sp_ddns.service”
    ```
    vim /usr/lib/systemd/system/gt_sp_ddns.service
    ```
*   注意自行设置日志及服务目录
*   命令样板
    ```
    [Unit]
    Description=GeenTi DDNS Script
    #描述服务
    After=syslog.target
    After=network.target
    
    [Service]
    Type=forking
    #代表后台运行
    Restart=on-failure
    PIDFile=/home/sp_home/gt_sp_ddns/gt_sp_ddns.pid
    ExecStart=/home/py_v_env/gt_sp_ddns/bin/python3 /home/sp_home/gt_sp_ddns/gt_sp_ddns.py
    ExecStop=ps -ef | grep gt_sp_ddns | awk '{print $2}' | xargs kill -9
    PrivateTmp=true
    
    [Install]
    WantedBy=multi-user.target

    ```
    
*   给权限
    ```
    chmod 754 /usr/lib/systemd/system/gt_sp_ddns.service
    ```
    
*   设置开机自启
    ```
    systemctl enable gt_sp_ddns
    ```
