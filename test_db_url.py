import dj_database_url
print("dj_database_url imported successfully")
conf = dj_database_url.config(default='sqlite:///')
print("Config:", conf)
