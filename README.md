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


## Hosting

To host the `ReadAllComics-to-PDF-Downloader` project on an Ubuntu VPS, follow these steps:

1. Connect to your VPS via SSH.
```sh
ssh username@your_vps_ip
```

2. Update your package lists for upgrades and new package installations.
```sh
sudo apt-get update
```

3. Install Git, Python, and pip.
```sh
sudo apt-get install git python3 python3-pip
```

4. Clone the repository from GitHub.
```sh
git clone https://github.com/m4xy07/ReadAllComics-to-PDF-Downloader.git
```

5. Navigate to the project directory.
```sh
cd ReadAllComics-to-PDF-Downloader
```
Note before the next step you may need to create a virtual env 1. `apt install python3.11-venv` 2. `python3 -m venv venv` 3. `source venv/bin/activate`

6. Install the required Python packages.
```sh
pip3 install -r requirements.txt
```

7. Install Gunicorn, a Python WSGI HTTP Server for UNIX.
```sh
pip3 install gunicorn
```

8. Run the Flask application with Gunicorn.
```sh
gunicorn -w 4 main:app
```

9. Now, your application should be running on `http://your_vps_ip:8000`.

10. To make the application accessible on port 80, install and configure Nginx.
```sh
sudo apt-get install nginx
```

11. Remove the default Nginx configuration.
```sh
sudo rm /etc/nginx/sites-enabled/default
```

12. Create a new Nginx configuration for your application.
```sh
sudo nano /etc/nginx/sites-available/readallcomics
```

13. Add the following configuration, replacing `your_vps_ip` with your VPS's IP address.
```nginx
server {
    listen 80;
    server_name your_vps_ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

14. Enable the new configuration.
```sh
sudo ln -s /etc/nginx/sites-available/readallcomics /etc/nginx/sites-enabled/
```

15. Restart Nginx.
```sh
sudo service nginx restart
```

Now, your application should be accessible at `http://your_vps_ip`.

