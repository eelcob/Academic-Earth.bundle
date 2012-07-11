NAME = 'Academic Earth'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_SEARCH = 'icon-search.png'

BASE_URL = "http://www.academicearth.org"
SPEAKER_LECTURES = '%s/speakers/ajax_speakers_get_more_lectures/%%s/%%d' % BASE_URL

RE_INDEX = Regex("Lecture (?P<index>[0-9]+) -")

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

  HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
def MainMenu():

  oc = ObjectContainer()
  oc.add(DirectoryObject(key = Callback(Subjects), title = 'Subjects'))
  oc.add(DirectoryObject(key = Callback(Universities), title = 'Universities'))
  oc.add(DirectoryObject(key = Callback(Instructors), title = 'Instructors'))
  oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.academicearth", title = "Search...", prompt = "Search for Videos", thumb = R(ICON_SEARCH)))
  return oc

####################################################################################################
def Subjects():

  oc = ObjectContainer(title2 = "Subjects")
  page = HTML.ElementFromURL('http://academicearth.org/subjects/')

  for subject in page.xpath("//a[@class='subj-links']"):
    title = subject.xpath(".//div/text()")[0].strip()
    url = BASE_URL + subject.get('href')

    # We don't support Online Degrees
    if '/onlinedegreeprograms' in url:
      continue

    oc.add(DirectoryObject(key = Callback(Subject, title=title, url=url), title=title))

  return oc

####################################################################################################
def Subject(title, url, page=1):

  oc = ObjectContainer(title2 = title)
  content = HTML.ElementFromURL('%s/page:%d' % (url, page))

  for course in content.xpath("//div[@id='tab_content']//div[@class='info']/.."):
    course_url = BASE_URL + course.xpath(".//a[@class='thumb']")[0].get('href')
    course_title = course.xpath(".//img[not(@class='play-icon')]")[0].get('alt')
    thumb = course.xpath(".//div[@class='thumb']//img[not(@class='play-icon')]")[0].get('src')
    if thumb.find('http://') == -1:
        thumb = BASE_URL + thumb
   
    summary = course.xpath(".//div[@class='info']//div/a[1]")[0].text
	
    if '/courses/' in course_url:
      oc.add(DirectoryObject(
        key = Callback(Lectures, url=course_url, title=title),
        title = course_title,
        summary = summary,
        thumb = thumb
      ))
    else:
      oc.add(VideoClipObject(
        url = course_url,
        title = course_title,
        summary = summary,
        thumb = thumb
      ))

  if len(content.xpath('//a/span[text()="next page"]')) > 0:
    oc.add(DirectoryObject(key = Callback(Subject, title=title, url=url, page=page+1), title='Next ...'))

  return oc

####################################################################################################
def Lectures(url, title):

  oc = ObjectContainer(title2=title)
  page = HTML.ElementFromURL(url)

  for lecture in page.xpath("//div[@class='results-list']//li[@class='clearfix']"):
    lecture_url = BASE_URL + lecture.xpath(".//a")[0].get('href')
    episode_title = lecture.xpath(".//div[@class='description']/h4/a/text()")[0]
    summary = ''.join(lecture.xpath(".//div[@class='description']/p/text()")).strip()
    thumb = BASE_URL + lecture.xpath(".//img[contains(@class, 'thumb')]")[0].get('src')

    try: index = int(RE_INDEX.search(episode_title).group('index'))
    except: index = None

    if index is not None:
      episode_title = episode_title.split(' - ', 1)[1]

    oc.add(EpisodeObject(
      url = lecture_url,
      title = episode_title,
      index = index,
      show = title,
      summary = summary,
      thumb = thumb
    ))

  return oc

####################################################################################################
def Universities():

  oc = ObjectContainer(title2 = "Universities")
  page = HTML.ElementFromURL('http://academicearth.org/universities/')
  university_section = page.xpath("//div[contains(@class, 'box-border-main')]")[0]

  for university in university_section.xpath(".//a[@class='subj-links']"):
    url = BASE_URL + university.get('href')
    title = university.xpath(".//div/text()")[0].strip()
    oc.add(DirectoryObject(key = Callback(UniversitySubjects, url = url), title = title))

  return oc

####################################################################################################
def UniversitySubjects(url):

  oc = ObjectContainer(title2 = "Subjects")
  page = HTML.ElementFromURL(url)

  for subject in page.xpath("//div[@class='tab-container']//li"):
    url = BASE_URL + subject.xpath(".//a")[0].get('href')
    title = subject.xpath(".//a/text()")[0]
    oc.add(DirectoryObject(key = Callback(Subject, title=title, url=url), title=title))

  return oc

####################################################################################################
def Instructors():

  oc = ObjectContainer(title2 = "Instructors")
  page = HTML.ElementFromURL('http://academicearth.org/speakers/')

  for instructor_initial in page.xpath("//div[@class='tab-container']//a[contains(@class, 'tab-details-link')]"):
    url = BASE_URL + instructor_initial.get('href')
    title = instructor_initial.text

    if 'All Names' in title:
      continue

    oc.add(DirectoryObject(key = Callback(InstructorsOfLetter, title=title, url=url), title=title))

  return oc

####################################################################################################
def InstructorsOfLetter(title, url, page=1):

  oc = ObjectContainer(title2 = title)
  content = HTML.ElementFromURL('%s/page:%d' % (url, page))
  instructor_section = content.xpath("//div[@class='tab-container']/div")[2]

  for instructor in instructor_section.xpath(".//a"):
    instructor_url = BASE_URL + instructor.get('href')
    instructor_title = instructor.xpath('.//div/text()')[0]
    summary = instructor.xpath('.//div/text()')[1]

    oc.add(DirectoryObject(
      key = Callback(InstructorsVideos, url=instructor_url, instructor=instructor_title),
      title = instructor_title,
      summary = summary
    ))

  if len(content.xpath('//a/span[text()="next page"]')) > 0:
    oc.add(DirectoryObject(key = Callback(InstructorsOfLetter, title=title, url=url, page=page+1), title='Next ...'))

  return oc

####################################################################################################
def InstructorsVideos(url, instructor):

  oc = ObjectContainer(title2 = instructor)
  content = HTML.ElementFromURL(url)

  for course in content.xpath("//h3[text()='Courses']/following-sibling::ol[1]/li"):
    course_url = BASE_URL + course.xpath(".//a")[0].get('href')
    course_title = course.xpath(".//div[@class='description']/h4/a/text()")[0]
    summary = course.xpath(".//span[@class='org']/text()")[0]
    thumb = BASE_URL + course.xpath(".//div[@class='description-thumb']//img")[0].get('src')

    oc.add(DirectoryObject(
      key = Callback(Lectures, url=course_url, title=course_title),
      title = course_title,
      summary = summary,
      thumb = thumb
    ))

  name = url.rsplit('/',1)[1]
  start = 0
  items = 20

  more = True
  while more is True:
    url = SPEAKER_LECTURES % (name, start*items)
    start = start+1
    content = HTML.ElementFromURL(url)
    more = False

    for lecture in content.xpath("//ol/li"):
      lecture_url = BASE_URL + lecture.xpath(".//a")[0].get('href')
      episode_title = lecture.xpath(".//div[@class='description']/h4/a/text()")[0]
      summary = lecture.xpath(".//span[@class='org']/text()")[0].strip(' /')
      thumb = BASE_URL + lecture.xpath(".//img[contains(@class, 'thumb')]")[0].get('src')

      oc.add(EpisodeObject(
        url = lecture_url,
        title = episode_title,
        summary = summary,
        thumb = thumb
      ))

      more = True

  # It seems that some advertised lecturers don't actually have any videos available
  if len(oc) == 0:
    return MessageContainer("Error", "There are no lecutures currently available.")

  return oc
