FROM redis:alpine

RUN mkdir -p /data && chmod 755 /data

COPY redis.conf /usr/local/etc/redis/redis.conf

EXPOSE 6379

CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
