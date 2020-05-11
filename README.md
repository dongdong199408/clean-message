# clean-message
## 基于albert的文本清洗策略
一、验证方式：登陆密码
注册（内网可不用密码协商）
POST字段：json
```{'username': 用户名,'password': 密码}
二、调用接口说明：http://localhost:5000/clean_message/
1、GET
参数：message=评论内容（最长支持128个）
例如：http://localhost:5000/clean_message/?message=老师您辛苦了
```
{"code":0,"result":{"is_clean":true,"probability":"0.9885522"}}
2、POST
参数：json格式
{'message':评论内容}
相应体说明：
状态码：200 //正常相应；
400 //参数信息错误；
401 //传参超时。
返回体：
```json格式
{'code': 0, //0为响应码，正常结果返回，1为规则返回结果；可不看
'result': 
{'probability': 0.45, //正常评论的概率（不用清洗的概率）
 'is_clean': True,是否需要清洗
}
}
```
