# encoding: utf-8
from __future__ import print_function

import os
import json
import requests
import argparse
import concurrent.futures

from pybooru import Moebooru


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--data_dir', type=str, default='data')
    parser.add_argument('--output_fn', type=str, default='sakugabooru_list.json')
    parser.add_argument('--url', type=str, default='https://sakugabooru.com')
    parser.add_argument('--resume_from', type=int, default=None)
    parser.add_argument('--page_limit', type=int, default=None)
    parser.add_argument('--n_process', type=int, default=8)

    return parser.parse_args()


def initialize_idx_json(args):
    json_path = os.path.join(args.data_dir, args.output_fn)

    if args.resume_from and os.path.isfile(json_path):
        page = args.resume_from
        with open(json_path, 'r') as f:
            json_list = json.load(f)
    else:
        json_list = []
        page = 1

    return page, json_list, json_path


def log_skip(e, page):
    print()
    print(str(e))
    print(f'--> Skipping page at {page}')


def request_save(url, save_fp):
    img_data = requests.get(url, timeout=5).content
    with open(save_fp, 'wb') as handler:
        handler.write(img_data)


if __name__ == '__main__':
    args = parse_args()

    LIMIT = 1000
    DEBUG_PAGE_LIMIT = 2

    # Page index for iteration
    page, json_list, json_path = initialize_idx_json(args)

    # Instance for crawling sakugabooru (Moebooru has the same sitemap structure with it)
    sakugabooru = Moebooru(site_url=args.url)

    while True:
        print(f"Getting {page}'th page, total {len(json_list)} tags collected", end='\r')

        url_list = []
        save_fp_list = []

        # Make directory for current page if not exist
        video_dir = os.path.join(args.data_dir, str(page))
        if not os.path.isdir(video_dir):
            os.mkdir(video_dir)
        
        # POST request : crawling website
        try:
            posts = sakugabooru.post_list(limit=LIMIT, page=page)
        except Exception as e:
            log_skip(e, page)

            if args.page_limit and page >= args.page_limit:
                break
            page += 1
            continue

        # Break the loop if no more images are returned
        if not posts:
            break

        for i, post in enumerate(posts):
            json_list.append(post)

            if post['file_url']:
                url_list.append(post['file_url'])

                extension = os.path.splitext(post['file_url'])[1]
                save_fp = os.path.join(video_dir, str(post['id']) + extension)
                save_fp_list.append(save_fp)

            if i >= DEBUG_PAGE_LIMIT: break

        # Save JSON file
        with open(json_path, 'w') as f:
            json.dump(json_list, f)

        # Queue process for crawling video files
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.n_process) as executor:
            future_to_url = {executor.submit(request_save, url, fp) for url, fp in zip(url_list, save_fp_list)}

        if args.page_limit and page >= args.page_limit:
            break
        page += 1
