# generateImageAndVideoReport
Script to recursivelly search for images and video, extract metadata, some video frames and generate a docx report

The initial goal was to process all img and video files, starting in one directory, import the images or several video frames, obtain an include the exif metadata and generate a docx document with all this information

We also include the ability to insert all data processed in a MongoDB database for further analysis.

Features:
* Moves recursively through all folders starting from the initial one.
* Detect images and video files with the following extensions:
** IMAGE: '.jpg', '.png', '.jfif', '.exif', '.gif', '.tiff', '.bmp'
** VIDEO: '.mp4', '.avi', '.mov', '.mpg', '.mpeg', '.wmv'
* Get exif information for each file with ExifTool (https://exiftool.org/).
* Capture several frames for each video.
* Put all this information together in a docx file.
* Insert the data in a MongoDB database with the following schema:
** Project: Defined when executed
** Files: File data associated to a schema
** Metadata: All metadata for each file
* Progress bar
* Total count of documents processed

