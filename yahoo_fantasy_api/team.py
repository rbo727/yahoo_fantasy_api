#!/bin/python

from fantasytools.yahoo_fantasy_api import yhandler
import objectpath


class Team:
    """An abstraction for all of the team-level APIs in Yahoo! fantasy

    :param sc: Fully constructed session context
    :type sc: :class:`yahoo_oauth.OAuth2`
    :param team_key: Team key identifier for the team we are constructing this
        object for.
    :type team_key: str
    """

    def __init__(self, sc, team_key):
        self.sc = sc
        self.team_key = team_key
        self.yhandler = yhandler.YHandler(sc)
        self.matchup_cache = {}

    def team_name(self, ):
        """Return the team name
        :return: String of team name

        >>> tm.daily_team_stats(3)

        """
        t = objectpath.Tree(self.yhandler.get_team_raw(self.team_key))
        name = t.execute('$..team..name')

        return name

    def inject_yhandler(self, yhandler):
        self.yhandler = yhandler

    def matchup(self, week):
        """Return the matchup for a given week. The first level of this dictionary
         is simply the matchup metadata

        :param week: Week number to find the matchup for
        :type week: int
        :return: Matchup metadata
        """
        self.matchup_cache = self.matchup_cache or self._get_all_matchups()
        t = objectpath.Tree(self.matchup_cache)
        all_matchups = t.execute("$..matchup")
        for matchup in all_matchups:
            if matchup['week'] == str(week):
                return matchup

        raise LookupError("Could not find weekly matchup")

    def matchup_opponent(self, week):
        """Return the team of the matchup my team is playing in a given week

        :param week: Week number to find the matchup for
        :type week: int
        :return: Team key of the opponent

        >>> tm.matchup_opponent(3)
        388.l.27081.t.9
        """
        matchup = self.matchup(week)
        m = objectpath.Tree(matchup)
        team_keys = m.execute("$..team_key")
        for team_key in team_keys:
            if  team_key != self.team_key:
                return team_key
        raise LookupError("Could not find opponent")

    def matchup_stat_winners(self, week):
        """Return the stat winner info for a matchup in a given week.

        :param week: Week number to find the matchup for
        :type week: int
        :return: Matchup metadata

        """
        try:
            matchup = self.matchup(week)
        except LookupError:
            return None
        m = objectpath.Tree(matchup)
        stat_winners = m.execute("$..stat_winners.stat_winner")

        return stat_winners

    def daily_roster(self, date):
        """Return the team roster for a given date

        :param date: Date of the roster to get
        :type week: string (YYYY-MM-DD)
        :return: Array of players.  Each entry is a dict with the following
           fields: player_id, name, position_type, eligible_positions,
           selected_position

        >>> tm.roster(3)
        [{'player_id': 8578, 'name': 'John Doe', 'position_type': 'B',
         'eligible_positions': ['C','1B'], 'selected_position': 'C'},
         {'player_id': 8967, 'name': 'Joe Baseball', 'position_type': 'B',
         'eligible_positions': ['SS'], 'selected_position': 'SS'},
         {'player_id': 9961, 'name': 'Ed Reliever', 'position_type': 'P',
         'eligible_positions': ['RP']}]
        """
        def _compact_selected_pos(j):
            selected_position = {}
            for d in j:
                selected_position.update(d)
            return selected_position

        def _compact_eligible_pos(j):
            compact_pos = []
            for p in j["eligible_positions"]:
                compact_pos.append(p['position'])
            return compact_pos

        t = objectpath.Tree(self.yhandler.get_daily_roster_raw(self.team_key, date))
        roster = t.execute('$..roster.(coverage_type, date, week, is_editable)')
        roster_meta = next(roster)
    #    roster_meta['team_key']=self.team_key
        players = t.execute('$..(player)')
        roster_players = []
        selected_position = {}
        elligible_position = ()
        for player in players:
            player_dict = {}
            p = objectpath.Tree(player)

            it = p.execute('''
                            $..(player_key,player_id,full,ascii_first,ascii_last,status,
                            status_full,injury_note,editorial_player_key,editorial_team_key,
                            editorial_team_full_name,editorial_team_abbr,bye_week,uniform_number,
                            display_position,headshot_url,headshot_size,image_url,is_undroppable,
                            is_editable,is_starting,position_type,primary_position,eligible_positions,
                            selected_position,order_num)''')

            for item in it:
                for k,v in item.items():
                    if k == 'selected_position':
                        v = _compact_selected_pos(v)
                    player_dict[k] = v
            roster_players.append(player_dict)
            
        return roster_meta, roster_players
            # try:
            #     while True:
            #         item = next(it)
                    # roster.append({ "player_key":next(it)["player_key"],
                    #                 "player_id": int(next(it)["player_id"]),
                    #                 "full": next(it)["name"]["full"],
                    #                 "ascii_first": next(it)["name"]["ascii_first"],
                    #                 "ascii_last": next(it)["name"]["ascii_last"],
                    #                 "status": next(it)["status"],
                    #                 "status_full": next(it)["status_full"],
                    #                 "injury_note": next(it)["injury_note"],
                    #                 "editorial_player_key": next(it)["editorial_player_key"],
                    #                 "editorial_team_key": next(it)["editorial_team_key"],
                    #                 "editorial_team_full_name": next(it)["editorial_team_full_name"],
                    #                 "editorial_team_abbr": next(it)["editorial_team_abbr"],
                    #                 "bye_week": next(it)["bye_weeks"]["week"],
                    #                 "uniform_number": next(it)["uniform_number"],
                    #                 "display_position": next(it)["display_position"],
                    #                 "headshot_url": next(it)["headshot"]["headshot_url"],
                    #                 "headshot_size": next(it)["headshot"]["headshot_size"],
                    #                 "image_url": next(it)["image_url"],
                    #                 "is_undroppable": next(it)["is_undroppable"],
                    #                 "is_editable": next(it)["is_editable"],
                    #                 "is_starting": next(it)["is_starting"],
                    #                 "position_type": next(it)["position_type"],
                    #                 "primary_position": next(it)["primary_position"],
                    #                 "elligible_positions": next(it)["elligible_positions"],
                    #                 "selected_position": next(it)["selected_position"],
                    #                 "order_num": next(it)["order_num"],
                    #                 })
            # except StopIteration:
            #     pass


 



    def weekly_roster(self, week):
        """Return the team roster for a given week

        :param week: Week number of the roster to get
        :type week: int
        :return: Array of players.  Each entry is a dict with the following
           fields: player_id, name, position_type, eligible_positions,
           selected_position

        >>> tm.roster(3)
        [{'player_id': 8578, 'name': 'John Doe', 'position_type': 'B',
         'eligible_positions': ['C','1B'], 'selected_position': 'C'},
         {'player_id': 8967, 'name': 'Joe Baseball', 'position_type': 'B',
         'eligible_positions': ['SS'], 'selected_position': 'SS'},
         {'player_id': 9961, 'name': 'Ed Reliever', 'position_type': 'P',
         'eligible_positions': ['RP']}]
        """
        t = objectpath.Tree(self.yhandler.get_weekly_roster_raw(self.team_key, week))
        it = t.execute('''
                        $..roster.players.(player_key,player_id,full,ascii_first,ascii_last,status,\
                        status_full,injury_note,editorial_player_key,editorial_team_key,\
                        editorial_team_full_name,editorial_team_abbr,bye_week,uniform_number,\
                        display_position,headshot_url,headshot_size,image_url,is_undroppable,\
                        is_editable,is_starting,position_type,primary_position,elligible_positions,\
                        selected_position,order_num)''')

        # def _compact_selected_pos(j):
        #     return j["selected_position"][1]["position"]
        #
        # def _compact_eligible_pos(j):
        #     compact_pos = []
        #     for p in j["eligible_positions"]:
        #         compact_pos.append(p['position'])
        #     return compact_pos

        roster = []
        for player in it:
                roster.append(player)

        return roster

    def daily_team_stats(self, date):
        """Return the team stats for a given date

        :param date: Date of stats to get
        :type date: int
        :return: Array of stats for a given team.  Each entry is a dict with the following
           fields: player_id, name, position_type, eligible_positions,
           selected_position

        >>> tm.daily_team_stats(3)

        """
        t = objectpath.Tree(self.yhandler.get_daily_team_stats_raw(self.team_key, date))
        stats = t.execute('$..team_stats.stats')

        team_stats = []
        for stat in next(stats):
            team_stats.append(stat['stat'])

        return team_stats

    def weekly_team_stats(self, week):
        """Return the cumulative team stats for a given week

        :param week: Week of stats to get
        :type week: int
        :return: Array of stats for a given team.  Each entry is a dict with the following
           fields: stat_id: stat_value

        >>> tm.weekly_team_stats(3)

        """
        t = objectpath.Tree(self.yhandler.get_weekly_team_stats_raw(self.team_key, week))
        stats = t.execute('$..team_stats.stats')

        team_stats = []
        for stat in next(stats):
            team_stats.append(stat['stat'])

        return team_stats

    def matchup_team_points(self, week, team_key):
        """Return the cumulative team points for a given week

        :param week: Week of stats to get
        :type week: int
        :param team_key: Team key
        :type team_key: string
        :return: Dictionary of total points for a given team on a given week.
        """
        matchup = self.matchup(week)
        m = objectpath.Tree(matchup)
        team_keys = m.execute('$..(team_key)')
        team_points = m.execute('$..(team_points)')

        for matchup_team_key, matchup_team_points in zip(team_keys, team_points):
            if matchup_team_key['team_key'] == team_key:
                return matchup_team_points['team_points']

        raise RuntimeError("team_key {} does not exist in current matchup!".format(team_key))

    def _get_all_matchups(self):
        max_week_list=""
        for week_num in range(1, 53):
            max_week_list += str(week_num)+","
        
        self.matchup_cache = self.yhandler.get_matchup_raw(self.team_key, max_week_list)
        return self.matchup_cache
