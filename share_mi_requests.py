import base64
import random
import time
import requests
import functools
import json,sys,hashlib
import os
import pickle
import  urllib.parse
import multiprocessing

from encrpty import *
from mi_logger import logger
from timer import Timer
from config import global_config
from concurrent.futures import ProcessPoolExecutor
from util import (
    parse_json,
    send_wechat,
    wait_some_time,
    get_random_useragent
)


"""
主要用到的加密算法有两个：
1、登录接口的加密算法，包括请求头和body，具体加密逻辑在其他文件。
2、抢购、预约的入参加密，包括 yp-srs、 yp-ss、 yp-srt三个值。
具体加密逻辑比较敏感，暂不公开，感兴趣的可以联系。
"""

class MiSeckill(object):
    def __init__(self , user_name):
        # 初始化信息
        self.act_id = global_config.getRaw('config', 'act_id')
        self.timers = Timer()
        self.spider_session = SpiderSession(user_name)
        self.spider_session.load_cookies_from_local()
        self.login = Login(self.spider_session,user_name)
        self.session = self.spider_session.get_session()
        self.user_agent = self.spider_session.user_agent
        self.locationUrl = None


    def login_by_accountAndPassword(self):
        """
        登陆
        :return:
        """
        if self.login.is_login:
            logger.info('登录成功')
            return

        self.login.login_by_accountAndPassword()

        if self.login.is_login:
            #将cookie记录在本地
            self.spider_session.save_cookies_to_local(self.login.nickName)
        else:
            raise logger.error("账号密码登录失败！")

    def check_login(func):
        """
        用户登陆态校验装饰器。若用户未登陆，则调用登陆
        """
        @functools.wraps(func)
        def new_func(self, *args, **kwargs):
            if not self.login.is_login:
                self.login_by_accountAndPassword()
            return func(self, *args, **kwargs)
        return new_func


    @check_login
    def appoint(self):
        """
        预约
        """
        self._appoint()

    def getSignByData(self,data):
        #核心加密，隐藏
        pass

        re ={
            'yp-srt':xxx,
            'yp-srs': xxx,
            'yp-ss': xxx
        }
        return re

    def isAppoint(self):
        # 核心代码隐藏
        pass
        re = self.session.post("xxxxxxxxxxxxx",
                               data=json.dumps(data), headers=header)
        if re.json().get('code') == 0 and re.json().get('success')  and  re.json().get('data').get('userStatusInfo'):
            return re.json().get('data').get('userStatusInfo').get('ordered')
        else:
            logger.error('获取今日商品信息出错，程序继续执行。')
            return  False




    def _appoint(self):
        self.getTodayActid()
        if self.isAppoint() :
            logger.info("---------您已预约成功，无需再次预约！----------")
            return True

        nowtime = int(round(time.time() * 1000))
        data = [{}, {"actId": self.act_id, "tel": ""}]

        #获取校验所需加密参数
        signDict =  self.getSignByData(data)

        headerPhone = {
            "accept": "*/*"
            , "accept-encoding": "gzip, deflate, br"
            , "accept-language": "zh-CN,zh;q=0.9"
            , "content-type": "application/json"
            ,"referer": self.locationUrl
            ,"user-agent": self.user_agent
            , "X-Requested-With": "XMLHttpRequest"
            , "yp-srs": signDict['yp-srs']
            , "yp-ss": signDict['yp-ss']
            , "yp-srt": signDict['yp-srt']

        }

        re = self.session.post("https://m.xiaomiyoupin.com/mtop/act/orderspike/order?_=" + str(nowtime),
                               data=json.dumps(data),headers=headerPhone)

        if json.loads(re.text).get("code") == 0 and json.loads(re.text).get("success") == True:
            logger.info("---------预约成功，记得按时抢购哦！----------")
            logger.info("当前预约人数为：{}".format(json.loads(re.text).get("data").get("orderCount") ))
            return True
        else:
            logger.info("预约失败，返回结果为：{}".format(json.loads(re.text)))
            return False




    @check_login
    def seckill(self):
        """
        抢购
        """
        self._seckill()


    def seckill_by_proc_pool(self, work_count=1):
        """
        多进程进行抢购
        work_count：进程数量
        """
        multiprocessing.freeze_support()
        with ProcessPoolExecutor(work_count) as pool:
            for i in range(work_count):
                pool.submit(self.seckill)


    def getUserlevel(self):


        try :
            # 核心代码隐藏
            pass
            re = self.session.post("xxxx", data=json.dumps(data),
                                   headers=header)
            re = re.json().get("data").get("userLevelVO")
            # logger.info(re)
            if re:
                logger.info("获取用户品值为："+str(re.get("score"))+", 活跃度："+str(re.get("activity"))+
                        ", 名誉值："+str(re.get("reputation")))
        except Exception as e :
            logger.error("获取用户品值出现异常【{}】".format(e))


    def getTodayActid(self):
        try :
            #核心代码隐藏
            pass

            ###返回302转跳链接
            if re.headers.get('Location'):
                self.locationUrl = re.headers.get('Location')
                urlparse = urllib.parse.urlparse(self.locationUrl)
                query_dict = urllib.parse.parse_qs(urlparse.query)
                self.act_id = query_dict.get('actId')[0]
                logger.info("获取到今日飞天茅台商品id为 -----> {}".format(self.act_id))
            ##访问一次抢购页面
            self.session.get(self.locationUrl)

        except Exception as e :
            logger.error("获取当天商品id出错：{}".format(e))


    def _seckill(self):
        """
        抢购
        """
        a=0
        while True:
            try:
                self.getUserlevel()
                self.getTodayActid()
                self.timers.start()
                while True:
                    logger.info("第{}次抢购。".format(a))
                    flag = self.startKill()
                    #抢购成功直接返回，失败继续
                    if flag :
                        return
                    a = a + 1
                    wait_some_time()
                    if a>15 :
                        logger.info('抢购失败,明天继续努力。')
                        return

            except Exception as e:
                logger.info('抢购发生异常，稍后继续执行！', e)
            wait_some_time()

    def startKill(self):
        data = [{}, {"actId": self.act_id,
                     "token": self.act_id}]
        reDict = self.getSignByData(data)

        trustType = xxx


        headerPhone = {
            "accept": "*/*"
            , "accept-encoding": "gzip, deflate, br"
            , "accept-language": "zh-CN,zh;q=0.9"
            , "content-type": "application/json"
            ,"referer": self.locationUrl
            ,"user-agent": self.user_agent
            , "X-Requested-With": "XMLHttpRequest"
            , "c": xxxx
            , "d": xxxx
            , "yp-srs": reDict['yp-srs']
            , "yp-ss": reDict['yp-ss']
            , "yp-srt": reDict['yp-srt']

        }


        re = self.session.post("https://m.xiaomiyoupin.com/mtop/act/orderspike/ekips?_=" + str(int(time.time() * 1000)),
                               data=json.dumps(data), headers=headerPhone)

        if json.loads(re.text).get("code") == 0 :
            if json.loads(re.text).get("data").get("success"):
                logger.info("-------------成功啦，请作者喝杯咖啡吧！！！---------------")
                return True
        logger.info("抢购失败:【{}】".format(re.text.strip()))

        return False



