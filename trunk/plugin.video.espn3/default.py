#!/usr/bin/python
#
#
# Written by Ksosez, with massive help from Bluecop
# Released under GPL(v2)

import urllib, urllib2, xbmcplugin, xbmcaddon, xbmcgui, string, htmllib, os, platform, random, calendar, re
from datetime import date, timedelta
from BeautifulSoup import BeautifulStoneSoup as Soup


## Get the settings

selfAddon = xbmcaddon.Addon(id='plugin.video.espn3')
cbrowser=selfAddon.getSetting('browser')
if cbrowser is '' or cbrowser is None:
    # Default to Firefox
    cbrowser = "Firefox"
usexbmc = selfAddon.getSetting('watchinxbmc')
defaultimage = 'special://home/addons/plugin.video.espn3/icon.png'
if usexbmc is '' or usexbmc is None:
    usexbmc = True

def CATEGORIES():
    mode = 1
    addDir('Live', 'http://espn.go.com/espn3/feeds/live', mode, defaultimage)
    addDir('Replay - By Sport', 'http://espn3.passportproject.org/', 2,
           defaultimage)
    addDir('Replay - Previous 10 Days', 'http://espn3.passportproject.org/10_days.xml', mode,
           defaultimage)
    addDir('Upcoming', 'http://sports-ak.espn.go.com/espn3/feeds/upcoming', mode,
           defaultimage)

   # print pluginhandle
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def INDEX(url):
    if "upcoming" in url or "replay" in url:
        addDir("Today", "", 1, defaultimage)
    html = get_html(url)
    soup = Soup(html)
    tomadded = 0 # set for headers in indexing later
    nextdayadded = 0
    savedate = date.today()
    for event in soup.findAll('event'):
        msg_attrs = dict(event.attrs)
        eventname = str(event.find('name'))
        if len(eventname) < 5:  # Ignore the first instance which is broken
            pass
        else:
            if "upcoming" in url or "live" in url:
                reventname = string.split(string.split(eventname, "[")[2], "]]")[0]
            else:
                reventname = string.split(string.split(eventname, ">")[1], "<")[0]
            eventid = str(msg_attrs[u'id'])
            league = string.split(string.split(str(event.find('league')), ">")[1], "<")[0]
            sport = event.find('sport')
            eventedt =string.split(string.split(str(event.find('starttime')),">")[1], "<")[0]
            eyear = eventedt[0:4]
            emonth = eventedt[4:6]
            eday = eventedt[6:8]
            etime = eventedt[8:12]
            if "upcoming" in url:
                today = date.today()
                edate = date(int(eyear),int(emonth),int(eday))
                tom = today.replace(day=today.day+1)
                nextday = today.replace(day=today.day+2)
                diffdate = date(int(eyear),int(emonth),int(eday)) - date.today()

                if edate == today:
                    pass
                elif  edate == tom and tomadded != 1:
                    addDir("Tomorrow", "special://home/addons/plugin.video.espn3/icon.png", 1, defaultimage)
                    tomadded =  1
                elif edate == nextday and nextdayadded != 1:
                    addDir(nextday.strftime("%A - %B %d, %Y"), "special://home/addons/plugin.video.espn3/icon.png", 1, defaultimage)
                    nextdayadded = 1
                else:
                    pass

                if diffdate < timedelta(days=3):
                    # Only print the next 2 days
                    sport = string.split(string.split(str(sport), ">")[1], "<")[0]
                    etime = ampm(etime)
                    name = etime + " EDT" + ":" + reventname + ":" + sport + ":" + league
                    rurl = "http://espn.go.com/espn3/player?id=%s&league=%s" % (eventid, urllib.quote(league))
                    print rurl
                    mode = 4
                    rthumbnail = event.find('thumbnail')
                    sthumbnail = string.split(string.split(str(rthumbnail), "<small>")[1], "</small>")[0]
                    sthumbnail = string.split(string.split(sthumbnail, "[")[2], "]]")[0]
                    if sthumbnail < 5:
                        thumbnail = "special://home/addons/plugin.video.espn3/icon.png"
                    else:
                        thumbnail = sthumbnail
                    addLink(name, rurl, mode, thumbnail)
                else:
                    pass
            elif "live" in url:
                 ## Live
                sport = string.split(string.split(str(sport), ">")[1], "<")[0]
                etime = ampm(etime)
                name = etime + " EDT:" + reventname + ":" + sport + ":" + league
                rurl = "http://espn.go.com/espn3/player?id=%s&league=%s" % (eventid, urllib.quote(league))
                print rurl
                mode = 4
                rthumbnail = event.find('thumbnail')
                sthumbnail = string.split(string.split(str(rthumbnail), "<small>")[1], "</small>")[0]
                sthumbnail = string.split(string.split(sthumbnail, "[")[2], "]]")[0]
                if sthumbnail < 5:
                    thumbnail = "special://home/addons/plugin.video.espn3/icon.png"
                else:
                    thumbnail = sthumbnail
                addLink(name, rurl, mode, thumbnail)
            else:
                # Everything else to Index
                edate = date(int(eyear),int(emonth),int(eday))
                #diffdate = date.today() - date(int(eyear),int(emonth),int(eday))
                if "10_days" in url:
                    if edate == savedate:
                        pass
                    elif edate != savedate:
                        try:
                            savedate = savedate.replace(day=savedate.day-1)
                        except ValueError:
                            try:
                                savedate = savedate.replace(month=savedate.month-1)
                                savedate = savedate.replace(day=calendar.monthrange(savedate.year,savedate.month)[1])
                            except ValueError:
                                savedate = savedate.replace(year=savedate.year-1)
                                savedate = savedate.replace(month=12)
                                savedate = savedate.replace(day=31)

                        addDir(savedate.strftime("%A - %B %d, %Y"), "special://home/addons/plugin.video.espn3/icon.png", 1, defaultimage)

                    else:
                        pass
                else:
                    if savedate != edate:
                        addDir(edate.strftime("%A - %B %d, %Y"), "special://home/addons/plugin.video.espn3/icon.png", 1, defaultimage)
                    else:
                        pass
                    savedate = edate
                sport = string.split(string.split(str(sport), ">")[1], "<")[0]
                etime = ampm(etime)
                name = etime + " EDT" + ":" + reventname + ":" + sport + ":" + league
                rurl = "http://espn.go.com/espn3/player?id=%s&league=%s" % (eventid, urllib.quote(league))
                print rurl
                mode = 4
                rthumbnail = event.find('thumbnail')
                sthumbnail = string.split(string.split(str(rthumbnail), "<small>")[1], "</small>")[0]
                #sthumbnail = string.split(string.split(sthumbnail, "[")[2], "]]")[0]
                if sthumbnail < 5:
                    thumbnail = "special://home/addons/plugin.video.espn3/icon.png"
                else:
                    thumbnail = sthumbnail
                addLink(name, rurl, mode, thumbnail)


def REPLAYBYSPORT(url):
    html = get_html(url)
    match = re.compile('<img src="/icons/text.gif" alt="\[TXT\]"> <a href="(.+?)">(.+?)</a>').findall(html)
    for gurl,name in match:
        if gurl == '10_days.xml':
            pass
        else:
            realurl = "http://espn3.passportproject.org/%s" % gurl
            name = string.split(unescape(name), ".")[0]
            name = name.replace("_", " ")
            name = name.title()
            mode = 1
            addDir(name,realurl, mode, defaultimage)
    
            


def PLAY(url):
    #Make startupevent url from page url
    print url
    startUrl = 'http://espn.go.com/espn3/feeds/startupEvent?'+url.split('?')[1]+'&gameId=null&sportCode=null'
    #Get eventid, bamContentId, and bamEventId from starturl data
    html = get_html(startUrl)
    if html == False:
        dialog = xbmcgui.Dialog()
        dialog.ok("Failure to Launch URL", "Unable to launch video feed most likely", "because you already requested this feed.", "Please wait a while and try again.")
    else:
        event = Soup(html)('event')[1]
        eventid = event['id']
        bamContentId = event['bamcontentid']
        bamEventId = event['bameventid']


        #Make identityPointId from userdata
        userdata = 'http://broadband.espn.go.com/espn3/auth/userData'
        html = get_html(userdata)
        soup = Soup(html)
        affiliateid = soup('name')[0].string
        swid = soup('personalization')[0]['swid']
        identityPointId = affiliateid+':'+swid

        #Use eventid, bamContentId, bamEventId, and identityPointId to get smil url and auth data
        authurl = 'https://espn-ws.bamnetworks.com/pubajaxws/bamrest/MediaService2_0/op-findUserVerifiedEvent/v-2.1'
        authurl += '?platform=WEB_MEDIAPLAYER'
        authurl += '&playbackScenario=FMS_CLOUD'
        authurl += '&eventId='+bamEventId
        authurl += '&contentId='+bamContentId
        authurl += '&rand='+str(random.random())+'0000'
        authurl += '&cdnName=PRIMARY_AKAMAI'
        authurl += '&partnerContentId='+eventid
        authurl += '&identityPointId='+identityPointId
        authurl += '&playerId=domestic'
        html = get_html(authurl)
        smilurl = Soup(html).findAll('url')[0].string
        auth = smilurl.split('?')[1]

        #Grab smil url to get rtmp url and playpath
        html = get_html(smilurl)
        soup = Soup(html)
        print soup.prettify()
        rtmp = soup.findAll('meta')[0]['base']
        #live selects stream quality
        #200000,400000,800000,1200000,1800000
        #     0,     1,     2,      3,      4
        #     Lowest, Low,   Medium,  High, Highest
        #Change the [4] to 0-4 to change the bitrate
        if 'ondemand' in rtmp:
            replayquality = selfAddon.getSetting('replayquality')
            playpath = soup.findAll('video')[int(replayquality)]['src']
            finalurl = rtmp+'/?'+auth+' playpath='+playpath
        elif 'live' in rtmp:
            livequality = selfAddon.getSetting('livequality')
            playpath = soup.findAll('video')[int(livequality)]['src']
            finalurl = rtmp+' live=1 playlist=1 subscribe='+playpath+' playpath='+playpath+'?'+auth
        item = xbmcgui.ListItem(path=finalurl)
        return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

def PLAYBROWSER(url):
    print "Play URL:%s" % url
    psystem = platform.system()
    if cbrowser == "Chrome":
        if psystem == "Darwin":
            cmd = 'open -a /Applications/Chrome.app %s' % url
        elif psystem == "Linux":
            cmd = "/usr/bin/google-chrome  %s" % url
        elif psystem == "Windows":
            cmd = "chrome.exe %s" % url
        else:
            print "Aint no browser here"
    else:
        if psystem == "Darwin":
            cmd = 'open -a /Applications/Firefox.app %s' % url
        elif psystem == "Linux":
            cmd = "/usr/bin/firefox %s" % url
        elif psystem == "Windows":
            cmd = '"C:\Program Files\Mozilla Firefox\firefox.exe" %s' % url
        else:
            print "Aint no browser here"

    os.system(cmd)

#	subprocess.call(['open -a /Applications/Firefox.app'])


def get_html(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    try:
        response = urllib2.urlopen(req)
        html = response.read()
        response.close()
    except urllib2.HTTPError:
        response = False
        html = False
    return html

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param


def addLink(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()

def ampm(etime):
    if int(etime) >= 1300:
        etime = int(etime) - 1200
        etime = str(etime) + "PM"
    elif 1200 <= int(etime) < 1300:
        etime = str(etime) + "PM"
    else:
        etime = etime + "AM"
    return etime

params = get_params()
url = None
name = None
mode = None
cookie = None

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    name = urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass

print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)

if mode == None or url == None or len(url) < 1:
    print "Generate Main Menu"
    CATEGORIES()
elif mode == 1:
    print "Indexing Videos"
    INDEX(url)
elif mode == 2:
	print "Indexing Replay by Sport"
	REPLAYBYSPORT(url)

elif mode == 4:
    print "Play Video"
    if usexbmc == True or usexbmc == "true":
        PLAY(url)
    else:
        PLAYBROWSER(url)

#elif mode =="categories":
#    print "Category: Categories"
#    CATEGORIES(url)
##elif mode =="search":
##   print "Category: Search"
#  SEARCH(url, mode)
#else:
#    print ""+url
#   INDEX(url)



xbmcplugin.endOfDirectory(int(sys.argv[1]))