FROM quay.io/keycloak/keycloak:latest as builder

# Enable health and metrics support
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true

# Configure database vendor for PostgreSQL
ENV KC_DB=postgres

WORKDIR /opt/keycloak

# Build the custom image
RUN /opt/keycloak/bin/kc.sh build

FROM quay.io/keycloak/keycloak:latest
COPY --from=builder /opt/keycloak/ /opt/keycloak/

# Default to Postgres and listen on 8080
ENV KC_DB=postgres
ENV KC_HTTP_RELATIVE_PATH=/

ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
