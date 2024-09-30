## 🖊blogging

> A smart tool to help you to manage blogs

![screencast](/screencast.gif)

This cmdline tool was initially created to help managing [my own blog](http://cuyu.github.io), and it really saves my time. So I'd like to abstract the tool (suit for more scenario) here to benefit you!
***Note**: the tool is only tested on macOS, but it should work on Linux as well.*

### Installation & Setup

```bash
pip3 install github-blogging
```

Enable the auto-complete feature:

```bash
echo 'eval "$(register-python-argcomplete blogging)"' >> ~/.zshrc
```

#### Initial setup

For the first time you use the tool, you **must** do some settings (e.g. set the blog project root path). To get settings done, just type:

```
blogging
```

*Or you can manually create and edit the `~/.blogging` file.*


### How this tool can help you

#### Create a new blog

Assume you just get a good idea and want to write it down to the disk. So you will create a file and name it, and write some metadata like categories and tags at first.

With this tool, you just need to type one command, and it will do all the things above (it even opens the file automatically for you):

```sh
blogging new {title} {category} {tag1} {tag2}
```

#### Save drafts to cloud

The writing work is almost done, but you have something more urgent to handle. You feel not very safe to only save the file on the disk. So here, a single command will save all the drafts to the cloud (GitHub):

```sh
blogging save
```

#### Continue the writes

The urgent work is done, and you'd like to continue the writes just saved.

This tool gives you the convenience (just press `tab`, and pick from all the drafts) to open the draft:

```sh
blogging continue {file_name}
```

#### Publish the blog

The writes is done. You'd like to publish the blog to the web. To achieve this, you may need to move the file from the drafts folder to the publish folder and push the changes to the server side.

With `blogging`:

```sh
blogging publish {file_name}
```

#### Edit the published blog

The blog is published, and you'd like to edit the published blog again. However, you cannot remember the exact title of the blog. 

With `blogging`, you can open the published blog conveniently with `--filter` option. This option will search the title/category/tags of all published  blogs, and pop up (need to press `space` and  `tab`  after the keyword) candidate blogs in the terminal.

```sh
blogging edit --filter {keyword} {file_name}
```

The `--filter` is optional and is case-insensitive (i.e. 'Abc' works the same as 'abc').

#### Insert images

Sometimes, you may need to insert images into the blog. This tool can help you to insert images into the markdown file with correct url path and also move the images to the blog git repo (which can be uploaded to GitHub later when publishing).

```sh
blogging image {image_local_path} {file_name}
```

This command will generate the markdown image tag and add to your clipboard. You can paste it to the markdown file directly.

***Super easy, right?***

All you need to do is open your terminal and execute:

```sh
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
├── _images
│   ├── screenshot1.png
│   └── screenshot2.png
├── index.html
└── ...
```

All markdown files under `_posts` folder will be compiled into html files and hosted on your site. 

**The folder names above (e.g. `_posts`) can be configured when you use the tool for the first time*

### Compatibility

The supportability of auto complete feature is depend on [argcomplete](https://github.com/kislyuk/argcomplete).

### Known issue

- ~~Auto complete feature is not work when inputs contain unicode. (See this [issue](https://github.com/kislyuk/argcomplete/issues/228) for details)~~ (Fixed with a monkey patch)

- For zsh, it shows `command not found: complete`. To fix this, pls add following lines to your `~/.zshrc` file and source it:

  ```
  autoload bashcompinit
  bashcompinit
  ```



### TODO

- ~~Support more shell types~~
- ~~More flexible blog project structure (e.g. can customise the draft/publish folder name)~~
- ~~An option to open and edit published blogs, also support add `-filter` option to filter by word, category, tags, etc.~~
- ~~Add a gif screenshot to show this tool~~
- Cache the blogs' meta info to improve performance (For now, I have near 80 blogs, performance is not the bottleneck)

