爬取B站动态列表
===================================
#### 功能
爬取一位B站用户的全部动态，按时间顺序从旧到新排列，保存为json

用途：例如希望检索某一条UP主曾经发过的动态。就可以用此方法存成json，然后在文件里进行字符串查找

#### 使用
```shell
git clone https://github.com/Starrah/BilibiliGetDynamics
cd BilibiliGetDynamics
pip install -r requirements.txt
# 默认会自动下载动态中的图片到pics文件夹内
python getDynamics.py 12345678
# 如果不希望自动下载图片（速度会更快），请加--no_download参数：
# python getDynamics.py 12345678 --no_download
```
将上述12345678换成你要查询的用户的UID即可。（查看UID：浏览器打开用户的个人空间，链接会形如https://space.bilibili.com/xxxxxxxx?from=balabalabala （?之后的部分可能有也可能没有，不用管），space.bilibili.com/ 后面紧跟的那一连串数字就是）

运行过程中会不断打印当前收到的数据。  
等待最终打印出“已完成”后，打开当前目录下的result.json即可查看结果。

#### 实现说明
（只有一个文件getDynamics.py、60几行代码，其实有个几分钟从上到下过一下就全看懂了）

##### 代码概述
基于[bilibili-api](https://github.com/Passkou/bilibili-api) 库开发，利用其中封装的User.get_dynamics接口请求json数据。 
主函数是main函数，里面用一个循环调用get_dynamics接口，开始时用offset=0调用
期间每次请求都会返回一个offset，需要在下一次请求时作为参数传入，从而依次请求各个页面。  
请求到的数据是一个cards数组、每个元素表示一条动态。  
cardToObj方法对其进行简单的字段筛选以压缩体积，然后保存起来。

##### 已知问题&改进方法
不能正确处理视频动态情况（其实就是筛选字段没有选对，作者懒了）。  
事实上，第93行（附近）`for card in res["cards"]:`循环内的card变量就是一条动态的完整对象，所有的信息都在这里面，可自行修改获得各种信息。  
更欢迎把您的修改发PR上来。
