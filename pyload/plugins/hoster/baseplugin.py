# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from urllib.parse import urlparse
from re import match, search
from urllib.parse import unquote

from pyload.plugins.request import ResponseException
from pyload.plugins.hoster import Hoster
from pyload.utils import html_unescape, remove_chars


class BasePlugin(Hoster):
    __name__ = "BasePlugin"
    __type__ = "hoster"
    __pattern__ = r'^unmatchable$'
    __version__ = "0.19"
    __description__ = """Base Plugin when any other didnt fit"""
    __author_name__ = "RaNaN"
    __author_mail__ = "Mast3rRaNaN@hotmail.de"

    def setup(self):
        self.chunkLimit = -1
        self.resumeDownload = True

    def process(self, pyfile):
        """main function"""

        #debug part, for api exerciser
        if pyfile.url.startswith("DEBUG_API"):
            self.multiDL = False
            return

        # self.__name__ = "NetloadIn"
        # pyfile.name = "test"
        # self.html = self.load("http://localhost:9000/short")
        # self.download("http://localhost:9000/short")
        # self.api = self.load("http://localhost:9000/short")
        # self.decryptCaptcha("http://localhost:9000/captcha")
        #
        # if pyfile.url == "79":
        #     self.pyload.api.addPackage("test", [str(i) for i in range(80)], 1)
        #
        # return
        if pyfile.url.startswith("http"):

            try:
                self.downloadFile(pyfile)
            except ResponseException as e:
                if e.code in (401, 403):
                    self.logDebug("Auth required")

                    account = self.pyload.accountManager.getAccountPlugin('Http')
                    servers = [x['login'] for x in account.getAllAccounts()]
                    server = urlparse(pyfile.url).netloc

                    if server in servers:
                        self.logDebug("Logging on to %s" % server)
                        self.req.addAuth(account.accounts[server]["password"])
                    else:
                        for pwd in pyfile.package().password.splitlines():
                            if ":" in pwd:
                                self.req.addAuth(pwd.strip())
                                break
                        else:
                            self.fail(_("Authorization required (username:password)"))

                    self.downloadFile(pyfile)
                else:
                    raise

        else:
            self.fail("No Plugin matched and not a downloadable url.")

    def download_file(self, pyfile):
        url = pyfile.url

        for _ in range(5):
            header = self.load(url, just_header=True)

            # self.load does not raise a BadHeader on 404 responses, do it here
            if 'code' in header and header['code'] == 404:
                raise ResponseException(404)

            if 'location' in header:
                self.logDebug("Location: " + header['location'])
                base = match(r'https?://[^/]+', url).group(0)
                if header['location'].startswith("http"):
                    url = unquote(header['location'])
                elif header['location'].startswith("/"):
                    url = base + unquote(header['location'])
                else:
                    url = '%s/%s' % (base, unquote(header['location']))
            else:
                break

        name = html_unescape(unquote(urlparse(url).path.split("/")[-1]))

        if 'content-disposition' in header:
            self.logDebug("Content-Disposition: " + header['content-disposition'])
            m = search("filename(?P<type>=|\*=(?P<enc>.+)'')(?P<name>.*)", header['content-disposition'])
            if m:
                disp = m.groupdict()
                self.logDebug(disp)
                if not disp['enc']:
                    disp['enc'] = 'utf-8'
                name = remove_chars(disp['name'], "\"';").strip()
                name = str(unquote(name), disp['enc'])

        if not name:
            name = url
        pyfile.name = name
        self.logDebug("Filename: %s" % pyfile.name)
        self.download(url, disposition=True)
