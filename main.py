from flask import Flask, request, abort
 
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os
import wikipedia
 
app = Flask(__name__)
 
#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
 
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

wikipedia.set_lang("ja")
 
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
 
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
 
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
 
    return 'OK'
 
 
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
    
    try:
        keyword = wikipedia.search(event.message.text)[0]
        response = wikipedia.page(keyword).summary
        
    except wikipedia.exceptions.DisambiguationError as e:
        response = "次の検索候補から、再度送信して下さい。\n"
        for option in e.options:
            response += option + "\n"
        
    except:
        response = "wikipediaのページにヒットしませんでした...。\nキーワードを変えて、もう一度お試し下さい。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response))
 
 
if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)