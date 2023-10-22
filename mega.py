import os
import telebot

# Configure o token do seu bot aqui
BOT_TOKEN = '6695074982:AAF3dNWFRDHsMYh7mP1p64Kew1G_14tBs1w'

# Pasta para armazenar arquivos recebidos
FILE_FOLDER = 'arquivos'  # Crie essa pasta se ainda não existir

# Nome do arquivo de registro de arquivos
LOG_FILE = 'arquivos_log.txt'

# Inicializa o bot
bot = telebot.TeleBot(BOT_TOKEN)

# Trata o comando '/start'
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 'Bem-vindo ao seu bot de armazenamento de arquivos! Envie um arquivo para começar.')

# Trata o envio de imagens, GIFs e arquivos MP4
@bot.message_handler(content_types=['photo', 'document'])
def handle_media(message):
    user_id = message.from_user.id
    user_name = message.from_user.username if message.from_user.username else 'Unknown'
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        extension = 'jpg'
    elif message.content_type == 'document':
        file_id = message.document.file_id
        extension = message.document.file_name.split('.')[-1].lower()

    # Use o ID e o nome do usuário no nome do arquivo
    filename = f'{user_id}_{user_name}.{extension}'

    # Verifica se o arquivo já foi armazenado
    if not file_exists(filename):
        # Salva o arquivo localmente
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        with open(os.path.join(FILE_FOLDER, filename), 'wb') as new_file:
            new_file.write(file)

        # Registra o arquivo no arquivo de registro
        log_file = open(LOG_FILE, 'a')
        log_file.write(f'{filename}\n')
        log_file.close()

        bot.reply_to(message, 'Arquivo salvo com sucesso!')
    else:
        bot.reply_to(message, 'Você já enviou um arquivo anteriormente.')

# Trata o comando '/arquivos'
@bot.message_handler(commands=['arquivos'])
def handle_get_files(message):
    with open(LOG_FILE, 'r') as log_file:
        filenames = log_file.read().splitlines()

    if filenames:
        bot.send_message(message.chat.id, 'Aqui estão seus arquivos:')
        for filename in filenames:
            file_path = os.path.join(FILE_FOLDER, filename)
            with open(file_path, 'rb') as file:
                bot.send_document(message.chat.id, file)
    else:
        bot.send_message(message.chat.id, 'Você não tem arquivos armazenados.')

def file_exists(filename):
    with open(LOG_FILE, 'r') as log_file:
        filenames = log_file.read().splitlines()
        return filename in filenames

if __name__ == '__main__':
    if not os.path.exists(FILE_FOLDER):
        os.makedirs(FILE_FOLDER)
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()
    bot.polling()
	