import os, glob, time, random
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from pattern.web import DOM

import shutil, requests

class Goguess(object):

    validFormats = ('*.png','*.jpg','*.jpeg', '*.bmp', '*.tiff')
    BASE_URL =  'http://www.google.com/searchbyimage/upload'

    def __init__(self, inputDir=None):
        """ search class to upload all the photos in input directory 
            and upload them to google and get the best guess from google
            * we can also use image url rather than upload the local file!
            but the performace will be the same!
            Args:
                inputDir which is the directory of input folder
        """         

    	self.query = ''
    	self.input_DIR = inputDir
        self.name = os.path.basename( self.input_DIR )

    	self.images = []
        self.urls = []
        self.guessList = []

        self.currentImagePath = None
        self.currentImageName = None

    	self.buildImagelist()

    def buildImagelist(self):
        """
        make a list of all imagefile in the input directory
        """
    	if not self.input_DIR:
    		raise 'no input directory defined'

    	for fileFormat in self.validFormats:
    		self.images.extend( glob.glob( os.path.join(self.input_DIR, fileFormat) ) )

    def updateQuery(self):
        """
        encode image to data and make the url to load with browser
        """
        multipart = {'encoded_image': (self.currentImagePath, open(self.currentImagePath, 'rb')), 'image_content': ''}
        try:
            r = requests.post(self.BASE_URL, files=multipart, allow_redirects=False)
            self.query = r.headers['Location']
        except requests.Timeout as err:
            print  err.message
        except requests.RequestException as err:
            print err

    def save(self):
        text_filename = os.path.join( self.name+ '_guess_list.txt' )
        with  open(text_filename, 'w') as f:
            for n in self.guessList:
                f.write( n )
                f.write('\n')


    def set_languageToEnglish(self):
        """
        if the first result was not in english, we switch to english
        * the rest will be in english!
        """
        try:
            english = self.driver.find_element_by_link_text('Change to English')
            english.click()
        except NoSuchElementException:
            pass

    def updateDataset(self, guess, pages):
        self.guessList.append( self.currentImageName + '\t' + guess + '\t' + '\t'.join(pages) )
        print self.currentImageName + ' processed!' + ' guess: ' + guess

    def updateProps(self, imagePath):
        """
        update what image needs to be processed
        """
        self.currentImagePath = imagePath
        self.currentImageName = os.path.basename(imagePath)
        self.updateQuery()

    def extractGuess(self, lang=False):

        #get the page content
        self.driver.get(self.query)
        #check if the language is not in english
        if lang:
            self.set_languageToEnglish()
            time.sleep(0.5)

        #make dom object of page source
        dom = DOM(self.driver.page_source)

        guess = []
        pages = []

        pageElements = dom('div.g h3.r a')
        guessElement = dom('a._gUb')

        for pageElement in pageElements:
            try:
                if self.isString( pageElement.content ):
                    pages.append( pageElement.content.encode('utf-8', 'ignore') )
            except:
                print 'page title not found!'

        for g in guessElement:
            try:
                guess.append( g.content )
            except: 
                print 'guess not found!'

        if len(guess)>0:
            guess = guess[0].encode('utf-8', 'ignore')
        else:
            guess = 'Null'

        #save results in
        self.updateDataset(guess, pages)

    def openBrowser(self):
        self.driver = webdriver.Firefox()

    def isString(self,s):
        return isinstance(s,str) or isinstance(s,unicode)

    def go(self):
        self.openBrowser()
        print self.name + ' start to proccess!'
        print 'estimate time:%d min' %(len(self.images)*2/60)
        for i, imagePath in enumerate(self.images):
            self.updateProps(imagePath)
            if i == 0:
                self.extractGuess(True)
            else:
                self.extractGuess()

            # time.sleep(0.5)
            time.sleep(random.uniform(1,2))
            print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> left:' + str( len(self.images) - i )

        self.save()
        self.driver.close()
        print self.name + ' is done!'
        print '#### ##### ####'
