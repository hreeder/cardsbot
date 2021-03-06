#!/usr/bin/env python
import config
import sleekxmpp
import logging
import cardsgame
from optparse import OptionParser

class CardsBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid + "/cahbot-dev-0.01", password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self.muc_message_handler)
        self.commands = {}
        self.config = config

    def start(self, args):
        self.send_presence()
        self.get_roster()
        self.plugin['xep_0045'].joinMUC(
            config.xmpp['muc'], config.xmpp['nick']
        )

        self.register_command("help", self.help_text)

    def register_command(self, command, function):
        self.commands[command] = function

    def help_text(self, msg):
        return "The following commands are available: " + ", ".join(["%s%s" % (config.xmpp['trigger'], command) for command in self.commands])

    def muc_message_handler(self, msg):
        print "<%s> %s" % (msg['from'], msg['body'])
        if msg['body'][0] == config.xmpp['trigger']:
            if " " in msg['body']:
                firstWord = msg['body'][1:].split(" ")[0]
            else:
                firstWord = msg['body'][1:]

            firstWord = firstWord.lower()

            try:
                output = self.commands[firstWord](msg)

                if output:
                    self.send_message(
                                      mto=msg['from'].bare,
                                      mbody=output,
                                      mtype="groupchat"
                                      )
            except KeyError:
                self.send_message(
                    mto=msg['from'].bare,
                    mbody="Command '%s' Not Recognised. Please try %shelp" % (firstWord,config.xmpp['trigger']),
                    mtype="groupchat"
                )


if __name__ == "__main__":
    optp = OptionParser()

    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    opts, args = optp.parse_args()

    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    xmpp = CardsBot(config.xmpp['jid'], config.xmpp['password'])
    xmpp.register_plugin('xep_0045')
    
    cah = cardsgame.CardsGame(xmpp)   
    cah.register_commands(xmpp)

    if xmpp.connect():
        xmpp.process()
    else:
        print("Unable to connect")