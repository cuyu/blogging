#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import cgi
import os
import datetime
import re
from subprocess import call
from tabulate import tabulate
import codecs
import argcomplete
from Tkinter import Tk
import time
from termcolor import colored
from constants import __VERSION__, BLOGGING_SETTINGS_FILE


def add_to_clipboard(text):
    # this function seems not work for me?
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
    return cgi.escape(s)


class Settings(object):
    def __init__(self, setting_path):
        self.PROJECT_PATH = None
        if os.path.isfile(setting_path):
            with open(setting_path, 'r') as f:
                for line in f:
                    k, v = line.split('=')
                    setattr(self, k.upper(), v.strip())

    def __getattribute__(self, item):
        if item == 'PROJECT_PATH':
            assert object.__getattribute__(self,
                                           item), 'Please set the project path firstly\n E.g. blogging set-project-path [YOUR_BLOG_PATH]'
        return object.__getattribute__(self, item)


SETTINGS = Settings(BLOGGING_SETTINGS_FILE)


def _get_meta_info(path='_posts'):
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


def _list_meta_info(path='_posts'):
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
    all_categories = result['category'].keys()
    all_categories.sort()
    for c in all_categories:
        table.append([c, result['category'][c]])
    print tabulate(table, headers=['Category', 'Count'])


def stats_tags():
    result = _list_meta_info()
    table = []
    all_tags = result['tag'].keys()
    all_tags.sort()
    for c in all_tags:
        table.append([c, result['tag'][c]])
    print tabulate(table, headers=['Tag', 'Count'])


class FileCompleter(object):
    def __init__(self, path):
        try:
            drafts_path = os.path.join(SETTINGS.PROJECT_PATH, path)
        except AssertionError:
            file_names = []
        else:
            if os.path.isdir(drafts_path):
                file_names = os.listdir(os.path.join(SETTINGS.PROJECT_PATH, path))
            else:
                file_names = []
        self.choices = [name.decode('utf-8') for name in file_names if not name.startswith('.')]

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
                results.append(filename.decode('utf-8'))
        return results


def CategoryCompleter(prefix, **kwargs):
    # FIXME: there is a bug (of argcomplete) that when `blogging new '的' `, then tab is not work as expect, the reason should be the unicode in cmd
    result = _list_meta_info()
    all_categories = result['category'].keys()
    return (c for c in all_categories if c.startswith(prefix))


def TagCompleter(prefix, **kwargs):
    result = _list_meta_info()
    # Sorting is not work as it is controlled by the bash side
    # See https://github.com/kislyuk/argcomplete/issues/129 for details
    all_tags = result['tag'].keys()
    return (c for c in all_tags if c.startswith(prefix))


#################################################################
# To register with argcompletion, run following command:        #
#   eval "$(register-python-argcomplete blogging)"              #
#################################################################
def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=colored('blogging ({0})\n'.format(__VERSION__), 'cyan') +
                                                 'A simple tool to create new blogging file.\n' +
                                                 'Use example: ./blogging new "post_title" category tag1 tag2\n')
    subparsers = parser.add_subparsers(help='Use {subcommand} -h for each subcommand\'s optional arguments details',
                                       dest='command')
    set_parser = subparsers.add_parser('set-project-path', help='Configure the project path')
    set_parser.add_argument('project_path', help='Path of your blog project')

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
        '_drafts')

    publish_parser = subparsers.add_parser('publish', help='Publish the post to the Github')
    publish_parser.add_argument('draft_file', help='File name of the draft').completer = FileCompleter('_drafts')

    image_parser = subparsers.add_parser('image', help='Rename and save the image to the Github')
    image_parser.add_argument('image_path', help='Path of the image file')
    image_parser.add_argument('draft_file', help='Title of the blog in draft').completer = FileCompleter('_drafts')

    edit_parser = subparsers.add_parser('edit', help='Open one published post and edit')
    edit_parser.add_argument('--filter', action='store', nargs=1, help='Filter posts by keywords in title/tag/category')
    edit_parser.add_argument('post_file', help='File name of the post').completer = FileCompleterWithFilter('_posts')

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

        draft_path = os.path.join(SETTINGS.PROJECT_PATH, '_drafts', '{0}'.format(file_name))
        with open(draft_path, 'w') as f:
            f.write(content)
        print "\"{0}\" has been created under _drafts folder.".format(file_name)
        call(['open', draft_path])
    elif args.command == 'ls':
        if args.list_content == 'categories':
            stats_categories()
        elif args.list_content == 'tags':
            stats_tags()
    elif args.command == 'publish':
        os.chdir(SETTINGS.PROJECT_PATH)
        # Rename the file name and the date in meta header then commit to Github
        draft_path = os.path.join(SETTINGS.PROJECT_PATH, '_drafts', args.draft_file)
        new_name = str(datetime.date.today()) + args.draft_file[10:]
        post_path = os.path.join(SETTINGS.PROJECT_PATH, '_posts', new_name)
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
        all_drafts = os.path.join(SETTINGS.PROJECT_PATH, '_drafts', '*')
        all_posts = os.path.join(SETTINGS.PROJECT_PATH, '_posts', '*')
        call(['git', 'add', all_drafts])
        call(['git', 'add', all_posts])
        call(['git', 'commit', '-m', 'Save drafts and edited posts'])
        call(['git', 'push'])
    elif args.command == 'set-project-path':
        with open(BLOGGING_SETTINGS_FILE, 'w') as f:
            f.write('project_path={0}\n'.format(args.project_path))
    elif args.command == 'continue':
        draft_path = os.path.join(SETTINGS.PROJECT_PATH, '_drafts', args.draft_file)
        call(['open', draft_path])
    elif args.command == 'image':
        image_extension = args.image_path.split('.')[-1]
        image_name = args.draft_file.replace('.md', '') + '.' + image_extension
        index = 1
        while os.path.isfile(os.path.join(SETTINGS.PROJECT_PATH, 'images', image_name)):
            image_name = args.draft_file.replace('.md', '') + '-{0}'.format(index) + '.' + image_extension
            index += 1
        call(['mv', args.image_path, os.path.join(SETTINGS.PROJECT_PATH, 'images', image_name)])
        os.chdir(SETTINGS.PROJECT_PATH)
        call(['git', 'add', os.path.join(SETTINGS.PROJECT_PATH, 'images', image_name)])
        print '/images/{0}'.format(image_name)
        # TODO: add image path to clipboard
    elif args.command == 'edit':
        post_path = os.path.join(SETTINGS.PROJECT_PATH, '_posts', args.post_file)
        call(['open', post_path])


if __name__ == '__main__':
    main()
