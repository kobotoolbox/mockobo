# mockobo

Make mock submissions to a deployed KoBo form

> NOT WORKING FOR GROUPED QUESTIONS YET OR MEDIA-TYPE QUESTIONS

1. Setup

```
git clone https://github.com/joshuaberetta/mockobo
cd mockobo

python3 -m venv e
. e/bin/activate
pip3 install -r requirements.txt

chmod +x mockobo.py
```

2. Create config file in the root

`kobo.json`

```json
{
  "token": "YOUR_TOKEN",
  "kf_url": "https://kf.kobotoolbox.org",
  "kc_url": "https://kc.kobotoolbox.org"
}
```

3. Create submissions

```
./mockobo.py --asset-uid aLmmfWSAUNamKwiSTcVSix --count 42
```

Or

```
./mockobo.py -a aLmmfWSAUNamKwiSTcVSix -c 42
```

4. Use attachments

Add a video or audio file to your project, and run `mockobo` with `--media-file` option\
The format is `type`:`/path/to/the/file`

```
./mockobo.py -a aLmmfWSAUNamKwiSTcVSix -c 42 --media-file image:/path/to/mypicture.jpg
./mockobo.py -a aLmmfWSAUNamKwiSTcVSix -c 42 --media-file video:/path/to/myvideo.mp4
```

4. Use concurrency

By default, `mockobo` only uses 2 threads. Increasing the value for dev environments 
is almost useless since the Django dev server does not seem to handle it. 
On production, the gain is noticeable, especially when you want to create a 
large set of data.

**BE AWARE** to not flood the server.

```
./mockobo.py -a aLmmfWSAUNamKwiSTcVSix -c 42 -w 10
```
