from PMS import Plugin, Log, HTTP, FileTypes
from PMS.MediaXML import *
from PMS.Shorthand import _L, _R, _E, _D

from FrameworkAdditions import *

####################################################################################################

AE_PLUGIN_PREFIX      = "/video/AcademicEarth"
AE_ART_NAME           = None
AE_URL                = "http://www.academicearth.org"
AE_UNIVERSITIES_KEY   = "/universities"
AE_INSTRUCTORS_KEY    = "/speakers"
AE_UNI_SUBJECTS_URL   = "%s/universities/%%s/category:/" % AE_URL

CACHE_TIME            = 1800
VIDEO_BITRATE         = "500"

XP_INST_LIST          = "//div[@class='institution-list']/ul/li//a"
XPATH_UNI_SUBJECTS    = "//div[@class='results-side']/ul/li/a"

XP_VIDEO              = "//div[@class='video-results']//div[@class='info']/parent::*"
XPATH_VIDEO_THUMBS    = "//div[@class='video-results']/ol/li/div[@class='thumb']/a[@class='thumb']/img"

####################################################################################################

class AEMenuContainer(MediaContainer):
  def __init__(self, art="art-default.png", viewGroup="Menu", title1=None, title2=None, noHistory=False, replaceParent=False):
    if title1 is None:
      title1 = _L("AcademicEarth")
    MediaContainer.__init__(self, art, viewGroup, title1, title2, noHistory, replaceParent)

####################################################################################################

def Start():
  Plugin.AddRequestHandler(AE_PLUGIN_PREFIX, HandleRequest, _L("AcademicEarth"), "icon-default.png", "art-default.png")
  Plugin.AddViewGroup("Menu", viewMode="List", contentType="items")
  Plugin.AddViewGroup("Video", viewMode="InfoList", contentType="video")

####################################################################################################
  
def HandleRequest(pathNouns, count):
  
  if count == 0:
    return MainMenu().ToXML()
  
  elif pathNouns[0] == "search":
    if count == 2:
      return SearchResultsPage("%s/lectures/search/%s" % (AE_URL, pathNouns[1])).ToXML()
  
  elif pathNouns[0] == "spage":
    if count == 2:
      return SearchResultsPage(_D(pathNouns[1])).ToXML()
  
  elif pathNouns[0] == "inlist":
    if count == 4:
      return InstitutionListMenu(_D(pathNouns[1]), _D(pathNouns[2]), title2=_D(pathNouns[3])).ToXML()
  elif pathNouns[0] == "rpage":
    if count == 4:
      return ResultsPageMenu(_D(pathNouns[1]), _D(pathNouns[2]), _D(pathNouns[3])).ToXML()
  
  elif pathNouns[0] == "courses":
    if count == 2:
      (key, t1, t2) = pathNouns[1].split("$")
      return CoursePageMenu(key, t1, t2).ToXML()

  elif pathNouns[0] == "lectures":
    if count == 2:
      return LecturePlaylist(pathNouns[1])
    
  elif pathNouns[0] == "toprated":
    if count == 1:
      return TopRatedMenu().ToXML()
    elif pathNouns[1] == "instructors":
      dir = AEMenuContainer(title2=_L("TopRatedI"))
      for instructor in XMLElementFromURL(AE_URL, True, CACHE_TIME).xpath("//a[@id='professors']/../..//li/a"):
        dir.AppendItem(DirectoryItem("%s/instructors/%s$%s$%s" % (AE_PLUGIN_PREFIX, instructor.get("href").split('/')[2], _E(_L("TopRatedI")), _E(instructor.text)), instructor.text))
      return dir.ToXML()
    elif pathNouns[1] == "courses":
      dir = AEMenuContainer(title2=_L("TopRatedC"), viewGroup="Video")
      for course in XMLElementFromURL(AE_URL, True, CACHE_TIME).xpath("//a[@id='courses'][1]/../following-sibling::div/ol/li"):
        url = course.xpath("h3/a")[0].get("href")
        title = course.xpath("h3/a")[0].text
        h4 = course.xpath("h4")[0].xpath("a")
        subtitle = "%s / %s" % (h4[0].text, h4[1].text)
        summary = course.xpath("h5/a")[0].text
        item = DirectoryItem("%s/courses/%s$%s$%s/" % (AE_PLUGIN_PREFIX, _E(url), _E(_L("TopRatedC")), _E(title)), title, summary=summary)
        item.SetAttr("subtitle", subtitle)
        dir.AppendItem(item)
      return dir.ToXML()
    elif pathNouns[1] == "lectures":
      dir = AEMenuContainer(title2=_L("TopRatedL"), viewGroup="Video")
      for lecture in XMLElementFromURL(AE_URL, True, CACHE_TIME).xpath("//a[@id='lectures'][1]/../following-sibling::div/ol/li"):
        url = lecture.xpath("h3/a")[0].get("href")
        title = lecture.xpath("h3/a")[0].text
        h4 = lecture.xpath("h4")[0].xpath("a")
        subtitle = "%s / %s" % (h4[0].text, h4[1].text)
        summary = lecture.xpath("h5/a")[0].text
        item = VideoItem("%s/lectures/%s.flv" % (AE_PLUGIN_PREFIX, _E(url)), title, summary, "", "")
        item.SetAttr("subtitle", subtitle)
        item.SetAttr("bitrate", VIDEO_BITRATE)
        dir.AppendItem(item)
      return dir.ToXML()
      
  elif pathNouns[0] == "subjects":
    if count == 2:
      (key, title) = pathNouns[1].split("$")
      return ResultsPageMenu("%s/subjects/%s" % (AE_URL, key), _L("Subjects"), _D(title)).ToXML()
      
  elif pathNouns[0] == "instructors":
    if count == 1:
      dir = AEMenuContainer(title2=_L("Instructors"))
      for instructor in XMLElementFromURL(AE_URL + AE_INSTRUCTORS_KEY, True, CACHE_TIME).xpath("//ul[@class='professors-list']//a"):
        dir.AppendItem(DirectoryItem("%s/instructors/%s$%s$%s" % (AE_PLUGIN_PREFIX, instructor.get("href").split('/')[2], _E(_L("Instructors")), _E(instructor.text)), instructor.text))
      return dir.ToXML()
    else:
      (key, title1, title2) = pathNouns[1].split("$")
      if count == 2:
        (key, title1, title2) = pathNouns[1].split("$")
        dir = AEMenuContainer(title1=_D(title1), title2=_D(title2))
        dir.AppendItem(DirectoryItem("courses", _L("Courses")))
        dir.AppendItem(DirectoryItem("lectures", _L("Lectures")))
        return dir.ToXML()
      elif pathNouns[2] == "courses":
        dir = AEMenuContainer(title1=_D(title2), title2=_L("Courses"), viewGroup="Video")
        for course in XMLElementFromURL("%s%s/%s" % (AE_URL, AE_INSTRUCTORS_KEY, key), True, CACHE_TIME).xpath("//div[@class='results-list']//h3[1]/following-sibling::ol[1]/li"):
          link = course.xpath("div/h4/a")[0]
          thumb = AE_URL + course.xpath("div/a/img")[0].get("src")
          subtitle = course.xpath("div/span[@class='org']")[0].text
          summary = course.xpath("div/span[@class='author']/a")[0].text
          item = DirectoryItem("%s/courses/%s$%s$%s" % (AE_PLUGIN_PREFIX, _E(link.get("href")), title2, _E(link.text)), link.text, thumb=thumb, summary=summary)
          item.SetAttr("subtitle", subtitle)
          dir.AppendItem(item)
        return dir.ToXML()
      elif pathNouns[2] == "lectures":
        dir = AEMenuContainer(title1=_D(title2), title2=_L("Lectures"), viewGroup="Video")
        for course in XMLElementFromURL("%s%s/%s" % (AE_URL, AE_INSTRUCTORS_KEY, key), True, CACHE_TIME).xpath("//div[@class='results-list']//h3[2]/following-sibling::ol[1]/li"):
          link = course.xpath("div/h4/a")[0]
          thumb = AE_URL + course.xpath("div/a/img[@class='thumb-144']")[0].get("src")
          subtitle = course.xpath("div/span[@class='org']")[0].text
          summary = course.xpath("div/span[@class='author']/a")[0].text
          item = VideoItem("%s/lectures/%s.flv" % (AE_PLUGIN_PREFIX, _E(link.get("href"))), link.text, summary, "", thumb)
          item.SetAttr("subtitle", subtitle)
          item.SetAttr("bitrate", VIDEO_BITRATE)
          dir.AppendItem(item)
        return dir.ToXML()
      
  elif pathNouns[0] == "universities":
    if count == 1:
      return UniversitiesMenu().ToXML()
    else:
      (key, title) = pathNouns[1].split('$')
      if count == 2:
        return UniversityMenu(_D(pathNouns[1].split('$')[1])).ToXML()
      elif pathNouns[2] == "subjects":
        if count == 3:
          return UniSubjectsMenu(key, _D(title)).ToXML()
        else:
          (subj, title2) = pathNouns[3].split('$')
          if count == 4:
            return ResultsPageMenu("%s/%s/%s" % (AE_URL + AE_UNIVERSITIES_KEY, key, subj), _D(title), _D(title2)).ToXML()
      elif pathNouns[2] == "featured":
        return ResultsPageMenu("%s/%s/featured:" % (AE_URL + AE_UNIVERSITIES_KEY, key), _D(title), _L("Featured")).ToXML()
      elif pathNouns[2] == "mostviewed":
        return ResultsPageMenu("%s/%s/featured:impressions" % (AE_URL + AE_UNIVERSITIES_KEY, key), _D(title), _L("MostViewed")).ToXML()
      elif pathNouns[2] == "toprated":
        return ResultsPageMenu("%s/%s/featured:ratings" % (AE_URL + AE_UNIVERSITIES_KEY, key), _D(title), _L("TopRated")).ToXML()
      
  
####################################################################################################

def MainMenu():
  dir = AEMenuContainer()
  dir.AppendItem(DirectoryItem("toprated",     _L("TopRated")))
  dir.AppendItem(DirectoryItem("%s/inlist/%s/%s/%s" % (AE_PLUGIN_PREFIX, _E("/universities"), _E("/universities"), _E(_L("Universities"))), _L("Universities")))
  dir.AppendItem(DirectoryItem("%s/inlist/%s/%s/%s" % (AE_PLUGIN_PREFIX, _E("/subjects"), _E("/subjects"), _E(_L("Subjects"))), _L("Subjects")))
  dir.AppendItem(DirectoryItem("instructors",  _L("Instructors")))
  #dir.AppendItem(DirectoryItem("playlists",    _L("Playlists")))
  dir.AppendItem(SearchDirectoryItem("search", _L("Search"), _L("SearchPrompt")))
  return dir

####################################################################################################
  
def TopRatedMenu():
  dir = AEMenuContainer()
  dir.AppendItem(DirectoryItem("courses",      _L("TopRatedC")))
  dir.AppendItem(DirectoryItem("lectures",     _L("TopRatedL")))
  dir.AppendItem(DirectoryItem("instructors",  _L("TopRatedI")))
  #dir.AppendItem(DirectoryItem("playlists",    _L("TopRatedP")))
  return dir
  
####################################################################################################

def InstitutionListMenu(key, prefix, title1=None, title2=None):
  dir = AEMenuContainer(title1=title1, title2=title2)
  for item in XMLElementFromURL(AE_URL + key, useHtmlParser=True, cacheTime=CACHE_TIME).xpath(XP_INST_LIST):
    dir.AppendItem(DirectoryItem("%s%s/%s$%s" % (AE_PLUGIN_PREFIX, prefix, item.get("href").split("/")[-1], _E(item.text)), item.text))
  return dir

####################################################################################################

def UniversityMenu(title):
  dir = AEMenuContainer(title1=_L("Universities"), title2=title)
  dir.AppendItem(DirectoryItem("subjects",     _L("Subjects")))
  dir.AppendItem(DirectoryItem("featured",     _L("Featured")))
  dir.AppendItem(DirectoryItem("mostviewed",   _L("MostViewed")))
  dir.AppendItem(DirectoryItem("toprated",     _L("TopRated")))
  return dir

####################################################################################################

def UniSubjectsMenu(key, title):
  dir = AEMenuContainer(title1=title, title2=_L("Subjects"))
  Log.Add(key)
  for subject in XMLElementFromURL(AE_UNI_SUBJECTS_URL % key, useHtmlParser=True, cacheTime=CACHE_TIME).xpath(XPATH_UNI_SUBJECTS):
    title = subject.text
    i = title.find("(")
    if i > -1:
      title = title[:i]
    dir.AppendItem(DirectoryItem("%s$%s" % (subject.get("href").split("/")[-1], _E(title)), subject.text))
  return dir

####################################################################################################

def ResultsPageMenu(url, title1=None, title2=None):
  dir = AEMenuContainer(title1=title1, title2=title2, viewGroup="Video")
  Log.Add(url)
  page = XMLElementFromURL(url, useHtmlParser=True, cacheTime=CACHE_TIME)
  for video in page.xpath(XP_VIDEO):
    h3 = video.xpath("div[@class='info']/h3/a")[0]
    summary = video.xpath("div[@class='info']/h5/a")[0].text.strip().replace("  ", " ")
    subtitleParts = video.xpath("div[@class='info']/h4/a")
    subtitle = "%s / %s" % (subtitleParts[0].text, subtitleParts[1].text)
    thumb = AE_URL + video.xpath("div/a[@class='thumb']/img[@class='thumb-144']")[0].get("src")
    url = h3.get("href")
    if url.find("/courses/") > -1:
      item = DirectoryItem("%s/courses/%s$%s$%s" % (AE_PLUGIN_PREFIX, _E(url), _E(title2), _E(h3.text)), h3.text, thumb=thumb)
    elif url.find("/lectures/") > -1:
      item = VideoItem("%s/lectures/%s" % (AE_PLUGIN_PREFIX, "%s.flv" % _E(url)), h3.text, "", "", thumb)
      item.SetAttr("bitrate", VIDEO_BITRATE)
    item.SetAttr("subtitle", subtitle)
    item.SetAttr("summary", summary)
    dir.AppendItem(item)
  try:
    link = page.xpath("//ul[@class='pagination']/li/a")[0]
    if link.text == ">":
      dir.AppendItem(DirectoryItem("%s/rpage/%s/%s/%s" % (AE_PLUGIN_PREFIX, _E(AE_URL + link.get("href")), _E(title1), _E(title2)), _L("NextPage")))
  except:
    pass
  return dir

####################################################################################################

def CoursePageMenu(key, title1=None, title2=None):
  dir = AEMenuContainer(title1=_D(title1), title2=_D(title2), viewGroup="Video")
  xml = XMLElementFromURL(AE_URL + _D(key), useHtmlParser=True, cacheTime=CACHE_TIME)
  results = xml.xpath("//div[@class='results-list']")[0]
  fbar = xml.xpath("id('feature-bar')/div/h2/a")
  subtitle = "%s / %s" % (fbar[1].text, fbar[0].text)
  summary = results.xpath("p")[0].text
  
  for lecture in results.xpath("ol/li"):
    link = lecture.xpath("div/h4/a")[0]
    thumb = AE_URL + lecture.xpath("a/img[@class='thumb-144']")[0].get("src")
    key = "%s/lectures/%s.flv" % (AE_PLUGIN_PREFIX, _E(link.get("href")))
    item = VideoItem(key, link.text, summary, "", thumb)
    item.SetAttr("subtitle", subtitle)
    item.SetAttr("bitrate", VIDEO_BITRATE)
    dir.AppendItem(item)
  
  return dir
  
####################################################################################################

def LecturePlaylist(key):
  xml = XMLElementFromURL(AE_URL + _D(key[:-4]), useHtmlParser=True, cacheTime=CACHE_TIME)
  script = xml.xpath("id('main')/div/script")[0].text
  script = script[script.find("flvURL = \"")+10:]
  url = script[:script.find("\"")]
  return Plugin.Redirect(url)
  
####################################################################################################

def SearchResultsPage(url):
  dir = AEMenuContainer(title2=_L("Search"), viewGroup="Video")
  page = XMLElementFromURL(url, True, CACHE_TIME)
  for result in page.xpath("//div[@id='results-container-std']//ol[@class='child-lists']/li"):
    h4 = result.xpath("div/h4/a")[0]
    url = AE_URL + h4.get("href")
    title = h4.text
    thumb = AE_URL + result.xpath("div/a/img[@class='thumb-144']")[0].get("src")
    subtitleParts = result.xpath("div[@class='description']/span[@class='org']/a")
    subtitle = "%s / %s" % (subtitleParts[0].text, subtitleParts[1].text)
    summary = result.xpath("div[@class='description']/span[@class='author']/a")[0].text
    item = VideoItem("%s/lectures/%s.pls" % (AE_URL, _E(url)), title, summary, "", thumb)
    item.SetAttr("subtitle", subtitle)
    item.SetAttr("bitrate", VIDEO_BITRATE)
    dir.AppendItem(item)
  try:
    for element in page.xpath("//ul[@class='pagination']/li/a"):
      if element.text == ">":
        dir.AppendItem(DirectoryItem("%s/spage/%s" % (AE_PLUGIN_PREFIX, _E(AE_URL + element.get("href"))), _L("NextPage")))
  except:
    pass
  return dir