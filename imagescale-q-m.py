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
import collections
import math
import multiprocessing
import os
import sys
import Image
import Qtrac


Result = collections.namedtuple("Result", "copied scaled name")  # copied:0or1 scaled:0or1
Summary = collections.namedtuple("Summary", "todo copied scaled canceled")


def main():
    size, smooth, source, target, concurrency = handle_commandline()
    Qtrac.report("starting...")  # just output the first 70th's log words
    summary = scale(size, smooth, source, target, concurrency)  # return Summary
    summarize(summary, concurrency)


def handle_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--concurrency", type=int,
            default=multiprocessing.cpu_count(),
            help="specify the concurrency (for debugging and "
                "timing) [default: %(default)d]")
    parser.add_argument("-s", "--size", default=400, type=int,
            help="make a scaled image that fits the given dimension "
                "[default: %(default)d]")
    parser.add_argument("-S", "--smooth", action="store_true",   # "true" value is stored for this parameter
            help="use smooth scaling (slow but good for text)")
    parser.add_argument("source",
            help="the directory containing the original .xpm images")
    parser.add_argument("target",
            help="the directory for the scaled .xpm images")
    args = parser.parse_args()
    source = os.path.abspath(args.source)  # Return the absolute path of source xpm images
    target = os.path.abspath(args.target)
    if source == target:
        args.error("source and target must be different")
    if not os.path.exists(args.target):
        os.makedirs(target)  # makedirs: make dirS if they don't exist
    return args.size, args.smooth, source, target, args.concurrency


def scale(size, smooth, source, target, concurrency):
    canceled = False
    jobs = multiprocessing.JoinableQueue()  # make jobs queue: like Queue() but join() and task_done() added
    results = multiprocessing.Queue()  # make results queue: filled in worker()
    create_processes(size, smooth, jobs, results, concurrency)  # Process in for -> daemon -> start()
    todo = add_jobs(source, target, jobs)  # fill jobs queue with source and target and return source images' names list
    try:        # queue.put() -> queue.task_done() in for -> queue.join()
        jobs.join()  # block main process until jobs queue is empty
    except KeyboardInterrupt:  # May not work on Windows
        Qtrac.report("canceling...")
        canceled = True
    copied = scaled = 0
    while not results.empty():  # queue results is filled in each worker() process
        result = results.get_nowait()  # Remove and return an item from the queue without blocking
        copied += result.copied
        scaled += result.scaled
    return Summary(todo, copied, scaled, canceled)  # copied: the total number of copied images


def create_processes(size, smooth, jobs, results, concurrency):
    for _ in range(concurrency):
        process = multiprocessing.Process(target=worker, args=(size,
                smooth, jobs, results))
        process.daemon = True  # All multiprocess are done when main process is done
        process.start()  # prepare multiprocess and call run()
        # here the process is blocked, not running, because worker's jobs queue is empty.
        # It needs to add_jobs(): jobs.put() to run() this process


def worker(size, smooth, jobs, results):
    while True:  # infinite loop is to finished when main process ends. (Daemon = True)
        try:
            sourceImage, targetImage = jobs.get()  # get images from queue. Blocked if no images to get.
            try:
                result = scale_one(size, smooth, sourceImage, targetImage)  # return Result
                Qtrac.report("{} {}".format("copied" if result.copied else
                        "scaled", os.path.basename(result.name)))
                results.put(result)  # put the result(Result) into the results queue
            except Image.Error as err:
                Qtrac.report(str(err), True)  # True: it is an error
        finally:
            jobs.task_done()  # this job is done. One task is done.


def add_jobs(source, target, jobs):
    for todo, name in enumerate(os.listdir(source), start=1):  # listdir: make a list of all file names in source path
        sourceImage = os.path.join(source, name)    # c:/source/images/1
        targetImage = os.path.join(target, name)    # c:/target/images/1
        jobs.put((sourceImage, targetImage))  # put the job into the jobs queue
    return todo  # the list of all file names in source path


def scale_one(size, smooth, sourceImage, targetImage):
    oldImage = Image.from_file(sourceImage)  # load source image
    if oldImage.width <= size and oldImage.height <= size:  # size: specified width and height, default values: 400, 400
        oldImage.save(targetImage)  # save it as target filename
        return Result(1, 0, targetImage)  # 1: copied  0: scaled
    else:
        if smooth:
            scale = min(size / oldImage.width, size / oldImage.height)  # 0 < scale < 1
            newImage = oldImage.scale(scale)
        else:
            stride = int(math.ceil(max(oldImage.width / size,
                                       oldImage.height / size)))  # ceil refer to hands-on note
            newImage = oldImage.subsample(stride)  # make the new image size into 1/stride
        newImage.save(targetImage)
        return Result(0, 1, targetImage)  # 0: copied   1: scaled


def summarize(summary, concurrency):
    message = "copied {} scaled {} ".format(summary.copied, summary.scaled)
    difference = summary.todo - (summary.copied + summary.scaled)
    if difference:
        message += "skipped {} ".format(difference)
    message += "using {} processes".format(concurrency)
    if summary.canceled:
        message += " [canceled]"
    Qtrac.report(message)  # flush out logs from ram
    print()  # just a blank line


if __name__ == "__main__":
    main()
