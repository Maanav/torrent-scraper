import requests
from lxml import html
import re

def sendHttpRequest(url):
    print "[] Sending HTTPS request to "+str(url)
    page = requests.get(url)
    content = html.fromstring(page.content)
    print "[] Received content"
    return content

def parseByXpath(HtmlContent,xpath):
    return HtmlContent.xpath(xpath)

def searchContent(showDetails,webSiteData):
    if(showDetails['uploader']!=None):
        uploaderMatch = False
        episodeMatch = False
        i = 0
        searchLimit = 30
        season=format(showDetails['season'],'02d')
        episode=format(showDetails['episode'],'02d')
        search_string='S'+str(season)+'E'+str(episode)
        torrent_name = parseByXpath(webSiteData,'//*[@id="searchResult"]/tr/td/div/a/text()')
        while(episodeMatch == False):
            if(i > 29):
                break;
            match = re.search(str(search_string),torrent_name[i])
            match2= re.search(str(showDetails['uploader']),torrent_name[i])
            episodeUploaderXpath = '//*[@id="searchResult"]/tr['+str(i+1)+']/td[2]/font/a/text()'
            episodeUploader = parseByXpath(webSiteData,episodeUploaderXpath)
            if(len(episodeUploader)==0):
                episodeUploader = 'Anonymous'
            else:
                episodeUploader = episodeUploader[0]
            if (episodeUploader == showDetails['uploader'] or bool(showDetails['uploader']) == False):
                uploaderMatch = True
            else:
                uploaderMatch = False
            print '['+str(i)+'] Searching '+str(search_string)+' by '+str(showDetails['uploader'])+' in '+str(torrent_name[i])
            i = i + 1
            if ((match !=None)):
                if (match.group(0)==search_string and uploaderMatch == True):
                    print 'Matched search'
                    print '[] Found at node '+str(i)
                    episodeMatch=True
                    break
        if(episodeMatch == True):
            print "[] Found. Parsing Details"
            episodeNode = i
            episodeNameXpath = '//*[@id="searchResult"]/tr['+str(episodeNode)+']/td[2]/div/a/text()'
            episodeName = parseByXpath(webSiteData, episodeNameXpath)[0]
            episodeMagnetXpath = '//*[@id="searchResult"]/tr['+str(episodeNode)+']/td[2]/a[1]/@href'
            magnetLink = parseByXpath(webSiteData,episodeMagnetXpath)[0]
            episodeUploaderXpath = '//*[@id="searchResult"]/tr['+str(episodeNode)+']/td[2]/font/a/text()'
            episodeUploader = parseByXpath(webSiteData,episodeUploaderXpath)[0]
            episodeDetailsXpath =  '//*[@id="searchResult"]/tr['+str(episodeNode)+']/td[2]/font/text()'
            episodeDetails = parseByXpath(webSiteData,episodeDetailsXpath)[0]+str(episodeUploader)
            episodeSeedsXpath = '//*[@id="searchResult"]/tr['+str(episodeNode)+']/td[3]/text()'
            episodeSeeds = parseByXpath(webSiteData,episodeSeedsXpath)[0]
            episodeLeechXpath = '//*[@id="searchResult"]/tr['+str(episodeNode)+']/td[4]/text()'
            episodeLeech = parseByXpath(webSiteData,episodeLeechXpath)[0]
            episodeUploaderXpath = '//*[@id="searchResult"]/tr['+str(episodeNode)+']/td[2]/font/a/text()'
            episodeUploader = parseByXpath(webSiteData,episodeUploaderXpath)[0]
            episodeDetails = {
                'name' : episodeName,
                'link' : magnetLink,
                'details' : episodeDetails,
                'seeds' : episodeSeeds,
                'leech' : episodeLeech,
                'uploader' : episodeUploader
            }
        if(episodeMatch == True):
            return episodeDetails
        else:
            return None
  ##  //*[@id="searchResult"]/tbody/tr[6]/td[2]/font/text()
  ##  //*[@id="searchResult"]/tbody/tr[7]/td[2]/div/a
    ## //*[@id="searchResult"]/tbody/tr[22]/td[2]/font/i

def searchEpisode(showName,uploader,season,episode):
    gotEpisode = False
    page = 0
    while(gotEpisode == False):
        print "Generating Request url for page "+str(page)
        name=showName.split()
        url = 'https://pirateproxy.pe/search/'
        for i in range(0,len(name)):
            if(i!=(len(name)-1)):
                url = url + str(name[i]) + "%20"
            else:
                url = url + str(name[i])
        url = url + "/"+str(page)+"/99/0"
        print url
        websiteData = sendHttpRequest(url)
        page = page + 1
        showDetails = {'name':showName,'season':season,'episode':episode,'uploader':uploader}
        searchResult = searchContent(showDetails,websiteData)
        if(searchResult!=None):
            gotEpisode = True
        if(page == 5):
            return {
                'name' : 'Not Found',
                'link' : 'Not Found',
                'details' : 'Not Found',
                'seeds' : 'Not Found',
                'leech' : 'Not Found',
                'uploader' : 'Not Found'
            }
    return searchResult

def sendJSONtoDeluge(link,serverAddress,port,password):
    link="\""+str(link)+"\""
    deluge = requests.session()
    JSONString ='{"method": "auth.login", "params": ["'+str(password)+'"], "id": 1}'
    postRequest = "http://"+serverAddress+":"+port+"/json"
    response = deluge.post(postRequest,data=JSONString)
    JSONString = str('{"method": "core.add_torrent_magnet", "params":[')+link+str(', {}], "id": 2}')
    print response.headers
    response = deluge.post(postRequest,data=JSONString)
    print response.headers
matchedEpisodes=[]

#print searchEpisode("Modern Family","ettv",7,1)

for i in range(0,21):
    episode = searchEpisode("Modern Family","",7,i+1)
    matchedEpisodes.append(episode)


for i in range(0,21):
    if(str(matchedEpisodes[i]['link']) != 'Not Found'):
        sendJSONtoDeluge(str(matchedEpisodes[i]['link']),"192.168.0.104","8112","9324651015")
