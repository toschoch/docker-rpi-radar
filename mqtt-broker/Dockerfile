FROM arm32v6/eclipse-mosquitto:2.0.10

COPY mosquitto.conf /mosquitto/config/mosquitto.conf
COPY passwd /mosquitto/config/passwd
COPY hc.sh /mosquitto/hc.sh
RUN chmod +x /mosquitto/hc.sh

HEALTHCHECK --start-period=5s --timeout=10s --interval=180s --retries=1 \
    CMD /mosquitto/hc.sh