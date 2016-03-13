if __name__ == "__main__":
    main()

def getgametimes(urlname):
    from lxml import html
    import requests 
    import scorescraper
    from datetime import datetime, timedelta
    page = requests.get(urlname)
    page.content2 =  page.content.replace("\\", "")
    tree=html.fromstring(page.content2) 
    gametime = tree.xpath('//tr[@class="game pre link"]//span[@class="time"]/text()')
    if not gametime:
        gametime = tree.xpath('//span[@class="time"]/text()')
    gametime2 = [x[0:-4] for x in gametime]
    URLs = tree.xpath('//tr[@class="game pre link"]//td[@class="score"]//@href')
    if not URLs:
        URLs = tree.xpath('//td[@class="score"]//@href')
    time_deltas = [(datetime.strptime(x, '%I:%M %p')-datetime.utcnow()+timedelta(hours=4)).seconds/60 for x in gametime2]
#   time_deltas2 = list(scorescraper.rename_duplicates(time_deltas))
    return (time_deltas,URLs)    
#   return (time_deltas2,URLs)    
    
def getcbbthread(urlname,secret,token):
    from datetime import datetime
    from lxml import html
    import pandas as pd
    import requests 
    import requests.auth
    import csv
    import scorescraper
    import OAuth2Util
    from StringIO import StringIO
    page = requests.get('http://sports.yahoo.com'+urlname)
    page.content2 =  page.content.replace("\\", "")
    tree=html.fromstring(page.content2)     
    
    pagerankmain = requests.get('http://cbbpoll.com/')
    pagerankmain.content2 =  pagerankmain.content.replace("\\", ",")
    treerankmain=html.fromstring(pagerankmain.content2)
    currenturl = 'http://cbbpoll.com' + treerankmain.xpath('//div[@class="row"]//@href')[0]
    
    pagerankings = requests.get(currenturl)
    pagerankings.content1 =  pagerankings.content.replace("\\", "")
    pagerankings.content2 =  pagerankings.content1.replace("|", ",")
    treerankings=html.fromstring(pagerankings.content2) 

    df1=pd.read_csv('https://raw.githubusercontent.com/airjesse123/GameThreadGenerator/master/TeamLookup.csv', sep=',',header=None)
    df = df1.fillna('')
    rank = 'rank,reddit_name,name,votes\n'+'\n'.join(treerankings.xpath('//div[@class="modal-body"]/textarea/text()')[0].splitlines()[3:28])
    rankdf = pd.read_csv(StringIO(rank), dtype=object)  

    visiting_team_name = tree.xpath('//div[@class="team away"]/div[@class="team-info"]/div[@class="name"]/a/text()')[0].lstrip('1234567890()').lstrip()
    visiting_yahoo_name = tree.xpath('//div[@class="team away"]/div[@class="team-info"]/div[@class="name"]//@href')[0][13:-1]
    try:
        visiting_reddit_name = df[df[1]==visiting_yahoo_name].iloc[0][2]
    except:
        visiting_reddit_name = ''
    try:
        visiting_flair = df[df[1]==visiting_yahoo_name].iloc[0][6]
    except:
        visiting_flair = ''
    try:
        visiting_radio_url = df[df[1]==visiting_yahoo_name].iloc[0][4]
    except:
        visiting_radio_url = ''
    try:
        visiting_subreddit = df[df[1]==visiting_yahoo_name].iloc[0][5]
    except:
        visiting_subreddit = ''
    try:	
#       visiting_rank = rankdf[rankdf.reddit_name == '[](/' + visiting_reddit_name + ')'].iloc[0][0] + ' '
        visiting_rank = '(' + tree.xpath('//div[@class="team away"]/div[@class="team-info"]/div[@class="name"]/a/text()')[0].rstrip(' ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.&-()\'').lstrip('(') + ' Seed) '
    except:
        visiting_rank = ''
    #visiting_team_record = tree.xpath('//div[@class="team away"]/div[@class="team-info"]/div[@class="rank"]/text()')[0]
    visiting_team_record = ''
    #visiting_team_logo = tree.xpath('//div[@class="team away"]/div[@class="team-info"]/div[@class="rank"]/text()')[0]
    if visiting_radio_url == '':
        visiting_radio_name = ''
    else:
        visiting_radio_name = visiting_reddit_name
    
    home_team_name = tree.xpath('//div[@class="team home"]/div[@class="team-info"]/div[@class="name"]/a/text()')[0].lstrip('1234567890()').lstrip()
    home_yahoo_name = tree.xpath('//div[@class="team home"]/div[@class="team-info"]/div[@class="name"]//@href')[0][13:-1]
    try:
        home_reddit_name = df[df[1]==home_yahoo_name].iloc[0][2]
    except:
        home_reddit_name = ''
    try:
        home_flair = df[df[1]==home_yahoo_name].iloc[0][6]
    except:
        home_flair = ''
    try:
        home_radio_url = df[df[1]==home_yahoo_name].iloc[0][4]
    except:
        home_radio_url = ''
    try:
        home_subreddit = df[df[1]==home_yahoo_name].iloc[0][5]
    except:
        home_subreddit = ''
    try:	
#       home_rank = rankdf[rankdf.reddit_name == '[](/' + home_reddit_name + ')'].iloc[0][0] + ' '
        home_rank = '(' + tree.xpath('//div[@class="team home"]/div[@class="team-info"]/div[@class="name"]/a/text()')[0].rstrip(' ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.&-()\'').lstrip('(') + ' Seed) '
    except:
        home_rank = ''
    #home_team_record = tree.xpath('//div[@class="team home"]/div[@class="team-info"]/div[@class="rank"]/text()')[0]
    home_team_record = ''
    #home_team_logo = tree.xpath('//div[@class="team away"]/div[@class="team-info"]/div[@class="rank"]/text()')[0]
    if home_subreddit=='' and visiting_subreddit=='':
        subreddits = ''
    elif home_subreddit=='' or visiting_subreddit=='':
        subreddits = '\n' + '\n' + '\n' + '\n' + '**Subscribe to these communities**'  + '\n' + '\n' + home_subreddit + visiting_subreddit
    else:
        subreddits =  '\n' + '\n' + '\n' + '\n' + '**Subscribe to these communities**' + '\n' + '\n' + visiting_subreddit + ' | ' + home_subreddit
    if home_radio_url == '':
        home_radio_name = ''
    else:
        home_radio_name = home_reddit_name

    pre_time = tree.xpath('//li[@class="status"]/text()')[0]
    date_time = datetime.strptime(pre_time[5:-7], "%b %d %H:%M").strftime("%-H:%M") + pre_time[-7:-4] + ' EDT'
    stadium = tree.xpath('//li[@class="stadium"]/span/text()')[0]
    try:
        tv = tree.xpath('//li[@class="left"]/ul/li/text()')[0]
    except:
        tv = '    No TV'    
    try:
        tourney = tree.xpath('//span[@class="tournament-name"]/text()')[0]
    except:
        tourney = '' 
    try:
        odds_favorite = tree.xpath('//li[@class="odds-ps-name\"]/text()')[0]
    except:
        odds_favorite = 'Odds not set'
    try:
        odds_spread = tree.xpath('//li[@class="odds-ps"]/text()')[0]
    except:
        odds_spread = 'NA'
    try:
        odds_ou = tree.xpath('//li[@class="odds-overunder"]/text()')[0]
    except:
        odds_ou = 'NA'

    subreddit = 'collegebasketball'

    title = '[Game Thread] ' + visiting_rank  + visiting_team_name + ' vs. ' + home_rank  + home_team_name + ' (' + date_time + ')' + ' ' + tourney

    body = '###NCAA Basketball' + '\n' + ' ' + '\n' + '---' \
    + '\n' + visiting_flair + ' **' + visiting_rank +visiting_team_name+'** '+visiting_team_record+' vs. ' + home_flair + ' **'  + home_rank+ home_team_name+'** '+home_team_record   \
    + '\n' + ' ' + '\n' + '**Tipoff:** '+ date_time + '\n' +  ' ' \
    + '\n' +  '**Venue:** '+stadium + '\n' +  ' ' \
    + '\n' +  '-----------------------------------------------------------------' + '\n' +  ' ' \
    + '\n' +  '**[Join the live IRC chat on freenode, #redditcbb](http://webchat.freenode.net/?channels=#redditcbb)**' \
    + '\n' +  ' '     \
    + '\n' +  '-----------------------------------------------------------------' + '\n' +  ' ' \
    + '\n' +  '**Television:** ' + '\n' +  tv[4:] + '\n' +  ' ' + '\n' +  '**Streams:** ' \
    + '\n' +  '[IsTheGameOn?](http://isthegameon.com/)' + '\n' +  ' ' \
    + '\n' +  '**Radio:** ' + '\n' +  '[' + visiting_radio_name + '](http://tunein.com' + visiting_radio_url + ')' + '\n'  +  ' ' \
    + '  [' + home_radio_name + '](http://tunein.com' + home_radio_url + ')' + '\n'  +  ' ' \
    + '\n' +  '**Preview/Follow:**' + '\n' +  '[Yahoo!](http://sports.yahoo.com'+urlname+')' \
    + '\n' +  ' '  + '\n' +  '**Odds**'  + '\n' +  ' '     \
    + '\n' +  '**Favorite:** ' + odds_favorite + '\n' +  ' '    + '\n' +  '**Game Line:** '+odds_spread \
    + '\n' +  ' ' + '\n' +  '**O/U:** ' + odds_ou \
    + '\n' +  ' ' + '\n' +  '----------------------------------------------------------------- ' \
    + '\n' + '\n' + '\n' + '\n' + '**Thread Notes:**   ' \
    + '\n' + '\n' + '- Discuss whatever you wish. You can trash talk, but keep it civil.' \
    + '\n' + '\n' + '- Turning comment sort to new will help you see the newest posts. ' \
    + '\n' + '\n' + '- Try [Chrome Refresh](https://chrome.google.com/extensions/detail/aifhnlnghddfdaccgbbpbhjfkmncekmn) or Firefoxs [ReloadEvery](https://addons.mozilla.org/en-US/firefox/addon/115/) to auto-refresh this tab.' \
    + '\n' + '\n' + '- You may also like [reddit stream](http://www.reddit.com/r/CFB/comments/wn9uj/lets_discuss_game_threads_come_fall/c5esw1u) to keep up with comments. ' \
    + '\n' + '\n' + '- [Follow @redditCBB](https://twitter.com/redditCBB) on twitter for news, updates, and bad attempts at humor.' \
    + subreddits \
    + '\n' +  ' ' + '\n' +  '----------------------------------------------------------------- ' \
    + '\n' + '\n' + '\n' + '\n' + 'Beep Boop. I am a bot. Please message /u/airjesse with any feedback for me.   ' \


    scorescraper.posttoreddit(subreddit,title,body,secret,token)
        
def rename_duplicates( old ):
    seen = {}
    for x in old:
        if x in seen:
            seen[x] += 1
            yield x + 11
        else:
            seen[x] = 0
            yield x

def posttoreddit(subreddit,title,body,secret,token):
    import praw
    r = praw.Reddit('GameThreadGenerator')
    r.set_oauth_app_info(client_id='toi-mfvVqbptkA',client_secret=secret,redirect_uri='http://127.0.0.1:65010/authorize_callback')
    r.refresh_access_information(token)
    r.submit(subreddit,title,body,send_replies='false')

def main(url,secret,token):
    import scorescraper
    import pandas as pd
    (timedeltas,urls) = scorescraper.getgametimes(url)
    df = pd.DataFrame({'timedeltas': timedeltas, 'urls': urls})
    df2 = df[df['timedeltas'].between(51,60)]
    for index, row in df2.iterrows():
        scorescraper.getcbbthread(row['urls'],secret,token)