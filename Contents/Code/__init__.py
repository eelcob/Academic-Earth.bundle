import re

NAME = 'Academic Earth'#L('AcademicEarth')
ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_SEARCH = 'icon-search.png'

BASE_URL = "http://www.academicearth.org"

CACHE_TIME            = 1800

####################################################################################################

def Start():
  Plugin.AddPrefixHandler('/video/academicearth', MainMenu, NAME, ICON, ART)
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="video")

  ObjectContainer.title1 = NAME
  ObjectContainer.view_group = 'List'
  ObjectContainer.art = R(ART)
      
  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)
      
  HTTP.CacheTime = CACHE_TIME

####################################################################################################
  
def MainMenu():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key = Callback(Subjects), title = 'Subjects'))
  oc.add(DirectoryObject(key = Callback(Universities), title = 'Universities'))
  oc.add(DirectoryObject(key = Callback(Instructors), title = 'Instructors'))
  oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.academicearth", title = "Search", summary = "Search Description", prompt = "Search Prompt", thumb = R(ICON_SEARCH)))
  return oc

####################################################################################################

def Subjects():
  oc = ObjectContainer(title2 = "Subjects")
  page = HTML.ElementFromURL('http://academicearth.org/subjects/')

  for subject in page.xpath("//div[@class='institution-list']//li/a"):
    title = subject.text
    url = BASE_URL + subject.get('href')
    oc.add(DirectoryObject(key = Callback(Subject, url = url, title = title), title = title))

  return oc

def Subject(url, title):
  oc = ObjectContainer(title2 = title)
  page = HTML.ElementFromURL(url)
    
  for course in page.xpath("//div[@class='video-results']//div[@class='info']/.."):
    lectures_url = BASE_URL + course.xpath(".//a[@class='thumb']")[0].get('href')
    title = course.xpath(".//h3/a/text()")[0].strip()
    institution = ''.join(course.xpath(".//h4//text()")).strip()
    speakers = ''.join(course.xpath(".//h5//text()")).strip()
    thumb = BASE_URL + course.xpath(".//div[@class='thumb']//img")[0].get('src')

    summary = "Lectures: %s\n\n%s" % (speakers, institution)
      
    oc.add(DirectoryObject(
      key = Callback(Lectures, url = lectures_url, title = title), 
      title = title, 
      summary = summary, 
      thumb = thumb))

  return oc

def Lectures(url, title):
  oc = ObjectContainer(title2 = title)
  page = HTML.ElementFromURL(url)
    
  for lecture in page.xpath("//div[@class='results-list']//li[@class='clearfix']"):
    lecture_url = BASE_URL + lecture.xpath(".//a")[0].get('href')
    episode_title = lecture.xpath(".//div[@class='description']/h4/a/text()")[0]
    summary = ''.join(lecture.xpath(".//div[@class='description']/p/text()")).strip()
    thumb = BASE_URL + lecture.xpath(".//img[contains(@class, 'thumb')]")[0].get('src')
    
    index = None
    try: index = int(re.match(".*Lecture (?P<index>[0-9]+) -.*").groupdict()['index'])
    except: pass
    episode_title = episode_title[episode_title.index('-') + 1:].strip()
      
    oc.add(EpisodeObject(
      url = lecture_url,
      title = episode_title,
      index = index,
      show = title,
      summary = summary,
      thumb = thumb))

  return oc

####################################################################################################

def Universities():
  oc = ObjectContainer(title2 = "Universities")
  page = HTML.ElementFromURL('http://academicearth.org/universities/')

  for university in page.xpath("//div[@class='institution-list']//li"):
    url = BASE_URL + university.xpath(".//a")[0].get('href')
    title = university.xpath(".//a/text()")[0]
    oc.add(DirectoryObject(key = Callback(UniversitySubjects, url = url), title = title))
    
  return oc

def UniversitySubjects(url):
  oc = ObjectContainer(title2 = "Subjects")
  page = HTML.ElementFromURL(url)
    
  for subject in page.xpath("//div[@class='results-side']//li"):
    url = BASE_URL + subject.xpath(".//a")[0].get('href')
    title = subject.xpath(".//a/text()")[0]
    title = title[:title.index('(')].strip()
    oc.add(DirectoryObject(key = Callback(Subject, url = url, title = title), title = title))
    
  return oc

####################################################################################################

def Instructors():
  oc = ObjectContainer(title2 = "Instructors")
  page = HTML.ElementFromURL('http://academicearth.org/speakers/')
    
  for instructor in page.xpath("//ul[@class='professors-list']//li/a"):
    url = BASE_URL + instructor.get('href')
    title = instructor.text
    oc.add(DirectoryObject(key = Callback(InstructorsVideos, url = url, instructor = title), title = title))

  return oc

def InstructorsVideos(url, instructor):
  oc = ObjectContainer(title2 = instructor)
  page = HTML.ElementFromURL(url)
    
  for lecture in page.xpath("//div[@class='results-list']//ol[@class='child-lists']/li"):
    url = lecture.xpath(".//a")[0].get('href')
    if url.startswith("/lectures/") == False:
      continue
      
    url = BASE_URL + url
    episode_title = lecture.xpath(".//img[contains(@class, 'thumb')]")[0].get('alt')
    summary = lecture.xpath(".//span[@class='org']/text()")[0]
    thumb = BASE_URL + lecture.xpath(".//img[contains(@class, 'thumb')]")[0].get('src')   

    oc.add(EpisodeObject(
      url = url,
      title = episode_title,
      summary = summary,
      thumb = thumb))

  return oc