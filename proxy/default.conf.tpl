server {
    listen 80;
    listen [::]:80;
    server_name api-dev.*;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api-dev.*;

    ssl_certificate /etc/nginx/ssl/live/api-dev.lumian.ai/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/live/api-dev.lumian.ai/privkey.pem;

    location / {
        uwsgi_pass ${API_HOST}:${API_PORT};
        include /etc/nginx/uwsgi_params;
        client_max_body_size 10M;
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name app-dev.*;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name app-dev.*;

    ssl_certificate /etc/nginx/ssl/live/api-dev.lumian.ai/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/live/api-dev.lumian.ai/privkey.pem;

    location / {
        proxy_pass http://${WEB_HOST}:${WEB_PORT};
    }
}