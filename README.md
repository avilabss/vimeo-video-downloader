# Vimeo Video Downloader
A simple python implementation for downloading videos from [Vimeo](https://vimeo.com/) 

# External Dependency
Download and Install [MKVToolNix](https://www.fosshub.com/MKVToolNix.html) and set it as path

# How to use
1. Open the video
2. Open **Dev Tools** in your browser by pressing **F12**
3. Switch to **Network** tab
4. Give page a refresh and play the video
5. In the search bar write **master.json**
6. Click on the result that has **master.json**
7. Under **Headers > General** you will find **Request URL**
8. Make sure it ends with **/master.json?base64_init=1**
9. Copy that url and use it as the value for **master_url**
10. Run the script: **python vimeo_downloader.py https://...**

# To-Do
- Implement quality selector, Downloades with max quality as of now
