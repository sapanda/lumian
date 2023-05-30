server {
    listen ${LISTEN_PORT};
    server_name api-dev.*;

    location / {
        uwsgi_pass ${API_HOST}:${API_PORT};
        include /etc/nginx/uwsgi_params;
        client_max_body_size 10M;
    }
}

server {
    listen ${LISTEN_PORT};
    server_name app-dev.*;

    location / {
        proxy_pass http://${WEB_HOST}:${WEB_PORT};
    }
}