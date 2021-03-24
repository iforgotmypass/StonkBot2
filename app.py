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
statsOld = Screener().getData()
scr = ScreenerAPI()
stats = scr.getHTML()



@sched.task('cron', id='update', hour=13, minute=00)
def getData():
    global czas, stats
    czas = time.strftime('%d/%m/%Y -- %H:%M:%S UTC')
    tabela = ScreenerAPI()
    stats = tabela.getHTML()


@app.route('/')
def renderStats():
    return render_template('stats.html', data=stats, time=czas,
                                         simple='stonksSimple.csv',
                                         full='stonksFull.csv')


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


@app.route('/old')
def renderStatsOld():
    return render_template('stats.html', data=statsOld.to_html(classes="table table-hover table-striped",
                                                               justify='center'), time=czas,
                                                               simple='stonksSimpleOld.csv',
                                                               full='stonksFullOld.csv')


if __name__ == '__main__':
    app.config.from_object(Config())
    sched.init_app(app)
    sched.start()
    app.run()
