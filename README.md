# Putting the project into production with uWSGI and Nginx

## App server uWSGI

Install the dependencies. Possibly, they are already installed (you don't need to be inside the venv):

```
$ sudo apt install gcc build-essential python3-dev`
```

Install uWSGI inside the venv and check the basic operation in HTTP mode

```
(env) $ pip install uwsgi
(env) $ uwsgi --http :8000 --module djangify.wsgi --master --buffer-size 32768
```

As we have added a new package to the project (uwsgi), we will need to update it in the requirements file:

```
(env) $ pip freeze > requirements.txt
```

## Web server Nginx

To serve static files, the web server is not needed, as it is more efficient than Django itself, which must remain to execute dynamic code. In this case, Nginx will be used as the web server:

```
$ sudo apt install nginx
```

Verify that Nginx is working by visiting http://localhost

Static files (images, CSS, JS) are spread across several folders in the Django web application, some of them inside the code libraries (which are in the venv). You need to compile all the static files. The STATIC_ROOT variable in settings.py will indicate which folder to dump all these files into.

Add to `settings.py`:

```
STATIC_URL = '/static'
STATIC_ROOT = BASE_DIR / '/static'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'myweb/static'),]
```

Now you can compile the static files, which will remain in the static/ folder:

```
(env) $ python3 manage.py collectstatic
```

Proceed to configure Nginx. Before doing so, make a backup of the default configuration file:

```
$ sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bkp
```

Enter the `default` file with the configuration adapted from the official uWSGI documentation. Remember that Nginx has to be listening on port 80 and redirecting requests to uWSGI on port 8001:

```
# arxiu /etc/nginx/sites-available/default

upstream django {
    # server unix:///path/to/your/mysite/mysite.sock; # possible versió file socket
    server 127.0.0.1:8001; # connexió via port socket
}
 
server {
    listen      80;
    charset     utf-8;
    client_max_body_size 75M;   # adjust to taste

    # Nginx serveix directament els arxius media i static
    location /media  {
        alias /home/super/djangify-web/media;
    }
 
    location /static {
        alias /home/super/djangify-web/static;
    }

    # Redirigir petició a l'app Django
    location / {
        uwsgi_pass  django;
        include     /etc/nginx/uwsgi_params; # aquest arxiu ja ve per defecte a la instal·lació de Nginx
    }
}
```

Restart Nginx:

```
$ sudo systemctl restart nginx.service
```

If you now visit localhost you should get a 502 Bad Gateway code, as uWSGI is not started on port 8001 as indicated in the configuration file. Nginx is running, but it is waiting to find the uWSGI application server which is not yet running.

Launch the web application with uWSGI on port 8001:

```
(env) $ uwsgi --socket :8001 --module djangify.wsgi --master --buffer-size 32768
```

If the CSS files are still not displayed, examine one of them by visiting the CSS file with the browser. If it gives a 403 Forbidden error, it is probably due to the file system, which does not allow Nginx to enter the Django project folder. If you are in IsardVDI you can solve it with:

```
$ chmod 755 ~
```

Reload the page and see if it works now.

## Enabling uWSGI at boot with supervisord

The website is now working, but it does not start when the machine boots, since uWSGI is not installed as a system module, but has been run manually.

`Supervisord` is a good tool to facilitate startup at operating system boot. It will also ensure that there is an instance always running, which is known as the watchdog function.

Install supervisord:

```
$ sudo apt install supervisor
```

Edit the configuration file for our app:

```
# arxiu /etc/supervisor/conf.d/djangify-web.conf
[program:djangify]
directory=/home/super/djangify-web
command=/home/super/env/bin/uwsgi --socket :8001 --module djangify.wsgi --master --buffer-size 32768
```

Supervisord needs to be reloaded:

```
$ sudo supervisorctl reload
```

Check if it is running:

```
$ sudo supervisorctl status
```

If something doesn't work as expected, analyze the logs:

```
sudo supervisorctl tail -f djangobase stderr
```
