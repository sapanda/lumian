server {
    listen ${LISTEN_PORT};
    server_name api-dev.lumian.ai;

    location /static {
        alias /vol/static;
    }

    location / {
        uwsgi_pass ${APP_HOST}:${APP_PORT};
        include /etc/nginx/uwsgi_params;
        client_max_body_size 10M;
    }
}

server {
    listen ${LISTEN_PORT};
    server_name app-dev.lumian.ai;

    location / {
        proxy_pass ${SERVER_ADDRESS}:8002;
    }
}