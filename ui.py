import threading
from time import sleep
from typing import Tuple
from db import DB
import tkinter as tk
from tkinter import BOTTOM, LEFT, RIGHT, TOP, StringVar, ttk
from concurrent import futures
from queue import Queue
from threading import Event as ThreadEvent
import requests
import logging


class UI:
    def __init__(self, db: DB) -> None:
        self.db = db
        self.list = db.get_all()
        self.root = tk.Tk()
        self.bg = '#2b2b2b'
        self.table_entries = []
        self.setup()

    def add_url(self):
        if(len(self.url_txt.get()) < 1):
            return
        url = self.url_txt.get()
        self.url_txt.set("")
        self.db.save_url(url)
        item = {'url': url, 'status': None, 'elapsed': None}
        tableEntry = self.treeview.insert(
            "", tk.END, text=url, values=(None, None))
        self.table_entries.append(tableEntry)
        self.list.append(item)
        data = self.fetch(item)
        self.update_table_entry((len(self.list)-1, data), self.db)

    def draw_table(self):
        self.treeview = ttk.Treeview(self.root, columns=("status", "elapsed"))
        self.treeview.heading("#0", text="URL")
        self.treeview.heading("status", text="Estado")
        self.treeview.heading("elapsed", text="Ping")
        for item in self.list:
            self.table_entries.append(self.treeview.insert("", tk.END, text=item['url'], values=(
                item['status'], item['elapsed'])))
        self.treeview.pack(side=TOP)

    def setup(self):
        ttk.Style().configure('TFrame', background=self.bg)
        self.url_txt = StringVar()
        self.root.attributes("-type", "dialog")
        self.root.title("Pinged")
        self.root['bg'] = self.bg
        self.mainframe = ttk.Frame(self.root, padding="12 12 12 12")
        self.mainframe.pack(side='top', fill="both")
        ttk.Entry(self.mainframe, textvariable=self.url_txt).pack(
            side=LEFT, fill="both", expand=1)
        ttk.Button(self.mainframe, text="Guardar",
                   command=lambda: self.add_url()).pack(side=LEFT, padx=5)
        self.draw_table()
        self.treeview.bind("<Double-1>", self.onDoubleClick)
        self.exec_trheads()

    def onDoubleClick(self, event):
        key = self.treeview.selection()[0]
        index = self.table_entries.index(key)
        item = self.list[index]
        self.db.rm(item['url'])
        self.list.remove(item)
        self.treeview.delete(key)
        self.table_entries.remove(key)

    def get_item_index(self, url: str):
        for index, item in enumerate(self.list):
            if(item['url'] == url):
                return index
        return -1

    def update_table_entry(self, msg: Tuple[int, dict], db):
        index = msg[0]
        item = msg[1]
        logging.info("Updating fn %s", item['url'])
        db.update_latest(
            url=item['url'], status=item['status'], elapsed=item['elapsed'])
        self.treeview.item(self.table_entries[index], text=item['url'], values=(
            item["status"], item['elapsed']))
        logging.info("Updated %s", item['url'])

    def fetch(self, item: dict):
        url = item['url']
        try:
            logging.info("Fetching %s", url)
            res = requests.get(url)
            elapsed = res.elapsed.total_seconds() * 1000
            status = res.status_code
            logging.info("Fetched %s %i", url, status)
            return {'url': url, 'elapsed': elapsed, 'status': status}
        except:
            return {'url': url, 'elapsed': None, 'status': 404}

    def consumer(self, event: ThreadEvent, queue: Queue):
        db = DB("pinged.db")
        while not event.is_set() or not queue.empty():
            item = queue.get()
            self.update_table_entry(item, db)

    def producer(self, queue: Queue):
        while True:
            for index, item in enumerate(self.list):
                data = self.fetch(item)
                queue.put((index, data))
            sleep(30)

    def exec_trheads(self):
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.INFO,
                            datefmt="%H:%M:%S")
        pipeline = Queue(maxsize=10)
        event = ThreadEvent()
        threading.Thread(target=self.producer, args=(
            pipeline,), daemon=True).start()
        threading.Thread(target=self.consumer, args=(
            event, pipeline), daemon=True).start()
