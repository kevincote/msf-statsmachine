from ohmysportsfeedspy import MySportsFeeds
from datetime import datetime, timedelta

class WeeklyStats:
    def __init__(self, user, pwd, n_last_days):
        self.msf = MySportsFeeds(version="1.0")
        self.auth_user(user, pwd)
        self.n_last_days = n_last_days
        self.dates = self.getdates(self.n_last_days)
        self.dailystats = self.getdailystats()
        self.playerstats = self.getplayerstats()

        self.top10()

    def auth_user(self, user, pwd):
        self.msf.authenticate(user, pwd)
        
    def getdates(self, n_lastdays):
        dates = []

        today = datetime.now()

        for i in range(1, n_lastdays + 1):
            date_n_ago = today - timedelta(days=i)

            frmt_date = date_n_ago.strftime("%Y%m%d")

            dates.append(frmt_date)

        return dates

    def getdailystats(self):
        dailystats = {}
        for date in self.dates:
            print "Retrieving daily stats for: %s" % date
            stats = self.msf.msf_get_data(league='nhl', season='2017-2018-regular',
                                           feed='daily_player_stats',
                                           format='json',
                                           fordate=date)

            dailystats[date] = stats["dailyplayerstats"]["playerstatsentry"]

        return dailystats

    def getplayerstats(self):
        all_playerstats = {}
        for date, playerlist in self.dailystats.iteritems():
            for player in playerlist:
                playerinfo = player["player"]
                playerstats = player["stats"]

                playerid = playerinfo["ID"]

                if not all_playerstats.has_key(playerid):
                    all_playerstats[playerid] = {
                        'name': "%s %s" % (playerinfo["FirstName"], playerinfo["LastName"]),
                        'id': playerid
                    }
                    for stat, statvalue in playerstats.iteritems():
                        all_playerstats[playerid][stat] = eval(statvalue['#text'])

                else:
                    for stat, statvalue in playerstats.iteritems():
                        if stat == 'FaceoffPercent' or stat == 'ShotPercent':
                            avg = (eval(statvalue['#text']) +
                                      all_playerstats[playerid][stat]) / 2.0
                            all_playerstats[playerid][stat] = avg
                        else:
                            all_playerstats[playerid][stat] = eval(statvalue['#text']) + all_playerstats[playerid][stat]

        ordered = sorted(all_playerstats.items(), key=lambda x: x[1]['Points'], reverse=True)

        return ordered

    def top10(self):
        print "Exporting TOP 10 players stats for last %s days" % self.n_last_days
        top10 = self.playerstats[:10]

        for player in top10:
            print player[1]['name']
            print "Total points: %s" % player[1]['Points']
            print "------------------------------------------------"

stats = WeeklyStats("kaycee", "plr4954cl", 3)

print "done"