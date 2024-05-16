# ReadAllComics-to-PDF-Downloader

This project is a Comic Downloader, which allows users to download comics from a specified [ReadAllComics](https://readallcomics.com). The downloaded comics are then converted into a PDF format for easy reading. The project uses Flask for the backend, Socket.IO for real-time updates, and APScheduler for scheduling tasks.

## Steps
Here are the steps to host this project:

1. Clone the repository from GitHub.
```sh
git clone https://github.com/m4xy07/ReadAllComics-to-PDF-Downloader.git
```

2. Navigate to the project directory.
```sh
cd ReadAllComics-to-PDF-Downloader
```

3. Install the required Python packages.
```sh
pip install -r requirements.txt
```

4. Run the Flask application.
```sh
python main.py
```

5. Open a web browser and navigate to `http://localhost:5000` to access the application.

Please note that this application is intended for local use. If you want to host it on a server, you may need to configure a production-ready server like Gunicorn or uWSGI and set up a reverse proxy with Nginx or Apache. 

*Also, ensure that you comply with the terms of service of the websites from which you are downloading comics.*

## License
This project is licensed under the [MIT License](LICENSE).

## Credits
This application is based on [RAD](https://github.com/Nighmared/RAD). Special thanks to [Nighmared](https://github.com/Nighmared)

## Improvements?
If you have anything you'd like to contribute feel free to open a pull request. 💖
