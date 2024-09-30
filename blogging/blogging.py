#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import html
import os
import datetime
import re
from subprocess import call
import sys
from tabulate import tabulate
import codecs
import argcomplete
import time
from termcolor import colored
from blogging.constants import __VERSION__, BLOGGING_SETTINGS_FILE
import struct


class UnknownImageFormat(Exception):
    pass


def copy2clip(txt):
    cmd = f"echo '{txt.strip()}'|pbcopy"
    return call(cmd, shell=True)


def get_image_size(file_path):
    """
    Return (width, height) for a given img file content - no external
    dependencies except the os and struct modules from core
    """
    size = os.path.getsize(file_path)

    with open(file_path, 'rb') as input:
        height = -1
        width = -1
        data = input.read(25)

        if (size >= 10) and data[:6] in (b'GIF87a', b'GIF89a'):
            # GIFs
            w, h = struct.unpack("<HH", data[6:10])
            width = int(w)
            height = int(h)
        elif ((size >= 24) and data.startswith(b'\211PNG\r\n\032\n')
              and (data[12:16] == b'IHDR')):
            # PNGs
            w, h = struct.unpack(">LL", data[16:24])
            width = int(w)
            height = int(h)
        elif (size >= 16) and data.startswith(b'\211PNG\r\n\032\n'):
            # older PNGs?
            w, h = struct.unpack(">LL", data[8:16])
            width = int(w)
            height = int(h)
        elif (size >= 2) and data.startswith(b'\377\330'):
            # JPEG
            msg = " raised while trying to decode as JPEG."
            input.seek(0)
            input.read(2)
            b = input.read(1)
            try:
                while (b and b[0] != 0xDA):
                    while (b[0] != 0xFF): b = input.read(1)
                    while (b[0] == 0xFF): b = input.read(1)
                    if (b[0] >= 0xC0 and b[0] <= 0xC3):
                        input.read(3)
                        h, w = struct.unpack(">HH", input.read(4))
                        break
                    else:
                        input.read(int(struct.unpack(">H", input.read(2))[0]) - 2)
                    b = input.read(1)
                width = int(w)
                height = int(h)
            except struct.error:
                raise UnknownImageFormat("StructError" + msg)
            except ValueError:
                raise UnknownImageFormat("ValueError" + msg)
            except Exception as e:
                raise UnknownImageFormat(e.__class__.__name__ + msg)
        else:
            raise UnknownImageFormat(
                "Sorry, don't know how to get information from this file."
            )

    return width, height


def validate_settings():
    if hasattr(SETTINGS, 'PROJECT_PATH') and hasattr(SETTINGS, 'DRAFTS_FOLDER') and hasattr(SETTINGS, 'POSTS_FOLDER') \
            and hasattr(SETTINGS, 'IMAGES_FOLDER'):
        return True
    else:
        return False


def add_to_clipboard(text):
    from tkinter import Tk
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append('some string')
    r.update()
    time.sleep(.2)
    r.update()
    r.destroy()


def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(s).strip().replace(' ', '-')
    return re.sub(r"[\~\#\%\&\*\{\}\\\:\<\>\?\/\+\|]", '', s)


def get_valid_title(s):
    """
    Escape characters when used as html parsing.
    E.g. `<` to `&lt;`
    """
    return html.escape(s)


class Settings(object):
    def __init__(self, setting_path):
        self.PROJECT_PATH = None
        if os.path.isfile(setting_path):
            with open(setting_path, 'r') as f:
                for line in f:
                    k, v = line.split('=')
                    setattr(self, k.upper(), v.strip())


SETTINGS = Settings(BLOGGING_SETTINGS_FILE)


def _get_meta_info(path=None):
    if path is None:
        path = SETTINGS.POSTS_FOLDER
    info = dict()
    for file_name in os.listdir(os.path.join(SETTINGS.PROJECT_PATH, path)):
        if file_name.startswith('.'):
            continue
        info[file_name] = dict()
        with codecs.open(os.path.join(SETTINGS.PROJECT_PATH, path, file_name), 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if first_line.startswith('---'):
                while True:
                    line = f.readline()
                    if line.startswith('title:'):
                        title = line[6:].strip()
                        info[file_name]['title'] = title
                    elif line.startswith('category:'):
                        category = line[9:].strip()
                        info[file_name]['category'] = category
                    elif line.startswith('tags:'):
                        tag_list = line[5:].strip()[1:-1].split(',')
                        tag_list = [tag.strip() for tag in tag_list]
                        info[file_name]['tag'] = tag_list
                    if line.startswith('---'):
                        break
    return info


def _list_meta_info(path=None):
    if path is None:
        path = SETTINGS.POSTS_FOLDER
    result = dict()
    categories = dict()
    tags = dict()
    titles = dict()
    result['category'] = categories
    result['tag'] = tags
    result['title'] = titles
    info = _get_meta_info(path)
    for file_name in info:
        category = info[file_name].get('category')
        tag_list = info[file_name].get('tag')
        title = info[file_name]['title']
        if category:
            if category in categories:
                categories[category] += 1
            else:
                categories[category] = 1
        if tag_list:
            for tag in tag_list:
                tag = tag.strip()
                if tag in tags:
                    tags[tag] += 1
                else:
                    tags[tag] = 1
        titles[title] = file_name
    return result


def stats_categories():
    result = _list_meta_info()
    table = []
    all_categories = list(result['category'].keys())
    all_categories.sort()
    for c in all_categories:
        table.append([c, result['category'][c]])
    print(tabulate(table, headers=['Category', 'Count']))


def stats_tags():
    result = _list_meta_info()
    table = []
    all_tags = list(result['tag'].keys())
    all_tags.sort()
    for c in all_tags:
        table.append([c, result['tag'][c]])
    print(tabulate(table, headers=['Tag', 'Count']))


class FileCompleter(object):
    def __init__(self, path):
        drafts_path = os.path.join(SETTINGS.PROJECT_PATH, path)
        if os.path.isdir(drafts_path):
            file_names = os.listdir(os.path.join(SETTINGS.PROJECT_PATH, path))
        else:
            file_names = []
        self.choices = [name for name in file_names if not name.startswith('.')]

    def __call__(self, prefix, parsed_args, **kwargs):
        return (c for c in self.choices if c.startswith(prefix))


class FileCompleterWithFilter(FileCompleter):
    def __init__(self, path):
        super(FileCompleterWithFilter, self).__init__(path)
        self.info = _get_meta_info(path)

    def __call__(self, prefix, parsed_args, **kwargs):
        if parsed_args.filter:
            keyword = parsed_args.filter[0]
            results = self.filter_by_keyword(keyword)
        else:
            results = self.choices
        return (c for c in results if c.startswith(prefix))

    def filter_by_keyword(self, keyword):
        results = []
        keyword_lower = keyword.lower()
        for filename in self.info:
            meta_data = self.info[filename]
            if (meta_data.get('category') and keyword_lower == meta_data.get('category').lower()) \
                    or keyword_lower in meta_data['title'].lower() \
                    or (meta_data.get('tag') and keyword_lower in [tag.lower() for tag in meta_data.get('tag')]):
                results.append(filename)
        return results


def CategoryCompleter(prefix, **kwargs):
    result = _list_meta_info()
    all_categories = list(result['category'].keys())
    return (c for c in all_categories if c.startswith(prefix))


def TagCompleter(prefix, **kwargs):
    result = _list_meta_info()
    all_tags = list(result['tag'].keys())
    return (c for c in all_tags if c.startswith(prefix))


#################################################################
# To register with argcompletion, run following command:        #
#   eval "$(register-python-argcomplete blogging)"              #
#################################################################
def parse_arguments():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=colored('blogging ({0})\n'.format(__VERSION__), 'cyan') +
                                                 'A simple tool to create new blogging file.\n' +
                                                 'Use example: ./blogging new "post_title" category tag1 tag2\n')
    subparsers = parser.add_subparsers(help='Use {subcommand} -h for each subcommand\'s optional arguments details',
                                       dest='command')

    create_parser = subparsers.add_parser('new', help='Create new blogging')
    create_parser.add_argument('post_title', help='Title of the blog')
    create_parser.add_argument('category', help='The category of the blog').completer = CategoryCompleter
    create_parser.add_argument('tags', help='The tag list of the blog, separate by space',
                               nargs="*").completer = TagCompleter

    ls_parser = subparsers.add_parser('ls', help='List exist stats')
    ls_parser.add_argument('list_content', choices=['categories', 'tags'])

    save_parser = subparsers.add_parser('save', help='Save all the drafts and changes of edited posts to the Github')

    continue_parser = subparsers.add_parser('continue', help='Open one draft and continue the writing')
    continue_parser.add_argument('--filter', action='store', nargs=1,
                                 help='Filter posts by keywords in title/tag/category')
    continue_parser.add_argument('draft_file', help='File name of the draft').completer = FileCompleterWithFilter(
        SETTINGS.DRAFTS_FOLDER)

    publish_parser = subparsers.add_parser('publish', help='Publish the post to the Github')
    publish_parser.add_argument('draft_file', help='File name of the draft').completer = FileCompleter(
        SETTINGS.DRAFTS_FOLDER)

    image_parser = subparsers.add_parser('image', help='Rename and save the image to the Github')
    image_parser.add_argument('image_path', help='Path of the image file')
    image_parser.add_argument('draft_file', help='Title of the blog in draft').completer = FileCompleter(
        SETTINGS.DRAFTS_FOLDER)

    edit_parser = subparsers.add_parser('edit', help='Open one published post and edit')
    edit_parser.add_argument('--filter', action='store', nargs=1, help='Filter posts by keywords in title/tag/category')
    edit_parser.add_argument('post_file', help='File name of the post').completer = FileCompleterWithFilter(
        SETTINGS.POSTS_FOLDER)

    argcomplete.autocomplete(parser, always_complete_options=False)
    args = parser.parse_args()

    if args.command == 'new':
        post_name = args.post_title
        post_tags = '[' + ', '.join(args.tags) + ']'
        today = datetime.date.today()
        file_name = str(today) + '-' + get_valid_filename(post_name) + '.md'
        post_name = get_valid_title(post_name)
        content = """---
layout: post
title: "{title}"
category: {category}
tags: {tags}
date: {date}
---""".format(title=post_name, date=str(today), category=args.category, tags=post_tags)

        draft_path = os.path.join(SETTINGS.PROJECT_PATH, SETTINGS.DRAFTS_FOLDER, '{0}'.format(file_name))
        with open(draft_path, 'w') as f:
            f.write(content)
        print("\"{0}\" has been created under _drafts folder.".format(file_name))
        call(['open', draft_path])
    elif args.command == 'ls':
        if args.list_content == 'categories':
            stats_categories()
        elif args.list_content == 'tags':
            stats_tags()
    elif args.command == 'publish':
        os.chdir(SETTINGS.PROJECT_PATH)
        # Rename the file name and the date in meta header then commit to Github
        draft_path = os.path.join(SETTINGS.PROJECT_PATH, SETTINGS.DRAFTS_FOLDER, args.draft_file)
        new_name = str(datetime.date.today()) + args.draft_file[10:]
        post_path = os.path.join(SETTINGS.PROJECT_PATH, SETTINGS.POSTS_FOLDER, new_name)
        changed_date = False
        with open(post_path, 'w') as in_file:
            with open(draft_path, 'r') as out_file:
                for line in out_file:
                    if not changed_date and line.startswith('date:'):
                        changed_date = True
                        line = 'date: {0}\n'.format(str(datetime.date.today()))
                    in_file.write(line)
        call(['git', 'add', post_path])
        call(['git', 'rm', '-f', draft_path])
        # If the draft has not been saved to github, the above cmd will do nothing
        # So here we check if the draft is still exist and remove if exist
        if os.path.isfile(draft_path):
            os.remove(draft_path)
        call(['git', 'commit', '-m', 'Publish post: {0}'.format(args.draft_file)])
        call(['git', 'push'])
    elif args.command == 'save':
        os.chdir(SETTINGS.PROJECT_PATH)
        all_drafts = os.path.join(SETTINGS.PROJECT_PATH, SETTINGS.DRAFTS_FOLDER, '*')
        all_posts = os.path.join(SETTINGS.PROJECT_PATH, SETTINGS.POSTS_FOLDER, '*')
        call(['git', 'add', all_drafts])
        call(['git', 'add', all_posts])
        call(['git', 'commit', '-m', 'Save drafts and edited posts'])
        call(['git', 'push'])
    elif args.command == 'continue':
        draft_path = os.path.join(SETTINGS.PROJECT_PATH, SETTINGS.DRAFTS_FOLDER, args.draft_file)
        call(['open', draft_path])
    elif args.command == 'image':
        image_extension = args.image_path.split('.')[-1]
        image_name = args.draft_file.replace('.md', '') + '.' + image_extension
        image_width, image_height = get_image_size(args.image_path)
        image_url = SETTINGS.IMAGES_FOLDER.replace(SETTINGS.PROJECT_PATH, '') + '/' + image_name
        image_url = image_url if image_url.startswith('/') else '/' + image_url
        index = 1
        while os.path.isfile(os.path.join(SETTINGS.PROJECT_PATH, SETTINGS.IMAGES_FOLDER, image_name)):
            image_name = args.draft_file.replace('.md', '') + '-{0}'.format(index) + '.' + image_extension
            index += 1
        call(['cp', args.image_path, os.path.join(SETTINGS.PROJECT_PATH, SETTINGS.IMAGES_FOLDER, image_name)])
        os.chdir(SETTINGS.PROJECT_PATH)
        call(['git', 'add', os.path.join(SETTINGS.PROJECT_PATH, SETTINGS.IMAGES_FOLDER, image_name)])
        image_tag = '''<img title="{0}" src="{1}" width="{2}" />
<span class="caption">REPLACEME</span>'''.format(
            image_name, image_url, image_width)
        print(image_tag)
        print('Above image tags has been copied to clipboard.')
        # Add to clipboard
        copy2clip(image_tag)
    elif args.command == 'edit':
        post_path = os.path.join(SETTINGS.PROJECT_PATH, SETTINGS.POSTS_FOLDER, args.post_file)
        call(['open', post_path])


def input_until_valid_path(validate_func, retry=3):
    line = sys.stdin.readline().strip()
    while not validate_func(line) and retry > 0:
        print('Please input a exist path:')
        line = sys.stdin.readline().strip()
        retry -= 1

    if validate_func(line):
        return line
    else:
        print(colored('Path still not valid. Exiting...', 'red'))
        exit(1)


def main():
    if validate_settings():
        parse_arguments()
    else:
        print('This seems your first time using this tool')
        print('Before playing the tool, there are some settings must be set')
        print(colored('[1] Your blog project full path:', 'magenta'))
        project_path = input_until_valid_path(os.path.isdir)

        print(colored('[2] Folder to put your drafts:', 'magenta'))
        drafts_folder = input_until_valid_path(lambda name: name and os.path.isdir(os.path.join(project_path, name)))

        print(colored('[3] Folder to put your published blogs:', 'magenta'))
        posts_folder = input_until_valid_path(lambda name: name and os.path.isdir(os.path.join(project_path, name)))

        print(colored('[4] Folder to put images of your blog:', 'magenta'))
        images_folder = input_until_valid_path(lambda name: name and os.path.isdir(os.path.join(project_path, name)))

        with open(BLOGGING_SETTINGS_FILE, 'w') as f:
            f.write('project_path={0}\n'.format(project_path))
            f.write('drafts_folder={0}\n'.format(drafts_folder))
            f.write('posts_folder={0}\n'.format(posts_folder))
            f.write('images_folder={0}\n'.format(images_folder))
        print(colored('Configration done. Enjoy the tool~', 'green'))


if __name__ == '__main__':
    main()
