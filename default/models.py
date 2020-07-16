from google.cloud import ndb


class Userdata(ndb.Model):
    apikey = ndb.StringProperty()
    webhook = ndb.StringProperty()
