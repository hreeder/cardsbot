class CardsGame(object):
    def __init__(self, client):
        self.client = client
        
        self.game_open=False
        self.game_in_progress=False
        self.allowing_cards=False
        
        self.game_owner = None
        self.players = {}
        self.card_tsar = None
        
        self.black_discarded = []
        self.white_discarded = []
        
    def register_commands(self, xmpp):
        xmpp.register_command("open", self.open_game)
        xmpp.register_command("join", self.join_game)
        xmpp.register_command("start", self.start_game)
        
    def get_jid(self, msg):
        muc = msg['from'].bare
        nick = msg['from'].resource
        
        jid = self.client.plugin['xep_0045'].getJidProperty(muc, nick, "jid")
        
        if jid:
            return jid.bare
        else:
            return None
    
    def open_game(self, msg):
        if self.game_open:
            return "A game is already open or in progress. Maybe try joining the game?"

        jid = self.get_jid(msg)

        self.game_open=True
        self.game_owner=jid
        self.players[jid] = {'score': 0, 'hand': []}
        self.card_tsar=jid
        
        self.client.send_message(mto=msg['from'].bare,
                                 mtype="groupchat",
                                 mbody="%s has opened a game of Cards Against Humanity! Use %sjoin to join the game!" % (msg['from'].resource, self.client.config.xmpp['trigger'])
                                 )
        
        self.client.send_message(mto=msg['from'].bare,
                                 mtype="groupchat",
                                 mbody="%s may use %sexpansions to configure which expansions will be used in play." % (msg['from'].resource, self.client.config.xmpp['trigger'])
                                 )
        
        return
    
    def join_game(self, msg):
        if self.game_in_progress:
            return "The game has already started, and I am unable to join you into the game right now"
        if not self.game_open:
            return "There is no game open to join. Open one with %sopen" % (self.client.config.xmpp['trigger'])
        
        jid = self.get_jid(msg)
        
        if jid in self.players.keys():
            return "%s: You are already in the game!" % (msg['from'].resource,)
        
        self.players[jid] = {'score': 0, 'hand': []}
        return "%s has joined the game!" % (msg['from'].resource,)
    
    def start_game(self, msg):
        if not self.game_open:
            return "There is no game open to start! Try %sopen to open a game!" % (self.client.config.xmpp['trigger'],)
        
        jid = self.get_jid(msg)
        
        if jid != self.game_owner:
            return "Only the game owner may start the game"
        
        if self.game_in_progress:
            return "The game has already begun!"
        
        if len(self.players) == 1:
            return "You can't play by yourself!"
        
        self.game_in_progress = True
        self.client.send_message(mto=msg['from'].bare,
                                 mtype="groupchat",
                                 mbody="%s has started a game with %s players." % (msg['from'].resource, len(self.players))
                                 )
        
        self.start_round(msg)
        
    def start_round(self, msg):
        if not self.game_in_progress:
            return
        
        # Get Card Tsar's Nick
        if self.client.plugin['xep_0045'].jidInRoom(msg['from'].bare, self.card_tsar):
            tsar = self.client.plugin['xep_0045'].getNick(msg['from'].bare, self.card_tsar)
        else:
            tsar = self.card_tsar.user
            
        self.client.send_message(mto=msg['from'].bare,
                                 mtype="groupchat",
                                 mbody="%s is the Card Tsar for this round." % (tsar,)
                                 )
        
        # Allow cards to be played
        self.allowing_cards=True
        
        # Draw Black Card
        
        # Announce Black Card