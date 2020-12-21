import flask
from flask import request, redirect, flash
from flask_simplelogin import SimpleLogin, login_required, url_for
import os
from telebot import types
import config
from bot_handlers import bot
from data_providers.bot_users_provider import BotUsersProvider
from data_providers.question_count_report_provider import QuestionCountReportProvider
from data_providers.questions_queue_info_provider import QuestionQueueInfoProvider
from tools.questions_queue_item_deleter import QuestionQueueItemDeleter
from repositories.bot_users_repository import BotUsersRepository
from repositories.question_queue_repository import QuestionQueueRepository
from repositories.post_archive_repository import PostsArchiveRepository


server = flask.Flask(__name__, template_folder='templates')

server.config['SECRET_KEY'] = config.SECRET
server.config['SIMPLELOGIN_USERNAME'] = config.ADMIN_USERNAME
server.config['SIMPLELOGIN_PASSWORD'] = config.ADMIN_PASSWORD
SimpleLogin(server)


@server.route('/' + config.TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([types.Update.de_json(flask.request.stream.read().decode('utf-8'))])
    return '!', 200


@server.route('/', methods=['GET'])
def index():
    bot.remove_webhook()
    bot.set_webhook(url='https://{}.herokuapp.com/{}'.format(config.APP_NAME, config.TOKEN))
    return 'Hello from Lapochka!', 200


@server.route('/admin', methods=['GET'])
@login_required
def admin():
    return redirect(url_for('admin_user_information'))


@server.route('/admin/user-information', methods=['GET'])
@login_required
def admin_user_information():
    provider = BotUsersProvider(BotUsersRepository())
    users = provider.get()
    return flask.render_template('user_information.html', users=users)


@server.route('/admin/message', methods=['GET', 'POST'])
@login_required
def admin_send_message():
    if request.method == 'POST':
        user_ids = request.form.getlist('user_id')
        text = request.form['text']
        for user_id in user_ids:
            try:
                bot.send_message(user_id, text)
            except:
                pass
        flash('success')
        return redirect(url_for('admin_send_message'))

    provider = BotUsersProvider(BotUsersRepository())
    users = provider.get()
    return flask.render_template('send_message.html', users=users)


@server.route('/admin/questions-queue', methods=['GET', 'POST'])
@login_required
def admin_questions_queue():
    if request.method == 'POST':
        question_deleter = QuestionQueueItemDeleter(QuestionQueueRepository())
        question_deleter.delete(request.form['id'])
        flash('success')
        return redirect(url_for('admin_questions_queue'))

    provider = QuestionQueueInfoProvider(QuestionQueueRepository())
    queue_info = provider.get()
    return flask.render_template('questions_queue.html', queue_info=queue_info)


@server.route('/admin/statistic', methods=['GET'])
@login_required
def admin_post_statistics():
    provider = QuestionCountReportProvider(PostsArchiveRepository())
    data = provider.get()
    return flask.render_template('post_statistics.html', data=data)


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
