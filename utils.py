import base64
import requests
import os


def covert_image_to_base64(image_path):
    # 获得文件后缀名
    ext = image_path.split(".")[-1]
    if ext not in ["gif", "jpeg", "png"]:
        ext = "jpeg"

    with open(image_path, "rb") as image_file:
        # Read the file
        encoded_string = base64.b64encode(image_file.read())

        # Convert bytes to string
        base64_data = encoded_string.decode("utf-8")

        # 生成base64编码的地址
        base64_url = f"data:image/{ext};base64,{base64_data}"
        return base64_url



def format_welcome_html():
    config = {
        'name': "©十万个为什么",
        'description': '这是一本特别神奇的儿童声音图书，里面装着满满的好奇心大宝藏——十万个为什么，还有好多好多关于星星和宇宙的秘密呢！快来一场有趣的探险吧！😊',
        'introduction_label': "<br>本领揭秘",
        'rule_label': "<br>使用小指南",
        'char1': '它像一位超棒的故事大王，能把复杂的科学知识变成小朋友们最爱听的奇妙故事，说话又有趣又简单。',
        'char2': '只要故事里说到什么，它就能变魔术一样，做出好听的声音和好看的图画，让故事活灵活现！',
        'char3': '想知道学会了没？没问题！它还能变身小老师，根据故事里的知识点，出题目给你玩挑战游戏，答对了，就厉害啦！',

        'rule1': '1.进到这个神奇世界，对着大大的问话框，告诉它你想知道的东西或者喜欢的主题，它就会去智慧宝库里找答案。',
        'rule2': '2.找到答案后，它不光讲故事给你听，还会让故事变身，变成耳边的好声音和眼前精彩的图片！',
        'rule3': '3.听完故事，还想再聪明一点吗？那就去专门的问答小岛，那里藏着刚刚故事里的秘密知识点哦。',
        'rule4': '4.每个知识点都藏了一个小谜题，点一点，就能试试你是不是真的变成了那个知识小达人！',

    }
    image_src = covert_image_to_base64('logo1.jpg')
    return f"""
<div class="bot_cover">
    <div class="bot_avatar">
        <img src={image_src} />
    </div>
    <div class="bot_name">{config.get("name")}</div>
    <div class="bot_desc">{config.get("description")}</div>
    <div class="bot_intro_label">{config.get("introduction_label")}</div>
    <div class="bot_intro_ctx">
        <ul>
            <li>{config.get("char1")}</li>
            <li>{config.get("char2")}</li>
            <li>{config.get("char3")}</li>
            
        </ul>
    </div>
    <div class="bot_intro_label">{config.get("rule_label")}</div>
    <div class="bot_intro_ctx">
        <ul>
            <li>{config.get("rule1")}</li>
            <li>{config.get("rule2")}</li>
            <li>{config.get("rule3")}</li>
            <li>{config.get("rule4")}</li>
        </ul>
    </div>
</div>
"""
