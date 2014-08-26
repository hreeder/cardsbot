class CardsGame(object):
    def __init__(self, client):
        self.client = client
        
        self.game_open=False
        self.game_in_progress=False
        
        self.players = []
        
    def register_commands(self, xmpp):
        xmpp.register_command("open", self.open_game)
        xmpp.register_command("join", self.join_game)
        
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

        self.game_open=True
        self.players.append(self.get_jid(msg))
        
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
        
        if jid in self.players:
            return "%s: You are already in the game!" % (msg['from'].resource,)
        
        self.players.append(jid)
        return "%s has joined the game!" % (msg['from'].resource,)