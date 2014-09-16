#!/usr/bin/env python
__author__ = 'Mahmoud Adel <mahmoud.adel2@gmail.com>'
__version__ = 0.2

from BeautifulSoup import BeautifulSoup
from requests import session
import pynotify
import gobject
import subprocess
import time

baseurl = 'http://loadmeter.egyptera.org/MiniCurrentLoadClock3.aspx'
browser = 'firefox'
gridstatus = {
    'Images/c1.gif': 'Safe',
    'Images/c2.gif': 'Warning',
    'Images/c3.gif': 'Critical'
}
oldstatus = 'Unknown'

def fetchdata(targetpage):
    try:
        with session() as c:
            request = c.get(targetpage, timeout=5)
            rawtext = request.text
            soup = BeautifulSoup(rawtext)
        global myhtml
        myhtml = soup.findAll('img', {'id': "FormView1_Imagexx"})
    except KeyboardInterrupt:
        exit(0)
    except:
        print '[ %s ] Could not fetch data, sleeping for 5 seconds...' % (int(time.time()))
        time.sleep(5)
        pass

def desktopnotify(status, header):
    pynotify.init('power-grid-notify')
    global loop
    loop = gobject.MainLoop()
    notify = pynotify.Notification("",
     '''
     <b><i>%s</i></b>
     ''' % (header))
    notify.set_urgency(pynotify.URGENCY_CRITICAL)
    notify.set_timeout(pynotify.EXPIRES_NEVER)
    notify.add_action('Open', 'Open Grid Status URL', openstatusurl)
    notify.connect("closed", ignoredaction)
    notify.show()
    loop.run()

def getgridstatus():
    fetchdata(baseurl)
    try:
        for tag in myhtml:
            statusdata = dict(tag.attrs)
        status = statusdata['src']
        return gridstatus[status]
    except:
        pass

def openstatusurl(action, label):
    subprocess.call('%s %s' % (browser, baseurl), shell=True)
    action.close()
    global loop
    loop.quit()

def ignoredaction(notification):
    notification.close()
    global loop
    loop.quit()

def main():
    global oldstatus
    currentstatus = getgridstatus()
    if currentstatus != oldstatus:
        if currentstatus == 'Safe':
            oldstatus = currentstatus
            desktopnotify(currentstatus, 'Power Grid Status now is: <b><span color="green">%s</span></b>' % (currentstatus))
        elif currentstatus == 'Warning':
            oldstatus = currentstatus
            desktopnotify(currentstatus, 'Power Grid Status now is: <b><span color="orange">%s</span></b>' % (currentstatus))
        elif currentstatus == 'Critical':
            oldstatus = currentstatus
            desktopnotify(currentstatus, 'Power Grid Status now is: <b><span color="red">%s</span></b>' % (currentstatus))

if __name__ == '__main__':
    try:
        while True: main()
    except KeyboardInterrupt:
        exit(0)
