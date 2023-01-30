# Image Grabber
Small tool to download automatically images from google

How to run:
1. Environment: make sure the environment have those libraries:
  * selenium
  * webdriver_manager
 the rest of the libraries are usually defaulted with python
 
2. To run the tool, you need a labels.json file that contains a label and its search query, this project has a default json file with labels from MCB project
   which can also be generated with the labels_gatherer.py but it requires the MCB project folder path

3. Run grabber.py and it will start downloading images to the folder 'download'. The grabber may stop due to some internet problems or too many requests that google deny. I this case run the tool again and it will start from the label it has not made a folder yet
