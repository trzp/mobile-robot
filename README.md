## mobile-robot使用方法

## 依赖包：
* pykinect, kcftracker_mul_pro, RmCar, yolo_mul_pro, 下载地址https://github.com/trzp

## 使用流程
### 补充电量
* 底盘充电，放大器电池充电（利用准备时间充电）

### 开启设备
* 设备上电，神州电脑开机，路由器通电
* 神州计算机连接，mobilerobot无线网络（密码mobilerobot）,查看其ip是否设置为固定IP:192.168.1.3
* 控制计算机开机，连接mobilerobot，查看ip是否固定为192.168.1.2
* 两级互ping，看手否联通。如失败，检查网路是否连接上，（如果不能ping,检查防火墙是否关闭）

### 检查设备是否正常运行
* 启动控制台：crt+R -> cmd
* cd E:\myPackages\mecanum-kinova\mecanum-kinova
* e:
* python2 demo.py

* 此时应当停止底盘充电,底盘应该上电
* 机械臂初始化，显示摄像头界面
* 使用鼠标框选目标物后，enter
* 在控制台中输入目标名称：如desk,bottle,person,chair，回车
* 小车初始化后应当执行正确动作
* 如果正常则检查完毕，关闭该程序

### 脑电设备检查
* 连接放大器电池
* 桌面—>打开pycorder,电极impedance和default mode查看放大器是否能够正常打开
* 如果不能打开设备，应当检查是否连接放大器至计算机或者电池电量是否充足

### 开始试验
* 佩戴电极帽涂抹导电胶安置电极，注意和被试初始电极位置一致
* 连接电极，启动pycorder,查看impedance,调整impedance
* 开始采集数据，进行闭眼检查

### 离线训练
* 进入e:\mobilerobotV2

* **<font color=#FF0000>启动任务管理器，点击详细信息，找到foxitprotect进程，关闭它</font>**

* 启动start_train.bat启动训练界面
* 进入P300-BCI\batch目录，启动p300训练EEG.bat
* 加载train参数
* 设置被试姓名，规则为name+offline,session根据被试进行的次数来设置（一天为一次）
* 保存参数
* start
* 最大化训练界面开始训练
* 停止后suspend,关闭BCI2000

* 完成后，启动P300-BCI\P3trainSWLDA\P3train.m
* 运行加载数据训练

* 再进行一次训练（可以加上以前session的数据）
* 运行P3train.m
* 视情况再进行训练（每次P3train都将以前的数据都加上）

* 训练完成，关闭训练界面，关闭BCI2000

### 开始控制
* 启动start_rm_server2.bat机械初始化，出现界面
* 启动 <P300在线 EEG.bat>
* 加载online参数
* 设置被试姓名: name + online, session根据被试进行的试验次数来设置（一天为一次新的session）
* start

* 配合operator使用

### 注意事项
* 随时处于轮椅右侧，注意及时排除危险情况，必要时可按下急停按钮
