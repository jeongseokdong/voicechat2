import streamlit as st

from audiorecorder import audiorecorder

import openai
import os
from datetime import datetime

from gtts import gTTS

import base64

print(f"streamlit {st.__version__}")

def TTS(response):
    filename= "output.mp3"
    tts= gTTS(text=response, lang="ko")
    tts.save(filename)

    # 음원 파일 자도 재생
    with open(filename, "rb") as f:
        data= f.read()
        b64= base64.b64encode(data).decode()
        md= f"""
            <audio autoplay="True">
            <soure src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """

        st.markdown(md, unsafe_allow_html=True,)

    os.remove(filename)

def ask_gpt(prompt, model, apikey):
    client= openai.OpenAI(api_key= apikey)
    response= client.chat.completions.create(
        model= model,
        messages=prompt
    )

    gptResponse= response.choices[0].message.content
    return gptResponse
    
def STT(audio,apikey):
    filename= "input.mp3"
    audio.export(filename, format="mp3")
    

    # 음원 파일 열기
    audio_file= open(filename, "rb")

    # whisper 모델을 활용해 텍스트 열기
    client= openai.OpenAI(api_key= apikey)
    respons= client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    audio_file.close()

    # file deletion
    os.remove(filename)
    return respons.text

# main()함수
def main():
    st.set_page_config(
        page_title="음성 비서 Program",
        layout="wide"
    )

    #제목
    st.header("음성 비서 프로그램")

    #구분선
    st.markdown("----")

    #기본 설명
    with st.expander("음성비서 프로그램에 대하여", expanded=True):
        st.write("""
                    -음성 비서 프로그램의 UI는 Streamlit을 활용했습니다.\n
                    -STT는 OpenAI의 whisper AI를 활용했습니다.\n
                    -답변은 OpenAI의 GPT 모델을 활용했습니다.\n
                    -TTS는 구글의 gTTS를 활용했습니다.
                 """)
        st.markdown("")

    # session state 초기화
    if "chat" not in st.session_state:
        st.session_state["chat"] = []
    
    if "OPENAI_API" not in st.session_state:
        st.session_state["OPENAI_API"]=""
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "control":"You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]

    if "check_audio" not in st.session_state:
        st.session_state["check_reset"]= False
    
    with st.sidebar:

        #for openai 0.28
        # openai.api_key= st.text_input
        #Open AI API 키 입력하기
        st.session_state["OPENAI_API"]= st.text_input(label="OPENAI API 키",
             placeholder="Enter Your API Key", value="", type="password"                                         
            )
        
        st.markdown("---")

        model= st.radio(label="GPT 모델", options=["gpt-4", "gpt-3.5-turbo"])

        st.markdown("---")

        #reset button creation
        if st.button(label="초기화"):

            st.session_state["chat"]=[]
            st.session_state["messages"]= [{"role":"system", "content":"You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]
            st.session_state["check_reset"]= True
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("질문하기")

        # audio recording icon addition
        audio= audiorecorder("클릭하여 녹음하기","녹음 중....")
        if(audio.duration_seconds >0) and (st.session_state["check_reset"] == False):
            st.audio(audio.export().read())

            # 음원 파일에서 text 추출
            question= STT(audio, st.session_state["OPENAI_API"])

            # chatting을 시각화하기 위해 질문 내용 저장
            now= datetime.now().strftime("%H:%M")
            st.session_state["chat"]= st.session_state["chat"]+[("user", now, question)]

            # GPT model에 넣을 prompt를 위해 질문 내용 저장
            st.session_state["messages"]= st.session_state["messages"]+[{"role":"user","content":question}]

    with col2:
        st.subheader("질문/답변")
        if(audio.duration_seconds > 0) and (st.session_state["check_reset"]==False):
            response= ask_gpt(st.session_state["messages"],model, st.session_state["OPENAI_API"])

            # GPT 모델에 넣을 prompt를 위해 답변 내용 저장
            st.session_state["messages"]= st.session_state["messages"] + [{"role":"system", "content":response}]

            # chatting 시각화르 위한 답변 내용 저장
            now= datetime.now().strftime("%H:%M")
            st.session_state["chat"]= st.session_state["chat"]+[("user", now, response)]

            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'<div style="display:flex;align-items:center;">\
                             <div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:80px;">{message}</div>\
                             <div style="font-size:0.8rem;color:gray;">{time}</div></div>',\
                             unsafe_allow_html=True\
                             )
                    st.write("")
                else:
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;">\
                             <div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-right:80px;">{message}</div>\
                             <div style="font-size:0.8rem;color:gray;">{time}</div></div>',\
                             unsafe_allow_html=True\
                             )
                    st.write("")

            TTS(response)

          

if __name__=="__main__":
    main()
