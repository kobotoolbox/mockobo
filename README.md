# mksubs

Make random submissions to a KoBo form

> NOT WORKING FOR GROUPED QUESTIONS YET OR MEDIA-TYPE QUESTIONS

1. Setup

```
git clone https://github.com/joshuaberetta/mksubs
cd mksubs

python3 -m venv e
. e/bin/activate
pip3 install -r requirements.txt

chmod +x mksubs.py
```

2. Create config file in the root

__kobo.json__

```json
{
  "token": "YOUR_TOKEN",
  "kc_url": "https://kc.kobotoolbox.org"
}
```

3. Create submissions

```
./mksubs.py --asset-uid aLmmfWSAUNamKwiSTcVSix --count 42
```

Or

```
./mksubs.py -a aLmmfWSAUNamKwiSTcVSix -c 42
```

