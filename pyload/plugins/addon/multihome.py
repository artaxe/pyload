# -*- coding: utf-8 -*-
#@author: mkaay

from __future__ import unicode_literals

from builtins import str
from builtins import object
from time import time

from pyload.plugins.hook import Hook


class MultiHome(Hook):
    __name__ = "MultiHome"
    __version__ = "0.11"
    __description__ = """Ip address changer"""
    __config__ = [("activated", "bool", "Activated", False),
                  ("interfaces", "str", "Interfaces", "None")]
    __author_name__ = "mkaay"
    __author_mail__ = "mkaay@mkaay.de"

    def setup(self):
        self.register = {}
        self.interfaces = []
        self.parseInterfaces(self.getConfig("interfaces").split(";"))
        if not self.interfaces:
            self.parseInterfaces([self.config["download"]["interface"]])
            self.setConfig("interfaces", self.toConfig())

    def to_config(self):
        return ";".join([i.adress for i in self.interfaces])

    def parse_interfaces(self, interfaces):
        for interface in interfaces:
            if not interface or str(interface).lower() == "none":
                continue
            self.interfaces.append(Interface(interface))

    def core_ready(self):
        requestFactory = self.pyload.requestFactory
        oldGetRequest = requestFactory.getRequest

        def get_request(pluginName, account=None):
            iface = self.bestInterface(pluginName, account)
            if iface:
                iface.useFor(pluginName, account)
                requestFactory.iface = lambda: iface.adress
                self.logDebug("Multihome: using address: " + iface.adress)
            return oldGetRequest(pluginName, account)

        requestFactory.getRequest = getRequest

    def best_interface(self, pluginName, account):
        best = None
        for interface in self.interfaces:
            if not best or interface.lastPluginAccess(pluginName, account) < best.lastPluginAccess(pluginName, account):
                best = interface
        return best


class Interface(object):
    def __init__(self, adress):
        self.adress = adress
        self.history = {}

    def last_plugin_access(self, pluginName, account):
        if (pluginName, account) in self.history:
            return self.history[(pluginName, account)]
        return 0

    def use_for(self, pluginName, account):
        self.history[(pluginName, account)] = time()

    def __repr__(self):
        return "<Interface - %s>" % self.adress
