# save as print_group_messages.py
import argparse
from dingtalk_stream import AckMessage
import dingtalk_stream
import requests
import smtplib
import ssl
from email.mime.text import MIMEText
from datetime import datetime

# 必填环境变量：
# DINGTALK_APP_KEY, DINGTALK_APP_SECRET, DINGTALK_CHAT_ID
# MAIL_FROM, MAIL_PASSWORD, MAIL_TO
# QQ邮箱 SMTP 默认: smtp.qq.com:465

DINGTALK_APP_KEY = "dingmgrjjplhkjagnxon"
DINGTALK_APP_SECRET = "CEhY8woh2igFpz1gqaFweW47_Qn7UZ1ecKiaWJYH0E69DeYGde7wDmHn4lseVqfr"
DINGTALK_CHAT_ID = "chatef9e17d706a00e0bc7dd634dea8771e5"

MAIL_FROM = "329372022@qq.com"
MAIL_PASSWORD = "wqxeuvbrxfyvbjcf"  # QQ邮箱为“授权码”
MAIL_TO = "329372022@qq.com"
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465

def send_mail(subject: str, body: str):
    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = MAIL_FROM
    msg["To"] = MAIL_TO
    msg["Subject"] = subject

    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=15, context=context)
        try:
            server.login(MAIL_FROM, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, [MAIL_TO], msg.as_string())
        finally:
            try:
                server.quit()
            except Exception:
                # 关闭阶段报错忽略
                pass
    except Exception as ssl_err:
        # 仅使用 SSL: 发送或关闭阶段异常均忽略，不中断流程
        print(f"SMTP 发送失败已忽略: SSL错误={ssl_err!r}")
    return

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--client_id", required=True)
    p.add_argument("--client_secret", required=True)
    return p.parse_args()

class PrintGroupMsgHandler(dingtalk_stream.CallbackHandler):
    async def process(self, callback: dingtalk_stream.CallbackMessage):
        msg = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
        # 只打印群聊(conversationType == '2')
        if msg.conversation_type == '2':
            text = None
            if msg.message_type == 'text' and msg.text:
                text = msg.text.content
            elif msg.message_type == 'richText':
                text = "\n".join(msg.get_text_list() or [])
            body_text = f"[群:{msg.conversation_title}] {msg.sender_nick}: {text}"
            print(body_text)
            subject = "钉钉群聊天内容"
            send_mail(subject, body_text)
            print("邮件已发送")
        return AckMessage.STATUS_OK, "OK"

def main():
    print("start")
    args = parse_args()
    cred = dingtalk_stream.Credential(args.client_id, args.client_secret)
    client = dingtalk_stream.DingTalkStreamClient(cred)
    client.register_callback_handler(dingtalk_stream.ChatbotMessage.TOPIC, PrintGroupMsgHandler())
    client.start_forever()

if __name__ == "__main__":
    main()