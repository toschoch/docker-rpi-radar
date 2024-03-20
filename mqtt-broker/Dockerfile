FROM arm32v6/eclipse-mosquitto:2.0.18


ARG CONFIG_FILE=/mosquitto/config/mosquitto.conf
ENV CONFIG_FILE=$CONFIG_FILE
COPY mosquitto.conf $CONFIG_FILE
COPY passwd /mosquitto/config/passwd
COPY hc.sh /mosquitto/hc.sh

COPY docker-entrypoint.sh /
COPY expand_vars.sh /
RUN chmod +x /mosquitto/hc.sh /docker-entrypoint.sh /expand_vars.sh

HEALTHCHECK --start-period=5s --timeout=10s --interval=180s --retries=1 \
    CMD /mosquitto/hc.sh

CMD ["/usr/sbin/mosquitto", "-c", "$CONFIG_FILE"]
