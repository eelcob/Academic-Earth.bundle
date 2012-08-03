NAME = 'Academic Earth'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_SEARCH = 'icon-search.png'
ICON_MORE = "icon-more.png"

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
  # Search disabled for now since the search function doesn't work on the site itself
  #oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.academicearth", title = "Search...", prompt = "Search for Videos", thumb = R(ICON_SEARCH)))
  return oc

####################################################################################################
#ok
def Subjects():

	oc = ObjectContainer(title2 = "Subjects")
	page = HTML.ElementFromURL(BASE_URL + "/subjects/")

	for subject in page.xpath("//div[@class='menu']"):
		title = subject.xpath(".//a/text()")[0].strip()
	
		# We don't support Online Degrees and filter out subjects itself
		if 'Subjects' in title:
			continue
	
		oc.add(DirectoryObject(key = Callback(SubCatagory, title=title), title=title))

	return oc

####################################################################################################
#ok
def SubCatagory(title):

	oc = ObjectContainer(title2 = title)
	
	page = HTML.ElementFromURL(BASE_URL + "/subjects/")
	
	for sub in page.xpath("//div[@class='menu']"):
		subtitle = sub.xpath(".//a/text()")[0].strip()
		if subtitle == title:
			for subcata in sub.xpath(".//div/a"):
				subcatatitle = subcata.xpath(".//text()")[0].strip()
				subcatalink  = BASE_URL + subcata.xpath(".")[0].get('href')
				
				oc.add(DirectoryObject(key = Callback(ClipsperCatagory, url=subcatalink, title=subcatatitle), title=subcatatitle))
		
	return oc
	
####################################################################################################
#ok
def ClipsperCatagory(url, title, pagenr=1):

	oc = ObjectContainer(title2=title)
	
	page = HTML.ElementFromURL('%s/page:%d' % (url, pagenr))
	
	for subject in page.xpath("//div[@class='lecture']"):
		lectureurl = BASE_URL + subject.xpath(".//a")[0].get('href')
		title = subject.xpath(".//a/h3/text()")[0]
		thumb = subject.xpath(".//a/img")[1].get('src')

		oc.add(EpisodeObject(
			url = lectureurl,
			title = title,
			show = title,
			thumb = thumb
    ))

	if len(page.xpath('//a/span[@class="next"]')) > 0:
		oc.add(DirectoryObject(key=Callback(UniversitySubjects, url=url, pagenr=pagenr+1), title='More', thumb=R(ICON_MORE)))
	
	return oc
	
####################################################################################################
def Lectures(url, title):

  oc = ObjectContainer(title2=title)

  # It's possible that the given lecture URL will attempt to redirect to a new 'degree' section of 
  # their site. This requires separate authentication but is not supported by this plugin. We'll
  # therefore just filter these out.
  try: 
    page = HTML.ElementFromURL(url, follow_redirects = False)
  except Ex.RedirectError, e: 
    if e.location.startswith("http://academicearth.degreeamerica.com"):
      oc	= ObjectContainer(header = "No Videos", message = "There are no available videos")
      return oc
    else:
      page = HTML.ElementFromURL(url)

  for lecture in page.xpath("//div[@class='results-list']//li[@class='clearfix']"):
    lecture_url = BASE_URL + lecture.xpath(".//a")[0].get('href')
    episode_title = lecture.xpath(".//div[@class='description']/h4/a/text()")[0]
    summary = ''.join(lecture.xpath(".//div[@class='description']/p/text()")).strip()
    thumb = lecture.xpath(".//img[contains(@class, 'thumb')]")[0].get('src')
    if thumb.find('http://') == -1:
        thumb = BASE_URL + thumb	


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

######################################################z##############################################
#ok
def Universities(pagenr=1):

	oc = ObjectContainer(title2 = 'Universities')
	page = HTML.ElementFromURL('%s/universities/page:%d' % (BASE_URL, pagenr))
	university_section = page.xpath('//div[@class="lectureVideosIndex"]/div[@class="items"]')[0]
	for university in university_section.xpath('.//div'):
		url = BASE_URL + university.xpath('.//a')[0].get('href')
		title = university.xpath('.//a/text()')[1].strip()
		oc.add(DirectoryObject(key = Callback(UniversitySubjects, url = url), title = title))

	if len(page.xpath('//a/span[@class="next"]')) > 0:
		oc.add(DirectoryObject(key=Callback(Universities, pagenr=pagenr+1), title='More', thumb=R(ICON_MORE)))
	
	return oc

####################################################################################################
#ok
def UniversitySubjects(url, pagenr=1):

	oc = ObjectContainer(title2 = 'Subjects')
	
	page = HTML.ElementFromURL('%s/page:%d' % (url, pagenr))
	
	for subject in page.xpath("//div[@class='lecture']"):
		lectureurl = BASE_URL + subject.xpath(".//a")[0].get('href')
		title = subject.xpath(".//a/h3/text()")[0]
		thumb = subject.xpath(".//a/img")[1].get('src')

		oc.add(EpisodeObject(
			url = lectureurl,
			title = title,
			show = title,
			thumb = thumb
    ))

	if len(page.xpath('//a/span[@class="next"]')) > 0:
		oc.add(DirectoryObject(key=Callback(UniversitySubjects, url=url, pagenr=pagenr+1), title='More', thumb=R(ICON_MORE)))
	
	return oc

####################################################################################################
#ok
def Instructors():

	oc = ObjectContainer(title2 = "Instructors")
	page = HTML.ElementFromURL(BASE_URL + '/speakers/')

	for instructor_initial in page.xpath("//div[@class='add-link']//div/a"):
		url = BASE_URL + instructor_initial.get('href')
		title = instructor_initial.text
		Log.Debug(url)
		oc.add(DirectoryObject(key = Callback(InstructorsOfLetter, title=title, url=url), title=title))

	return oc

####################################################################################################
#ok
def InstructorsOfLetter(title, url, pagenr=1):

	oc = ObjectContainer(title2 = title)
	content = HTML.ElementFromURL('%s/page:%d' % (url, pagenr))
  
  	for instructor in content.xpath("//div[@class='blue-hover']"):
		instructor_url = BASE_URL + instructor.xpath(".//a")[0].get('href')
		instructor_title = instructor.xpath('.//a/div/text()')[0].strip()
		summary = instructor.xpath('.//a/div/text()')[1]

		oc.add(DirectoryObject(key = Callback(InstructorsVideos, url=instructor_url, instructor=instructor_title), title=instructor_title, summary=summary))
		
	if len(content.xpath('//a/span[@class="next"]')) > 0:
		oc.add(DirectoryObject(key=Callback(InstructorsOfLetter, title=title, url=url, pagenr=pagenr+1), title='More', thumb=R(ICON_MORE)))

	return oc

####################################################################################################
def InstructorsVideos(url, instructor):

  oc = ObjectContainer(title2 = instructor)
  content = HTML.ElementFromURL(url)

  for course in content.xpath("//h3[text()='Courses']/following-sibling::ol[1]/li"):
    course_url = BASE_URL + course.xpath(".//a")[0].get('href')
    course_title = course.xpath(".//div[@class='description']/h4/a/text()")[0]
    summary = course.xpath(".//span[@class='org']/text()")[0]
    thumb = course.xpath(".//div[@class='description-thumb']//img")[0].get('src')
    if thumb.find('http://') == -1:
        thumb = BASE_URL + thumb  

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
      thumb = lecture.xpath(".//img[contains(@class, 'thumb')]")[0].get('src')
      if thumb.find('http://') == -1:
        thumb = BASE_URL + thumb  

      oc.add(EpisodeObject(
        url = lecture_url,
        title = episode_title,
        summary = summary,
        thumb = thumb
      ))

      more = True

  # It seems that some advertised lecturers don't actually have any videos available
  if len(oc) == 0:
      oc = ObjectContainer(header = "Error", message = "There are no lecutures currently available")
          
  return oc
