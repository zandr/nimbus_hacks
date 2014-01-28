if __name__ == "__main__":

    import time
    import json
    from datetime import datetime, timedelta
    from ConfigParser import ConfigParser
    from httplib2 import Http

    try:
        import wink
    except ImportError as e:
        import sys
        sys.path.insert(0, "..")
        import wink

    def is_tide(x):
        return 'Tide' in x['data']['type']

    def get_tides(url, key, location):
        yesterday = datetime.now() - timedelta(days=1)
        h = Http()
        resp, tides_json = h.request("%s/%s/tide_%s/q/%s.json" % (url, key, yesterday.strftime('%Y%m%d'), location))
        tides = json.loads(tides_json)
        tidelist = filter(is_tide, tides['tide']['tideSummary'])
        
        resp, levels_json = h.request("%s/%s/rawtide/q/%s.json" % (url, key, location))
        levels = json.loads(levels_json)
        
        return (tidelist, levels)

    w = wink.init("../config.cfg")

    if "cloud_clock" not in w.device_types():
        raise RuntimeError(
            "you do not have a cloud_clock associated with your account!"
        )
    c = w.cloud_clock()

    print "found cloud_clock %s called %s!" % (c.id, c.data.get("name"))

    config = ConfigParser()
    config.read('tides.cfg')
    wu_key = config.get('Wunderground', 'key')
    wu_url = config.get('Wunderground', 'url')
    wu_location = config.get('Wunderground', 'location')

    (tidelist, levels) = get_tides(wu_url, wu_key, wu_location)

    while tidelist:
        for i in tidelist:
            tide_epoch = int(i['date']['epoch'])
            if tide_epoch >= time.time():
                tide_duration = tide_epoch - last_tide_epoch
                position = ((time.time() - last_tide_epoch) / tide_duration) * 180
                tide_type = i['data']['type']
                if "High" in tide_type:
                    position += 180
                tide_height = "%s\'" % (i['data']['height'].partition(' ')[0])
                tide_time = "%02d:%02d" % (int(i['date']['hour']), int(i['date']['min']))
                break
            else:
                last_tide_epoch = tide_epoch

        for i in levels['rawtide']['rawTideObs']:
            if i['epoch'] >= time.time():
                level = i['height']
                break

        dial=c.dials()[3]
        original=dial.get_config()
        new_config=original
        new_config['dial_configuration']['num_ticks']=360
        labels = [level, tide_height]
        dial.update((dict(
            channel_configuration=dict(channel_id="10"),
            name="Tides",
            dial_configuration=new_config['dial_configuration'],
            label="%.2f\'" % level,
            labels=[("%.2f\'" % level), ("%s" % tide_height)],
            value=position
            )))

        time.sleep(60)
