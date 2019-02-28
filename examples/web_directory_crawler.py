#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import htmllistparse
import os
import time
import sys

sys.path.append("./../src")
from TorCrawler import TorCrawler

class WebDirectoryCrawler(object):
    def __init__(
            self,
            sitebase,
            savebase=None,
            delay=5,
            retrylimit=5,
            ctrl_pass=None,
            n_requests=5,
            use_tor=False,
            headers={}
             ):
        self.sitebase = sitebase
        self.savebase = savebase
        self.delay = delay
        self.headers = headers
        self.retrylimit = retrylimit
        self.n_requests = n_requests
        self.crawler = TorCrawler(ctrl_pass=ctrl_pass,
                                  n_requests=n_requests,
                                  use_tor=use_tor)

    def get_content(self, url, use_bs, retrylimit=5):
        req = None
        retry = 0
        while(retry<self.retrylimit):
            try:
                if use_bs:
                    self.crawler.use_bs=True
                    req = self.crawler.get(url, headers=self.headers)
                    return req
                else:
                    self.crawler.use_bs=False
                    req = self.crawler.get(url, headers=self.headers)
                    return req
            except Exception as err:
                print(err)
                print("retry..: ", retry+1)
                time.sleep(2)
                retry += 1
        return None

    def download_file(self, cwd, savepath, filename):
        if cwd != '/' and cwd[-1] != "/":
            cwd +='/'
        url = self.sitebase + cwd + filename

        req = self.get_content(url, use_bs=False)
        if not req:
            print("download fail: " + filename)
        f = open(savepath+filename, 'wb')
        f.write(req.content)
        f.close()

    def recursive_listing(self, cwd):
        savepath=None
        if cwd != '/' and cwd[-1] != "/":
            cwd +='/'
        url = self.sitebase + cwd
        req = self.get_content(url, use_bs=True)
        if not req:
            print("crawler error")
            return
        cwd, listing = htmllistparse.parse(req)
        if cwd == None:
            print("It does not seem to be 'Web Directory'.")
            return
        if cwd != '/' and cwd[-1] != "/":
            cwd +='/'
        if self.savebase:
            savepath = self.savebase+cwd
            try:
                print("Create directory: " + savepath)
                if not os.path.exists(savepath):
                    os.makedirs(savepath)
            except Exception as err:
                print("Cannot create directory..: " + str(err))
                sys.exit(0)

        for f in listing:
            if f.name[-1] != "/":
                print(cwd + f.name)
                if self.savebase:
                    self.download_file(cwd, savepath, f.name)
            else:
                print(cwd+f.name)
                self.recursive_listing(cwd+f.name)
            time.sleep(self.delay)

def main():
    headers = {
        "User-Agent":
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) "
            "Gecko/20100101 Firefox/65.0"
    }

    # Web Directory service domain
    # You have to change the domain.
    sitebase = "http://cqqwpdsiochyns4h.onion"

    # The Hidden Wiki
    # sitebase = "http://zqktlwi4fecvo6ri.onion/wiki/index.php/Main_Page"

    savebase = "/home/kisec/Tor_Crawler/examples/crawl"
    try:
        crawler = WebDirectoryCrawler(sitebase,
                                            savebase=savebase,
                                            ctrl_pass='kisec',
                                            use_tor=True,
                                            headers=headers,
                                            retrylimit=5,
                                            delay=1)
        crawler.recursive_listing('/')
    except KeyboardInterrupt:
        print("Terminated crawler")

if __name__ == '__main__':
    main()
