## 🖊blogging

> A smart tool to help you writing blogs

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

**Super easy, right?**

All you need to do is open your terminal and execute (not ready yet~):

```
pip install github-blogging
```

### Settings

For the first time you use the tool, you **must** set the blog project root path by:

```
blogging set-project-path {YOUR_PROJECT_PATH}
```

*Or you can manaully create and edit the `~/.blogging` file.*

### Compatibility

For now, only support the following shell:

- zsh

### TODO

- Support more shell types
- More flexible blog project structure (e.g. can customise the draft/publish folder name)
- An option to open and edit published blogs, also support add `-filter` option to filter by word, category, tags, etc.
- Add a gif screenshot to show this tool

