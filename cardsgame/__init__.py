class CardsGame(object):
    def __init__(self, client):
        self.client = client
        
        self.game_open=False
        self.game_in_progress=False
        
        self.players = []
        
    def register_commands(self, xmpp):
        xmpp.register_command("open", self.open_game)
        
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

        return "%s has opened a game of Cards Against Humanity! Use %sjoin to join the game!\r\n%s may use %sexpansions to configure which expansions will be used in play." % (msg['from'].resource, self.client.config.xmpp['trigger'], msg['from'].resource, self.client.config.xmpp['trigger'])