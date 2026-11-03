# Private PHP-FPM backend for the existing static portfolio Nginx.
FROM php:8.4-fpm-alpine
RUN apk add --no-cache sqlite-dev \
    && docker-php-ext-install -j"$(nproc)" pdo_sqlite \
    && mkdir -p /app /data \
    && chown -R 10001:10001 /app /data \
    && printf '%s\n' \
       '[www]' \
       'listen = 9000' \
       'user = www-data' \
       'group = www-data' \
       'pm = dynamic' \
       'pm.max_children = 4' \
       'pm.start_servers = 1' \
       'pm.min_spare_servers = 1' \
       'pm.max_spare_servers = 2' \
       'clear_env = no' \
       'catch_workers_output = yes' \
       > /usr/local/etc/php-fpm.d/zz-portfolio.conf \
    && rm -f /usr/local/etc/php-fpm.d/www.conf
COPY --chown=10001:10001 index.php /app/index.php
USER 10001:10001
WORKDIR /app
EXPOSE 9000
CMD ["php-fpm", "-F"]
