# generateImageAndVideoReport
Script to recursivelly search for images and video, extract metadata, some video frames and generate a docx report

The initial goal was to process all img and video files, starting in one directory, import the images or several video frames, obtain an include the exif metadata and generate a docx document with all this information

Features:
* Moves recursively through all folders starting from the initial one.
* Detect images and video files with the following extensions:
** IMAGE: '.jpg', '.png', '.jfif', '.exif', '.gif', '.tiff', '.bmp'
** VIDEO: '.mp4', '.avi', '.mov', '.mpg', '.mpeg', '.wmv'
* Get exif information for each file
* Capture several frames for each video
* Put all this information together in a docx file

