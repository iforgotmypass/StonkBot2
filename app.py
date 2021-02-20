# wersja 17.02.2021
import os
import time
from flask import Flask, render_template
from screenerAPI import ScreenerAPI
from screener import Screener
from flask_apscheduler import APScheduler
import logging

sched = APScheduler()
app = Flask(__name__)


class Config(object):
    SCHEDULER_API_ENABLED = True


czas = time.strftime('%d/%m/%Y -- %H:%M:%S UTC')
stats = ScreenerAPI().getHTML()
statsOld = Screener().getData()


@sched.task('cron', id='update', hour=13, minute=00)
def getData():
    global czas, stats
    czas = time.strftime('%d/%m/%Y -- %H:%M:%S UTC')
    tabela = ScreenerAPI()
    stats = tabela.getHTML()


@app.route('/')
def renderStats():
    return render_template('stats.html',
                           data=stats,
                           time=czas)


@app.route('/about')
def renderAbout():
    return render_template('about.html')


@app.route('/help')
def renderHelp():
    return render_template('help.html')


@app.route('/archive')
def renderArchive():
    stonklist = os.listdir('static/archive')
    return render_template('archive.html', len=len(stonklist), stonklist=stonklist)


if __name__ == '__main__':
    app.config.from_object(Config())
    sched.init_app(app)
    sched.start()
    app.run()
