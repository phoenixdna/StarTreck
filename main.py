# Version 2.5
import os
import json
import time
import wave
import sys
#import pyaudio
import appbuilder
import re

class AudioPlayer:
    def __init__(self):
        # self.p = pyaudio.PyAudio()
        self.tts = appbuilder.TTS()
        self.path = os.getcwd()
    cwd = os.getcwd()
    print("cwd is :", cwd)

    def run_tts_and_play_audio(self, text: str):
        msg = self.tts.run(appbuilder.Message(content={"text": text}), audio_type="pcm", model="paddlespeech-tts",
                           stream=True)
        '''
        stream = self.p.open(format=self.p.get_format_from_width(2),
                             channels=1,
                             rate=24000,
                             output=True,
                             frames_per_buffer=2048)
        for pcm in msg.content:
            stream.write(pcm)
        stream.stop_stream()
        stream.close()
        '''
    def save_audio_to_file(self, text: str, filename: str):
        msg = self.tts.run(appbuilder.Message(content={"text": text}), audio_type="pcm", model="paddlespeech-tts", stream=True)

        # Prepare to write to file
        output_file = os.path.join(self.cwd, filename)
        print(f"writing audio to wave file...{filename}")

        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)#self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(24000)

            # Write audio data to file
            for pcm in msg.content:
                wf.writeframes(pcm)

        print("wave file done!")



# 设置appbuilder的token密钥，从页面上复制粘贴我的密钥，覆盖此处的 "your_appbuilder_token"

# 设置需要调用的app，从页面上复制粘贴应用ID，覆盖此处的 "先做知识库提取"


class MyAgent:

    static_question_json = {
        "题干": "",
        "选项": [
            "选项A",
            "选项B",
            "选项C",
            "选项D"
        ],
        "答案": "C"
    }

    def __init__(self):
        os.environ['APPBUILDER_TOKEN'] = "bce-v3/ALTAK-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        print("AppBuilder 模块导入成功！")
        print("您的AppBuilder Token为：{}".format(os.environ['APPBUILDER_TOKEN']))
        self.question_json = MyAgent.static_question_json
        self.question = self.question_json["题干"]
        self.choices = self.question_json["选项"]
        self.answer = self.question_json["答案"]

        self.rags = []
        self.knowledge_tags=[]

    def extract_rags(self, text:str):
        # 使用split方法按换行符分割文本，strip方法去除每行首尾的空白字符
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        print("lines:",lines)
        self.rags = lines

    def get_tags(self):
        return self.knowledge_tags


    def extract_knowledge_tags(self):
        #tag初始化
        self.knowledge_tags = [None] * len(self.rags)
        tag_extraction = appbuilder.TagExtraction(model="ERNIE Speed-AppBuilder")
        print("开始提取标签。。。")
        for i,sentence in enumerate(self.rags):
            print("句子是：", i, sentence)
            result = tag_extraction(appbuilder.Message(sentence))
            print("标签提取输出是：",i,result.content)
            self.knowledge_tags[i] = self.process_text(result.content)
            print("knowledge_tags:",i,self.knowledge_tags)



    def process_text(self,text:str)->str:
        # 使用正则表达式匹配每行的主题词
        pattern = re.compile(r'\d+\.\s*(.+)')
        #print("string in processing text:",text)
        # 查找所有匹配的主题词
        matches = pattern.findall(text)

        # 检查matches数组的长度
        if len(matches) == 0:
            return "空，空"
        elif len(matches) == 1:
            return matches[0].strip()
        else:
            return matches[0].strip() + ',' + matches[1].strip()



    # 示例文本
    text = '''黑洞是**广义相对论预言的一种特殊天体**。它的基本特征是有一个封闭的边界，称为黑洞的‘视界’；外界的物质和辐射可以进入视界，视界内的东西却不能逃逸到外面去^[1]^。

            黑洞的结构很简单：一个视界包围着一个奇点。这个点称为黑洞的"奇点"，那里的物质密度和压力都变成了无穷大。尽管人们经常把视界称为"黑洞的表面"，其实在这个"表面"上并不存在任何有形的东西^[1][3]^。'''


    def set_question(self, q_json: dict={}):
        if q_json == {}:
            self.question_json = MyAgent.static_question_json
        else:
            self.question_json = q_json
        self.update_self()
        return self.question,self.choices,self.answer


    def update_self(self):
        self.question = self.question_json["题干"]
        self.choices = self.question_json["选项"]
        self.answer = self.question_json["答案"]


    def generate_quesiton(self, context):
        print("playground中的context", context)
        play = appbuilder.Playground(
            prompt_template='''
                    ```\n
                        {context}
                    ```\n
                    请基于以上文本出单选题，必须具备4个选项，正确选项必须唯一，其他选项必须是错误的，不同选项内容必须有差异，选项中不要包含选项字母，答案是正确选项的字母，输出格式必须严格符合json格式，举例如下：
                    ```
                        "题干": "科举制度在我国历史上具有重要意义，关于其起源和正式诞生，下列说法正确的是：",
                        "选项": [
                            "分科考试选拔官员的办法开始于隋炀帝时期。",
                            "科举制在隋文帝时期正式诞生。",
                            "隋炀帝时设“进士科”，成为了科举制正式诞生的标志。",
                            "科举制度的起源和正式诞生都是在唐朝。"
                        ],
                        "答案": "C"
                    ```
                    ''',
            model="ERNIE Speed-AppBuilder"
        )
        result = play(appbuilder.Message(context),
                      stream=False)
        print("playground得到的result.content", result.content)
        # 去掉前后的 ```json 和 ```
        # 去掉 Markdown 代码块标记和大括号
        cleaned_content = result.content.replace("```json", "").replace("```", "").strip()

        # 如果 cleaned_content 没有大括号包裹，再添加大括号
        if not (cleaned_content.startswith("{") and cleaned_content.endswith("}")):
            cleaned_content = "{" + cleaned_content + "}"

        print("playground得到的题目内容是（去掉前置符号）：", cleaned_content)

        # 解析 JSON
        data = json.loads(cleaned_content)

        self.question_json= data

        # 打印解析后的字典
        print("question-json now is: ",data)


    def rag_query(self, query: str):
        app_id = "06d4b747-93ed-490f-892b-50d78b44662d"
        # 初始化Agent实例
        agent = appbuilder.AppBuilderClient(app_id)
        # 创建会话ID
        conversation_id = agent.create_conversation()
        print("您的AppBuilder App ID为：{}".format(app_id))
        print("RAG processing")

        response_message = agent.run(conversation_id=conversation_id, query=query)
        description = response_message.content.answer
        print("提取助手的回复是：{}".format(description))
        self.extract_rags(description)
        print("rags:", self.rags)



        return description

    # 进行小说创作：

    def write_novel(self,description: str):
        model = "ERNIE Speed-AppBuilder"
        style_writing = appbuilder.StyleWriting(model)

        query1 = f'''
         你现在是一个科幻小说家，专门给小朋友们写小说，请基于如下的文字生成一段小说```
                    ```
                    {description}
                    ```
        请用通俗易懂的语言表达.
        '''

        style = "通用"
        length = 600

        msg = appbuilder.Message(query1)
        answer = str(style_writing(message=msg, style_query=style, length=length).content)
        print("小说是：", answer)
        return answer

    def generate_img(self, query: str):
        text2Image = appbuilder.Text2Image()
        content_data = {"prompt": query, "width": 1024, "height": 1024, "image_num": 1}
        msg = appbuilder.Message(content_data)
        out = text2Image.run(msg)
        img_url = out.content['img_urls'][0]
        print(f"生成 {query} 图片地址:{img_url}")
        return img_url

# ss= re.sub(r"\s+", "", answer)
# print("answer is :", ss)


'''

myAgent = MyAgent()
extract_msg = myAgent.rag_query("冥王星")
my_answer = myAgent.write_novel(extract_msg)
# 进行文本转语音：
audio_player = AudioPlayer()
audio_player.save_audio_to_file(my_answer, "hello.wav")



tts = appbuilder.TTS()
cwd = os.getcwd()
print("cwd is :", cwd)

# 使用baidu-tts模型, 默认返回MP3格式
inp = appbuilder.Message(content={"text": ss})
out = tts.run(inp)
mp3_sample_path = os.path.join(cwd,"sample.mp3")
with open(mp3_sample_path, "wb") as f:
    f.write(out.content["audio_binary"])
print("成功将文本转语音，mp3格式文件已写入：{}".format(mp3_sample_path))

# 使用paddlespeech-tts模型，目前只支持返回WAV格式
wav_sample_path = os.path.join(cwd, "sample.wav")
inp = appbuilder.Message(content={"text": ss})
out = tts.run(inp, model="paddlespeech-tts", audio_type="wav")
with open(wav_sample_path, "wb") as f:
    f.write(out.content["audio_binary"])
print("成功将文本转语音，wav格式文件已写入：{}".format(wav_sample_path))
'''