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
  "kf_url": "https://kf.kobotoolbox.org"
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

