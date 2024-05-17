This contains the sample nginx conf file for your site to put in sites-available

server {
    listen 80;
    server_name server;
    proxy_headers_hash_max_size 1024;
    proxy_headers_hash_bucket_size 128;

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:5000;
    }

    location /socket.io {
        include proxy_params;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_redirect off;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://127.0.0.1:5000/socket.io;
    }
    
    sendfile on;
}
