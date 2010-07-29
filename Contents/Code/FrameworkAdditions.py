from PMS import HTTP, XML

def XMLElementFromURL(url, useHtmlParser=False, cacheTime=0):
  if cacheTime == 0:
    return XML.ElementFromURL(url, useHtmlParser)
  else:
    return XML.ElementFromString(HTTP.GetCached(url, cacheTime), useHtmlParser)