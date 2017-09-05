## 🖊blogging

> A smart tool to help you managing blogs

![screencast](/screencast.gif)

This cmdline tool was initially created to help managing [my own blog](http://cuyu.github.io) and it really saves my time. So I'd like to abstract the tool (suit for more scenario) here to benefit you!

### How this tool can help you

#### Scenario 1

Assume you just get a good idea and want to write it down to the disk. So you will create a file and name it, and write some metadata like categories and tags at first.

With this tool, you just need to type one command and it will do all the things above (it even opens the file automatically for you):

```
blogging new {title} {category} {tag1} {tag2}
```

#### Scenario 2

The writing work is almost done, but you have something more urgent to handle. You feel not very safe to only save the file on the disk. So here, a single command will save all the drafts to the cloud (Github):

```
blogging save
```

#### Scenario 3

The urgent work is done and you'd like to continue the writes just saved.

This tool gives you the convenience (just press `tab`, and pick from all the drafts) to open the draft:

```
blogging continue {file_name}
```

#### Scenario 4

The writes is done. You'd like to publish the blog to the web. To achieve this, you may need to move the file from draft folder to the publish folder and push the changes to the server side.

With `blogging`:

```
blogging publish {file_name}
```

#### Scenario 5

The blog is published and you'd like to edit the published blog again. However you cannot remeber the exact title of the blog. 

With `blogging`, you can open the published blog conveniently with `--filter` option. This option will search the title/category/tags of all published  blogs, and pop up (need to press `space` and  `tab`  after the keyword) candidate blogs in the terminal.

```
blogging edit --filter {keyword} {file_name}
```

The `--filter` is optional and is case insensesitve (i.e. 'Abc' works the same as 'abc').

**Super easy, right?**

All you need to do is open your terminal and execute:

```
pip install github-blogging
```

**To enable the auto-complete (press `tab`) feature, you need to open a new shell session after installation.*

### File structures

This tool assume you have the following file structures for the blog project:

```
YOUR_PROJECT_PATH
├── _drafts
│   ├── first_draft.md
│   ├── second_draft.md
│   └── third_draft.md
├── _posts
│   ├── first_blog.md
│   ├── second_blog.md
│   └── third_blog.md
├── index.html
└── ...
```

All markdown files under `_posts` folder will be compiled into html files and hosted on your site. 

### Settings

For the first time you use the tool, you **must** set the blog project root path by:

```
blogging set-project-path {YOUR_PROJECT_PATH}
```

*Or you can manaully create and edit the `~/.blogging` file.*

### Compatibility

The supportability of auto complete feature is depend on [argcomplete](https://github.com/kislyuk/argcomplete).

### Known issue

Auto complete feature is not work when inputs contain unicode. (See this [issue](https://github.com/kislyuk/argcomplete/issues/228) for details)

### TODO

- ~~Support more shell types~~
- More flexible blog project structure (e.g. can customise the draft/publish folder name)
- ~~An option to open and edit published blogs, also support add `-filter` option to filter by word, category, tags, etc.~~
- ~~Add a gif screenshot to show this tool~~
- Cache the blogs' meta info to improve performance (For now, I have near 80 blogs, performance is not the bottleneck)

