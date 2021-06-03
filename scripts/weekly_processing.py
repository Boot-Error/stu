import csv
import os
import sys
import argparse
import logging
import glob
import json
import subprocess
import concurrent.futures
from dataclasses import dataclass
from typing import List


@dataclass(unsafe_hash=True)
class AuthorMeta:
    id: str
    secUid: str
    name: str
    nickName: str
    verified: str
    signature: str
    avatar: str
    following: str
    fans: str
    heart: int
    video: int
    digg: int


@dataclass(unsafe_hash=True)
class MusicMeta:
    musicId: str
    musicName: str
    musicAuthor: str
    musicOriginal: str
    musicAlbum: str
    playUrl: str
    coverThumb: str
    coverMedium: str
    coverLarge: str
    duration: int


@dataclass(unsafe_hash=True)
class Covers:
    default: str
    origin: str
    dynamic: str


@dataclass(unsafe_hash=True)
class VideoMeta:
    height: int
    width: int
    duration: int


@dataclass
class Tiktok:
    id: str
    secretID: str
    text: str
    createTime: str
    authorMeta: AuthorMeta
    musicMeta: MusicMeta
    covers: Covers
    webVideoUrl: str
    videoUrl: str
    videoUrlNoWaterMark: str
    videoApiUrlNoWaterMark: str
    videoMeta: VideoMeta
    diggCount: int
    shareCount: int
    playCount: int
    commentCount: int
    downloaded: int
    mentions: int
    hashtags: str
    effectStickers: str

    def __post_init__(self):
        self.videoMeta = VideoMeta(**self.videoMeta)
        self.authorMeta = AuthorMeta(**self.authorMeta)
        self.musicMeta = MusicMeta(**self.musicMeta)
        
    def __hash__(self):
        return hash(self.id)


def TiktokFromDict(tiktok_dict):
    modified = {}
    for k, v in tiktok_dict.items():

        # if k in ["hashtags", "mentions", "effectStickers"]:
        #     modified.setdefault(k, json.loads(v))
        #     continue

        if "." in k:
            root, key = k.split(".")
            if root not in modified:
                modified.setdefault(root, {key: v})
            else:
                modified[root].setdefault(key, v)
            continue

        modified.setdefault(k, v)

    return Tiktok(**modified)


def get15MinuteVideoContent(tiktoks):
    tiktoks = sorted(tiktoks, key=lambda tk: tk.playCount, reverse=True)
    queued = []
    totalPlaytime = 0
    for tk in tiktoks:
        totalTime = totalPlaytime + int(tk.videoMeta.duration)
        if totalTime > (15 * 60):
            break
        queued.append(tk)
        totalPlaytime = totalTime

    return tiktoks


def tiktokScraper(*args, cwd=None):
    proc = subprocess.run(("tiktok-scraper",) + args)
    return proc


def downloadVideos(tiktoks):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {}
        for tk in tiktoks:
            future = executor.submit(
                tiktokScraper,
                "video", tk.webVideoUrl, "-d",
                cwd="videos"
            )
            futures.setdefault(tk, future)

        for tk, future in futures.items():
            try:
                result = future.result()
                logging.info("Downloaded {}".format(tk.webVideoUrl))
            except Exception as e:
                logging.exception(e)
                logging.error(
                    "Failed to download video {}".format(tk.webVideoUrl))


def readCsvFile(filepath: str) -> List[Tiktok]:
    tiktoks = []
    logging.debug("Reading csv file {}".format(filepath))
    with open(filepath, mode='r', encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            logging.debug(row)
            tiktok = TiktokFromDict(row)
            tiktoks.append(tiktok)

    return tiktoks


def loadTiktokData(datadir: str) -> List[Tiktok]:
    tiktoks = []
    csv_files = glob.glob(os.path.join(datadir, "*.csv"))
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for csv_file in csv_files:
            futures.append(
                executor.submit(readCsvFile, filepath=csv_file)
            )
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                tiktoks.extend(result)
            except Exception as e:
                logging.exception(e)

    return tiktoks


def main(args):
    if args.debug:
        logging.setLogLevel("debug")
    data_dir = os.path.join(args.week, "trend")
    if not os.path.exists(data_dir):
        logging.error("Directory {} doesn't exist".format(data_dir))

    tiktoks = loadTiktokData(data_dir)
    videoContentTiktoks = get15MinuteVideoContent(tiktoks)
    downloadVideos(tiktoks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates videos for weekly trending uploads"
    )

    parser.add_argument('--week', type=str, required=True, help="week dir")
    parser.add_argument('--debug', default=False,
                        action="store_true", help="week dir")
    args = parser.parse_args()
    main(args)
