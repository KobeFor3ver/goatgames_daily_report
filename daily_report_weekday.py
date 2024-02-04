import hmac
import hashlib
import base64
import urllib.parse
import time
import json
import urllib.request
from loguru import logger
from requests import request


class DingTalkBot:
    """
    钉钉机器人
    """

    # 适配钉钉机器人的加签模式和关键字模式/白名单IP模式
    def __init__(self, secret=None, webhook_url=None):
        if secret:
            timestamp = str(round(time.time() * 1000))
            sign = self.get_sign(secret, timestamp)
            self.webhook_url = webhook_url + f'&timestamp={timestamp}&sign={sign}'  # 最终url，url+时间戳+签名
        else:
            self.webhook_url = webhook_url
        self.headers = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }

    def get_sign(self, secret, timestamp):
        """
        根据时间戳 + "sign" 生成密钥
        把timestamp+"\n"+密钥当做签名字符串，使用HmacSHA256算法计算签名，然后进行Base64 encode，最后再把签名参数再进行urlEncode，得到最终的签名（需要使用UTF-8字符集）。
        :return:
        """
        string_to_sign = f'{timestamp}\n{secret}'.encode('utf-8')
        hmac_code = hmac.new(
            secret.encode('utf-8'),
            string_to_sign,
            digestmod=hashlib.sha256).digest()

        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return sign


    def send_text(self, title, content, mobiles=None, is_at_all=False):
        """
        发送文本消息
        :param content: 发送的内容
        :param mobiles: 被艾特的用户的手机号码，格式是列表，注意需要在content里面添加@人的手机号码
        :param is_at_all: 是否艾特所有人，布尔类型，true为艾特所有人，false为不艾特
        """
        if mobiles:
            if isinstance(mobiles, list):
                payload = {
                    "msgtype": "text",
                    "title": title,
                    "text": {
                        "content": content
                    },
                    "at": {
                        "atMobiles": mobiles,
                        "isAtAll": False
                    }
                }
                for mobile in mobiles:
                    payload["text"]["content"] += f"@{mobile}"
            else:
                raise TypeError("mobiles类型错误 不是list类型.")
        else:
            payload = {
                "msgtype": "text",
                "title": title,
                "text": {
                    "content": content
                },
                "at": {
                    "atMobiles": "",
                    "isAtAll": is_at_all
                }
            }
        response = request(url=self.webhook_url, json=payload, headers=self.headers, method="POST")
        if response.json().get("errcode") == 0:
            logger.debug(f"send_text发送钉钉消息成功：{response.json()}")
            return True
        else:
            logger.debug(f"send_text发送钉钉消息失败：{response.text}")
            return False

    def send_link(self, title, text, message_url, pic_url=None):
        """
        发送链接消息
        :param title: 消息标题
        :param text: 消息内容，如果太长只会部分展示
        :param message_url: 点击消息跳转的url地址
        :param pic_url: 图片url
        """
        payload = {
            "msgtype": "link",
            "link": {
                "title": title,
                "text": text,
                "picUrl": pic_url,
                "messageUrl": message_url
            }
        }
        response = request(url=self.webhook_url, json=payload, headers=self.headers, method="POST")
        if response.json().get("errcode") == 0:
            logger.debug(f"send_link发送钉钉消息成功：{response.json()}")
            return True
        else:
            logger.debug(f"send_link发送钉钉消息失败：{response.text}")
            return False

    def send_markdown(self, title, text, mobiles=None, is_at_all=False):
        """
        发送markdown消息
        目前仅支持md语法的子集，如标题，引用，文字加粗，文字斜体，链接，图片，无序列表，有序列表
        :param title: 消息标题，首屏回话透出的展示内容
        :param text: 消息内容，markdown格式
        :param mobiles: 被艾特的用户的手机号码，格式是列表，注意需要在text里面添加@人的手机号码
        :param is_at_all: 是否艾特所有人，布尔类型，true为艾特所有人，false为不艾特
        """
        if mobiles:
            if isinstance(mobiles, list):
                payload = {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": title,
                        "text": text
                    },
                    "at": {
                        "atMobiles": mobiles,
                        "isAtAll": False
                    }
                }
                for mobile in mobiles:
                    payload["markdown"]["text"] += f" @{mobile}"
            else:
                raise TypeError("mobiles类型错误 不是list类型.")
        else:
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": text
                },
                "at": {
                    "atMobiles": "",
                    "isAtAll": is_at_all
                }
            }
        response = request(url=self.webhook_url, json=payload, headers=self.headers, method="POST")
        if response.json().get("errcode") == 0:
            logger.debug(f"send_markdown发送钉钉消息成功：{response.json()}")
            return True
        else:
            logger.debug(f"send_markdown发送钉钉消息失败：{response.text}")
            return False

    def send_action_card_single(self, title, text, single_title, single_url, btn_orientation=0):
        """
        发送消息卡片(整体跳转ActionCard类型)
        :param title: 消息标题
        :param text: 消息内容，md格式消息
        :param single_title: 单个按钮的标题
        :param single_url: 点击singleTitle按钮后触发的URL
        :param btn_orientation: 0-按钮竖直排列，1-按钮横向排列
        """
        payload = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": text,
                "singleTitle": single_title,
                "singleURL": single_url,
                "btnOrientation": btn_orientation,
            }

        }
        response = request(url=self.webhook_url, json=payload, headers=self.headers, method="POST")
        if response.json().get("errcode") == 0:
            logger.debug(f"send_action_card_single发送钉钉消息成功：{response.json()}")
            return True
        else:
            logger.debug(f"send_action_card_single发送钉钉消息失败：{response.text}")
            return False

    def send_action_card_split(self, title, text, btns, btn_orientation=0):
        """
        发送消息卡片(独立跳转ActionCard类型)
        :param title: 消息标题
        :param text: 消息内容，md格式消息
        :param btns: 列表嵌套字典类型，"btns": [{"title": "内容不错", "actionURL": "https://www.dingtalk.com/"}, ......]
        :param btn_orientation: 0-按钮竖直排列，1-按钮横向排列
        """
        payload = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": text,
                "btns": [],
                "btnOrientation": btn_orientation,
            }

        }
        for btn in btns:
            payload["actionCard"]["btns"].append({
                "title": btn.get("title"),
                "actionURL": btn.get("action_url")
            })
        response = request(url=self.webhook_url, json=payload, headers=self.headers, method="POST")
        if response.json().get("errcode") == 0:
            logger.debug(f"send_action_card_split发送钉钉消息成功：{response.json()}")
            return True
        else:
            logger.debug(f"send_action_card_split发送钉钉消息失败：{response.text}")
            return False

    def send_feed_card(self, links_msg):
        """
        发送多组消息卡片(FeedCard类型)
        :param links_msg: 列表嵌套字典类型，每一个字段包括如下参数：title(单条信息文本), messageURL(点击单条信息后的跳转链接), picURL(单条信息后面图片的url)
        """
        payload = {
            "msgtype": "feedCard",
            "feedCard": {
                "links": []
            }
        }
        for link in links_msg:
            payload["feedCard"]["links"].append(
                {
                    "title": link.get("title"),
                    "messageURL": link.get("messageURL"),
                    "picURL": link.get("picURL")
                }
            )
        response = request(url=self.webhook_url, json=payload, headers=self.headers, method="POST")
        if response.json().get("errcode") == 0:
            logger.debug(f"send_feed_card发送钉钉消息成功：{response.json()}")
            return True
        else:
            logger.debug(f"send_feed_card发送钉钉消息失败：{response.text}")
            return False

    def send_image(self, image_base64, mobiles=None, is_at_all=False):
        """
        发送图片消息
        """
        if mobiles:
            if isinstance(mobiles, list):
                payload = {
                    "msgtype": "image",
                    "image": {
                        "base64": image_base64
                    },
                    "at": {
                        "atMobiles": mobiles,
                        "isAtAll": False
                    }
                }
                for mobile in mobiles:
                    payload["image"]["base64"] += f" @{mobile}"
            else:
                raise TypeError("mobiles类型错误 不是list类型.")
        else:
            payload = {
                "msgtype": "image",
                "image": {
                    "base64": image_base64
                },
                "at": {
                    "atMobiles": "",
                    "isAtAll": is_at_all
                }
            }
        response = request(url=self.webhook_url, json=payload, headers=self.headers, method="POST")
        if response.json().get("errcode") == 0:
            logger.debug(f"send_markdown发送钉钉图片成功：{response.json()}")
            return True
        else:
            logger.debug(f"send_markdown发送钉钉图片失败：{response.text}")
            return False

# 读取数据开始
import requests
import numpy as np
import pandas as pd
import datetime as dt
import termtables as tt
from dateutil.relativedelta import relativedelta
from tabulate import tabulate

today = dt.datetime.today()
today_weekday = today.weekday()
today_string = f"{today.year}-{today.month}-{today.day}"
first_day_of_month = dt.datetime.today().date().replace(day=1)
first_day_of_last_month = (today.date()-relativedelta(months=1)).replace(day=1)

# 填写计划花费、安装以及7日roi：
planned_cost = 813055
planned_install = 72137
planned_7roi = 0.147

# 读取数据(get data)
def get_df():
    url = "https://bi.goatgames.com/bidata/adData/query"
    data = {
        "fields": ["impressions", "clicks", "install", "register", "login", "register_rate", "cost", "cpi", "cpu",
                   "cpm", "cpc", "ctr", "cvr", "ir", "pay_sum_1", "pay_sum_3", "pay_sum_7", "roi_1", "roi_3",
                   "roi_7"], "conditions": [{"field": "date", "operate": "ge", "value": f"{first_day_of_last_month.year}-{first_day_of_last_month.month}-{first_day_of_last_month.day}"},
                                            {"field": "date", "operate": "le", "value": f"{today.year}-{today.month}-{today.day}"},
                                            {"field": "app_id", "operate": "in",
                                             "value": ["com.goatgames.snd.gb.gp", "com.goatgames.snd.gb.ios"]},
                                            {"field": "game_id", "operate": "in", "value": [10038]},
                                            {"field": "media", "operate": "ne", "value": "untrusteddevices"},
                                            {"field": "time_zone", "operate": "eq", "value": 8},
                                            {"field": "revenue_sharing", "operate": "eq", "value": 1}],
        "aggregations": [{"field": "date", "unit": "day"}], "unified_currency": 1, "exportType": "excel",
        "offline": 0, "isNeedColor": 1}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Language": "zh"}
    res = requests.post(url=url, json=data, headers=headers).json()["data"]
    df = pd.DataFrame(res)
    return df

data = get_df()

# 处理数据
data['start_date'] = pd.to_datetime(data['start_date'])
data['end_date'] = pd.to_datetime(data['end_date'])
this_month_data = data[data['end_date'].dt.month==today.month]

three_one_coefficient = data[(data['end_date'].dt.date<=today.date()-dt.timedelta(days=3))\
     & (data['end_date'].dt.date>=today.date()-dt.timedelta(days=17))]['pay_sum_3'].sum()/\
    data[(data['end_date'].dt.date<=today.date()-dt.timedelta(days=3))\
     & (data['end_date'].dt.date>=today.date()-dt.timedelta(days=17))]['pay_sum_1'].sum()
seven_three_coefficient = data[(data['end_date'].dt.date<=today.date()-dt.timedelta(days=7))\
     & (data['end_date'].dt.date>=today.date()-dt.timedelta(days=21))]['pay_sum_7'].sum()/\
    data[(data['end_date'].dt.date<=today.date()-dt.timedelta(days=7))\
     & (data['end_date'].dt.date>=today.date()-dt.timedelta(days=21))]['pay_sum_3'].sum()

total_cost = round(this_month_data['cost'].sum())
total_install = this_month_data['install'].sum()
total_1roi = this_month_data['pay_sum_1'].sum()/this_month_data['cost'].sum()
def total_7roi_calculator():
    if this_month_data.shape[0] < 7:
        total_7roi = 0
        return total_7roi
    else:
        roi_observation_day = f"{today.year}-{today.month}-{today.day-6}"
        roi_data = this_month_data[this_month_data['end_date'] <= roi_observation_day]
        total_7roi = round(roi_data['pay_sum_7'].sum()/roi_data['cost'].sum(), 4)
        return total_7roi
total_7roi = total_7roi_calculator()
predicted_7roi = this_month_data['pay_sum_1'].sum()/this_month_data['cost'].sum()*three_one_coefficient*seven_three_coefficient

# 月累计数据：
content = f"本月累计{first_day_of_month.month}.{first_day_of_month.day}-{today.month}.{today.day}：\
\nCost: " + "{:,}".format(total_cost) + f"\t目标完成度: {total_cost/planned_cost:.2%}"\
+ "\nInstall: " + "{:,}".format(total_install) + f"\t目标完成度: {total_install/planned_install:.2%}"\
+ f"\n1日ROI(已完整): {total_1roi:.2%}"\
+ f"\n7日ROI(已完整): {total_7roi:.2%}" + f"\t目标完成度: {total_7roi/planned_7roi:.2%}"\
+ f"\n7日ROI预估: {predicted_7roi:.2%}"

# 周数据表格：
header_list = ['date', 'cost', 'install', '1日ROI', '3日ROI(包含预估)', '7日ROI(包含预估)']
my_table = []
for i in range(7):
    one_row = []
    index_date = today.date() - dt.timedelta(days=7-i)
    index_day = f"{index_date.year}-{index_date.month}-{index_date.day}"
    one_row.append(f"{index_date.month}-{index_date.day}")
    index_day_cost = data[data['end_date']==index_day]['cost'][7-i]
    one_row.append("{:,}".format(round(index_day_cost, 2)))
    index_day_install = data[data['end_date']==index_day]['install'][7-i]
    one_row.append("{:,}".format(index_day_install))
    index_day_1roi = data[data['end_date']==index_day]['roi_1'][7-i]
    one_row.append(f"{index_day_1roi:.2%}")
    index_three_one_coefficient = data[(data['end_date'].dt.date<=today.date()-dt.timedelta(days=7-i+2))\
     & (data['end_date'].dt.date>=today.date()-dt.timedelta(days=7-i+16))]['pay_sum_3'].sum()/\
    data[(data['end_date'].dt.date<=today.date()-dt.timedelta(days=7-i+2))\
     & (data['end_date'].dt.date>=today.date()-dt.timedelta(days=7-i+16))]['pay_sum_1'].sum()
    index_seven_three_coefficient = data[(data['end_date'].dt.date<=today.date()-dt.timedelta(days=7-i+6))\
     & (data['end_date'].dt.date>=today.date()-dt.timedelta(days=7-i+20))]['pay_sum_7'].sum()/\
    data[(data['end_date'].dt.date<=today.date()-dt.timedelta(days=7-i+6))\
     & (data['end_date'].dt.date>=today.date()-dt.timedelta(days=7-i+20))]['pay_sum_3'].sum()
    if pd.to_datetime(index_day).date() <= today.date()-dt.timedelta(days=2):
        index_predicted_3roi = data[data['end_date']==index_day]['roi_3'][7-i]
    else:
        index_predicted_3roi = index_day_1roi * index_three_one_coefficient
    one_row.append(f"{index_predicted_3roi:.2%}")
    if pd.to_datetime(index_day).date() <= today.date()-dt.timedelta(days=6):
        index_predicted_7roi = data[data['end_date']==index_day]['roi_7'][7-i]
    else:
        index_predicted_7roi = index_day_1roi * index_three_one_coefficient * index_seven_three_coefficient
    one_row.append(f"{index_predicted_7roi:.2%}")
    my_table.append(one_row)


# 保存表格&画趋势图
#%matplotlib inline
import matplotlib
from matplotlib import pyplot as plt

# 表格列居中、去除index
df = pd.DataFrame(my_table, columns = header_list)
df_style = df.style.set_table_styles([dict(selector='th', props=[('text-align', 'center')])])\
        .hide(axis='index')
df_style = df_style.set_properties(**{'text-align': 'center'})

# 表格图
import dataframe_image as dfi
dfi.export(df_style, 'df.png')

# 趋势图
fig, ax1 = plt.subplots(figsize=(10,6))
ax1.plot(df['date'].tolist(), (df['1日ROI'].apply(lambda x: x.strip('%')).apply(float)/100).tolist(), color='blue', label='1ROI')
ax1.plot(df['date'].tolist(), (df['7日ROI(包含预估)'].apply(lambda x: x.strip('%')).apply(float)/100).tolist(), color='red', label='7ROI(predicted)')
ax1.legend(['1ROI', '7ROI(predicted)'], bbox_to_anchor=(1, 1.15), loc = 'upper right')
ax1.scatter(df['date'], df['1日ROI'].apply(lambda x: x.strip('%')).apply(float)/100, color='blue')
for i in range(len(df)): 
    ax1.text(i + 0.15, (df['1日ROI'].apply(lambda x: x.strip('%')).apply(float)/100).iloc[i], df['1日ROI'].iloc[i], verticalalignment='bottom', color='blue', horizontalalignment='center')

ax1.set_xlabel('date')

ax1.scatter(df['date'], df['7日ROI(包含预估)'].apply(lambda x: x.strip('%')).apply(float)/100, color='red')
for i in range(len(df)): 
    ax1.text(i + 0.15, (df['7日ROI(包含预估)'].apply(lambda x: x.strip('%')).apply(float)/100).iloc[i], df['7日ROI(包含预估)'].iloc[i], verticalalignment='bottom', color='red', horizontalalignment='center')

ax1.axhline(y = 0.0333, color = 'b', linestyle = 'dashed')
ax1.axhline(y = 0.1333, color = 'r', linestyle = 'dashed') 

fig.tight_layout()
plt.title('Recent 7 Days 1ROI and 7ROI(predicted) Trend')
plt.xticks(rotation=45) # Rotate x-axis labels for better readability
plt.savefig('trend.png')


# 将图片转换成url
import pyimgur
CLIENT_ID = "f8e9a2d24f51064"
path = 'df.png'

im = pyimgur.Imgur(CLIENT_ID)
uploaded_image_df = im.upload_image(path, title='df.png')
#uploaded_image_df.link

path = 'trend.png'
uploaded_image_trend = im.upload_image(path, title='trend.png')
#uploaded_image_trend.link


# 发送消息
if __name__ == '__main__':
    my_secret = 'SECebdb1577dcf31b7f7d17bb0326afcb92b892772826f679e80f036f279046039b'
    my_url = 'https://oapi.dingtalk.com/robot/send?access_token=75d22f1a610b983ab0f8927df4e0a4efe36cafc6e52e5a48a0a98e7838784963'

    dingding = DingTalkBot(secret=my_secret, webhook_url=my_url)
    #content = ...
    dingding.send_text(title = "SND日报数据播报", content=content, is_at_all=False)
    dingding.send_markdown(title = "最近7天数据", text = f"**最近7天数据:**\n![image]({uploaded_image_df.link})\n\n**1日ROI和7日ROI(包含预估)趋势:**\n![image]({uploaded_image_trend.link})", mobiles=None, is_at_all=False)

if __name__ == '__main__':
    my_secret = 'SEC275e0afb43993c477e5b42ceb4c71b320d3d4c898884d37dd153b0833a5a0042'
    my_url = 'https://oapi.dingtalk.com/robot/send?access_token=ef52910f065f9043f4493777dc06b0f4a91111e065beb5c798946ba4064d04c1'

    dingding = DingTalkBot(secret=my_secret, webhook_url=my_url)
    #content = ...
    dingding.send_text(title = "SND日报数据播报", content=content, is_at_all=False)
    dingding.send_markdown(title = "最近7天数据", text = f"**最近7天数据:**\n![image]({uploaded_image_df.link})\n\n**1日ROI和7日ROI(包含预估)趋势:**\n![image]({uploaded_image_trend.link})", mobiles=None, is_at_all=False)

