# Version2.5
import gradio as gr
import json
# import soundfile as sf
import random
import main
import time
import os
import pandas
import threading
from utils import format_welcome_html

# from datetime import datetime

system_prompt = ""
my_Story = ""
query = ""
log_contents = ""
index = 0

DEBUGIMG = True
DEBUGAUDIO = False

static_question_json = {
    "题干": "科举制度在我国历史上具有重要意义，关于其起源和正式诞生，下列说法正确的是：",
    "选项": [
        "分科考试选拔官员的办法开始于隋炀帝时期。",
        "科举制在隋文帝时期正式诞生。",
        "隋炀帝时设“进士科”，成为了科举制正式诞生的标志。",
        "科举制度的起源和正式诞生都是在唐朝。"
    ],
    "答案": "C",
    "知识点标签": [
        "历史",
        "科举制度"
    ]
}

js_func = """
function refresh() {
    const url = new URL(window.location);

    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""


# 播放 gr.Audio 组件中加载的音频文件


# def play_audio():
#   audio.play()

def is_readable(file_path):
    try:
        with open(file_path, 'r') as file:
            return True
    except IOError:
        return False


uid = threading.current_thread().name

with gr.Blocks(gr.themes.Soft(), js=js_func, css='appBot.css') as demo:
    # 标题栏
    def update_knowledge(selected_index: gr.SelectData, dataframe_origin):
        val = my_agent.rags[selected_index.index[0]]

        return val


    GEN_KNOWLEDGE = False
    GEN_Q_MARK = False


    def gen_knowledge():
        global GEN_KNOWLEDGE  # Declare as global to modify the outer scope variable
        my_agent.extract_knowledge_tags()  # 调用tagextraction组件来生成
        knowledge_tags = my_agent.get_tags()
        print('knowledge_tags in gen_knowledge', knowledge_tags)
        dataframe_1t_value = pandas.DataFrame({"内容描述": knowledge_tags})
        if knowledge_tags:
            GEN_KNOWLEDGE = True
            return dataframe_1t_value, my_agent.rags[0], '载入知识库成功'
        else:
            # dataframe_1t_value = None
            return dataframe_1t_value, None, '系统提示：请先生成故事'


    def gen_question(question_text):
        global GEN_Q_MARK
        global GEN_KNOWLEDGE
        if GEN_KNOWLEDGE:
            my_agent.generate_quesiton(question_text)
            question, choices, answer = my_agent.set_question(my_agent.question_json)
            options = ["A." + choices[0], "B." + choices[1],
                       "C." + choices[2], "D." + choices[3]]
            GEN_Q_MARK = True
            return gr.update(value='## ' + question), gr.update(choices=options), '题目已经生成'

        else:
            return None, None, '系统提示：请先生成知识点'


    def check_answer(choice):
        global GEN_Q_MARK
        if GEN_Q_MARK:
            if choice[0] == my_agent.answer:
                return gr.update(value="## 恭喜你答对啦！再接再厉！", visible=True), "清查阅答案"
            else:
                return gr.update(value="## 很抱歉你回答错误啦，再试一次吧！", visible=True), "清查阅答案"
        else:
            return None, "请先生成题目"


    def game_ui():
        return {tabs: gr.update(visible=False), main_tabs: gr.update(visible=True)}


    def welcome_ui():
        return {tabs: gr.update(visible=True), main_tabs: gr.update(visible=False)}


    """demo.css = 
        body, .gradio-container, .gr-block, .gr-block > div, .gr-block > div > div {
            background-color: #00008B !important;  /* 设置深蓝色背景 */
            color: #FFFFFF !important;  /* 设置文本颜色为白色 */
        }
        /* 为聊天界面组件设置样式 */
        input[type="text"] {
            background-color: #00008B !important;  /* 设置深蓝色背景 */
            color: #FFFFFF !important;  /* 设置文本颜色为白色 */
        }

        /* 为对话输入框组件设置样式 */
        user_prompt {
            background-color: #00008B !important;  /* 设置深蓝色背景 */
            color: #FFFFFF !important;  /* 设置文本颜色为白色 */
        }
        
        markdown {
            background-color: #1e1e30 !important; /* 蓝黑色背景 */
            color: #FFFFFF !important; /* 白色字体 */
            padding: 20px;             /* 内边距 */
            border-radius: 5px;        /* 圆角 */
        }
    """
    demo.title = 'StarTrek'
    gr.Markdown('''<center><font size=6 style="color: #FFFFFF;">十万个为什么之星际迷航V2.5</font></center>''')
    state = gr.State({'session_seed': uid})
    tabs = gr.Tabs(visible=True)
    with tabs:
        welcome_tab = gr.Tab('软件介绍', id=0)
        with welcome_tab:
            user_chat_bot_cover = gr.HTML(format_welcome_html())
        with gr.Row():
            new_button = gr.Button(value='🚀我们的旅程是星辰大海', variant='primary')
    # 程序内部消息
    # question_json = gr.State(static_question_json)
    my_agent = main.MyAgent()
    question, choices, answer = my_agent.set_question()
    #    my_agent.extract_rags(rags)
    #    my_agent.extract_knowledge_tags()
    # question = static_question_json["题干"]
    # choices = static_question_json["选项"]
    # answer = static_question_json["答案"]
    # tags = static_question_json["知识点标签"]

    options = ["A." + choices[0], "B." + choices[1],
               "C." + choices[2], "D." + choices[3]]
    main_tabs = gr.Tabs(visible=False)
    with main_tabs:
        game_tab = gr.Tab(visible=True, label='故事窗口', )
        with game_tab:
            with gr.Row():
                with gr.Column(scale=7):
                    with gr.Row():
                        chatbot = gr.Chatbot(label='聊天界面', value=[], render_markdown=False, height=500,
                                             visible=True)
                    with gr.Row():
                        user_prompt = gr.Textbox(label='对话输入框（按Enter发送消息）', interactive=True, visible=True)
                        # input_audio = gr.Audio(sources=['microphone'])
                with gr.Column(scale=3):
                    with gr.Row():
                        audio = gr.Audio(label="output", interactive=False, autoplay=True)
                    with gr.Row():
                        image_output = gr.Image('logo.jpg', interactive=False, label="Your Image")
            clear = gr.Button("清除")

        test_tab = gr.Tab(label='测试窗口', visible=True)
        with test_tab:
            with gr.Row():
                with gr.Column(scale=7):
                    knowledge_output = gr.Textbox(label="Logs", lines=10, interactive=False, visible=True)
                    test = gr.Button("生成题目", visible=True)

                    question_markdown = gr.Markdown("## " + question, elem_classes="custom-markdown")
                    choices_radio = gr.Radio(options, label="请作答", interactive=True)
                    check_button = gr.Button("提交答案")
                with gr.Column(scale=3):
                    load = gr.Button("载入知识库", visible=True)
                    dataframe_1_value = pandas.DataFrame({"内容描述": my_agent.get_tags()})
                    dataframe_1 = gr.Dataframe(value=dataframe_1_value, label="知识点", interactive=False)
                    answer_markdown = gr.Markdown("## " + "您的答案是", visible=False)

            dataframe_1.select(update_knowledge, inputs=dataframe_1, outputs=knowledge_output)
        # chatbot = gr.Chatbot()
        # msg = gr.Textbox()

        with gr.Row():
            return_welcome_button = gr.Button(value="↩️返回首页")

        with gr.Row():
            status_markdown = gr.Markdown("系统运行状态：正常")
            # 按钮点击时检查和播放音频
        test.click(gen_question, knowledge_output, [question_markdown, choices_radio, status_markdown])
        load.click(gen_knowledge, None, [dataframe_1, knowledge_output, status_markdown])
        check_button.click(check_answer, choices_radio, [answer_markdown, status_markdown])

    # change ui
    new_button.click(game_ui, outputs=[tabs, main_tabs])
    return_welcome_button.click(welcome_ui, outputs=[tabs, main_tabs])


    def user(user_message, history):
        global my_Story
        global query

        extract_msg = my_agent.rag_query(user_message)
        print("extract_msg:", extract_msg)
        my_Story = my_agent.write_novel(extract_msg)
        knowledge = my_agent.knowledge_tags
        dataframe_1t_value = pandas.DataFrame({"内容描述": knowledge})
        query = user_message
        return "", history + [[user_message, None]], dataframe_1t_value


    def bot(history):
        # bot_message = random.choice(["你好吗？", "我爱你", "我很饿"])

        history[-1][1] = my_Story
        yield history
        # for character in my_Story:
        #    history[-1][1] += character
        #    time.sleep(0.05)
        #    yield history


    def update_image():
        if DEBUGIMG:
            yield gr.update(value='https://img.3dmgame.com/uploads/allimg/171129/377-1G1291SS1.jpg')
        else:
            my_imgurl = my_agent.generate_img(query)
            yield gr.update(value=my_imgurl)


    '''
    def append_log(log_text):
        global log_contents
        # 获取当前时间
        # now = datetime.now()
        # 格式化当前时间
        # formatted_now = now.strftime("%Y-%m-%d %H:%M:%S->")
        log_contents += log_text + "\n"
        return log_contents


    def update_log():
        global log_contents
        return gr.update(value=log_contents)
    
    '''


    # 添加检查和播放音频文件的函数
    def check_and_play_audio():
        audio_file = "hello.wav"
        if os.path.exists(audio_file):
            append_log(f"{audio_file}existed")
            return gr.update(value=audio_file, visible=True)
        else:
            append_log(f"{audio_file} not found.")
            return gr.update(value=None, visible=False)


    def update_audio():
        myaudio = main.AudioPlayer()
        # cwd = os.getcwd()
        # append_log(f"The cwd is：{cwd}")
        # file_path = os.path.join(cwd, "hello.wav")
        file_path = "hello.wav"
        if is_readable(file_path):
            print(f"The file {file_path} is readable.")
        else:
            print(f"The file {file_path} is not readable.")
        print(f"当前wave文件：{file_path}")
        if not DEBUGAUDIO:
            myaudio.save_audio_to_file(my_Story, file_path)  # 记得去掉注释；生成音频

        return gr.update(value=file_path, visible=True)


    user_prompt.submit(user, [user_prompt, chatbot], [user_prompt, chatbot], queue=False).then(
        bot, chatbot, chatbot
    ).then(
        update_audio, None, audio
    ).then(
        update_image, None, image_output
    )

    clear.click(lambda: None, None, chatbot, queue=False)

# demo.queue()
demo.launch()
