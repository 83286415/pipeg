#!/usr/bin/env python3
# Copyright © 2012-13 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version. It is provided for
# educational purposes and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import argparse
import multiprocessing
import os
import queue
import tempfile
import threading
import webbrowser
import Feed
import Qtrac


def main():
    limit, concurrency = handle_commandline()
    Qtrac.report("starting...")
    filename = os.path.join(os.path.dirname(__file__), "whatsnew.dat")  # os.path.dirname(__file__) returns py file path
    # this dat file stores those news's url and title with Format: Title\nURL UTF-8
    jobs = queue.Queue()
    results = queue.Queue()
    create_threads(limit, jobs, results, concurrency)
    todo = add_jobs(filename, jobs)  # _todo is the title count of url
    process(todo, jobs, results, concurrency)


def handle_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--limit", type=int, default=0,
            help="the maximum items per feed [default: unlimited]")  # max pieces of news per url
    parser.add_argument("-c", "--concurrency", type=int,
            default=multiprocessing.cpu_count() * 4,  # maybe *2 is the best config for threading
            help="specify the concurrency (for debugging and "
                "timing) [default: %(default)d]")
    args = parser.parse_args()
    return args.limit, args.concurrency


def create_threads(limit, jobs, results, concurrency):
    for _ in range(concurrency):
        thread = threading.Thread(target=worker, args=(limit, jobs,
                results))
        thread.daemon = True
        thread.start()


def worker(limit, jobs, results):
    while True:
        try:
            feed = jobs.get()  # block until Feed is loaded into this queue. see def add_jobs()
            ok, result = Feed.read(feed, limit)  # open url in feed.url and return news title + body; ok: url open ok
            if not ok:
                Qtrac.report(result, True)  # result here is url title + error info
            elif result is not None:
                Qtrac.report("read {}".format(result[0][4:-6]))  # ignore the <ul> tag
                results.put(result)
        finally:
            jobs.task_done()  # each jobs.get() ends with jobs.task_done()


def add_jobs(filename, jobs):
    for todo, feed in enumerate(Feed.iter(filename), start=1):  # _todo is 1, 2, 3, 4...  feed is Feed(title ,url) gen
        jobs.put(feed)  # load Feed's generator into jobs' queue
    return todo  # return the title count of mission


def process(todo, jobs, results, concurrency):
    canceled = False
    try:
        jobs.join()  # Wait for all the work to be done
    except KeyboardInterrupt: # May not work on Windows
        Qtrac.report("canceling...")
        canceled = True
    if canceled:
        done = results.qsize()  # return the queue's size: the count of the done jobs
        filename = None  # raise a OS Error if filename is None when web browser open it
    else:
        done, filename = output(results)
    Qtrac.report("read {}/{} feeds using {} threads{}".format(done, todo,
            concurrency, " [canceled]" if canceled else ""))
    print()  # just a blank line
    if not canceled:
        webbrowser.open(filename)


def output(results):  # write a result html to show
    done = 0
    filename = os.path.join(tempfile.gettempdir(), "whatsnew.html") 
    with open(filename, "wt", encoding="utf-8") as file:
        file.write("<!doctype html>\n")
        file.write("<html><head><title>What's New</title></head>\n")
        file.write("<body><h1>What's New</h1>\n")
        while not results.empty():  # Safe because all jobs have finished
            result = results.get_nowait()
            done += 1
            for item in result:
                file.write(item)
        file.write("</body></html>\n")
    return done, filename


if __name__ == "__main__":
    main()
