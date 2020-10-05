from telegram.ext.commandhandler import CommandHandler
from telegram.ext.updater import Updater
from telegram.ext.dispatcher import Dispatcher
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import MessageHandler, Filters
from telegram.bot import Bot
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.replykeyboardremove import ReplyKeyboardRemove
from packages import dialogflow_endpoint
from telegram import KeyboardButton
import configparser as cfg
import os
import random


class Server:
    def __init__(self):
        """Initialize the Server object for the bot
        TOKEN -> API key of the bot
        """
        self.TOKEN = self.read_token_from_config_file(
            './configfiles/config.cfg')
        self.updater = Updater(self.TOKEN, use_context=True)
        self.dispatcher: Dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dialogflow = dialogflow_endpoint.DialogFlowWrapper()
        self.dispatcher.add_handler(CommandHandler("end", self.end))
        self.dispatcher.add_handler(
            MessageHandler(Filters.all, self.make_response, pass_user_data=True))

    def read_token_from_config_file(self, config):
        """ Reads the token from the config.cfg file
        config -> Location of the config.cfg file
        """
        parser = cfg.ConfigParser()
        parser.read(config)
        return parser.get('creds', 'token')

    def prefix_reply(self, responses):
        """Returns a random string from a given set of responses"""
        pos = random.randint(0, len(responses) - 1)
        return responses[pos]

    def start(self, update: Update, context: CallbackContext):
        """Callback for start command"""
        bot: Bot = context.bot
        responses = ['Hi ', 'Hello ', 'Whats up ', 'How are you ']
        reply = self.prefix_reply(responses) + \
            update.message.from_user.first_name
        bot.send_message(chat_id=update.effective_chat.id, text=reply)
        responses = ['😌', '🙂']
        reply = self.prefix_reply(responses)
        bot.send_message(chat_id=update.effective_chat.id, text=reply)

    def end(self, update: Update, context: CallbackContext):
        """Callback for end command"""
        bot: Bot = context.bot
        responses = ['Nice talking you ', 'See you soon ',
                     'Hope you liked it ', 'Thank you for your time ']
        reply = self.prefix_reply(responses) + \
            update.message.from_user.first_name
        bot.send_message(chat_id=update.effective_chat.id, text=reply)
        responses = ['👋', '🖖', '🙏']
        reply = self.prefix_reply(responses)
        bot.send_message(chat_id=update.effective_chat.id, text=reply)

    def respond_text(self, update: Update, context: CallbackContext):
        """Respond to user with a text reply"""
        bot: Bot = context.bot
        parent_dir = os.getcwd()
        dir_name = os.path.join(parent_dir, 'logfiles')
        file_name = 'messages.log'
        reply = self.dialogflow.process_input(update.message.text, update.message.chat_id)
        log_reply = reply.replace('\n', ' ')
        log_reply = log_reply.replace(',', ' ')
        line = f'{update.message.date}, {update.message.from_user.first_name}, {update.message.from_user.last_name}, {update.message.chat_id}, {update.message.text}, {log_reply}\n'
        with open(os.path.join(dir_name, file_name), 'a') as file_pointer:
            file_pointer.writelines(line)
        bot.send_message(chat_id=update.message.chat_id, text=reply)

    def respond_images(self, update: Update, context: CallbackContext):
        """Respond to user with a image reply"""

    def respond_video(self, update: Update, context: CallbackContext):
        """Respond to user with a video reply"""

    def respond_sticker(self, update: Update, context: CallbackContext):
        """Respond to user with a sticker reply"""
        bot: Bot = context.bot
        reply = "Wait there!! I am still learning"
        bot.send_message(chat_id=update.effective_chat.id, text=reply)
        responses = ['🙄', '🤔', '😬', '😐']
        reply = self.prefix_reply(responses)
        bot.send_message(chat_id=update.effective_chat.id, text=reply)
        reply = 'This is all I can understand ' + update.message.sticker.emoji
        bot.send_message(chat_id=update.effective_chat.id, text=reply)

    def reply_to_messages(self, update: Update, context: CallbackContext):
        """Determine message type and then reply accordingly"""
        bot: Bot = context.bot
        if update.message.text:
            self.respond_text(update, context)
        elif update.message.video:
            self.respond_video(update, context)
        elif update.message.photo:
            self.respond_images(update, context)
        elif update.message.sticker:
            self.respond_sticker(update, context)
        elif update.message.location:
            print("HI location detected")
        elif update.message.contact:
            print("contackt kjd")

    def make_response(self, update: Update, context: CallbackContext):
        """Callback for making reponses to the user"""
        bot: Bot = context.bot
        self.reply_to_messages(update, context)

    def start_server(self):
        self.updater.start_polling()


if __name__ == "__main__":
    parent_dir = os.getcwd()
    dir_name = os.path.join (parent_dir, 'logfiles')
    file_name = 'messages.log'
    with open(os.path.join(dir_name, file_name), 'w') as file_pointer:
        file_pointer.writelines(f'date, first_name, last_name, chat_id, message, reply\n')
    server = Server()
    print(f'Server Started')
    server.start_server()
