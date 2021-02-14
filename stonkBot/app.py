# wersja 14.02.2021
import os
import time
from flask import Flask, render_template
from screener import Screener
from flask_apscheduler import APScheduler
import logging

os.environ['TZ'] = 'Poland'
time.tzset()

sched = APScheduler()
app = Flask(__name__)


class Config(object):
    SCHEDULER_API_ENABLED = True


czas = time.strftime('%d/%m/%Y -- %H:%M:%S CET')
stats = Screener().getData()


@sched.task('cron', id='update', hour=14)
def getData():
    global czas, stats
    czas = time.strftime('%d/%m/%Y -- %H:%M:%S CET')
    tabela = Screener()
    stats = tabela.getData()


@app.route('/')
def renderStats():
    return render_template('stats.html', data=stats.to_html(classes="table table-hover table-striped"),
                           time=czas)


@app.route('/about')
def renderAbout():
    return render_template('about.html')


if __name__ == '__main__':
    app.config.from_object(Config())
    sched.init_app(app)
    sched.start()
    app.run()
