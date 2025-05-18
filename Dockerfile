ARG RUST_VERSION="1.86"

FROM rust:$RUST_VERSION AS builder
WORKDIR "/app/"
COPY "." "."
RUN cargo build --release

FROM alpine
WORKDIR "/app/"
COPY --from=builder "/app/target/release/minecraft_server_status" "."

CMD ["./minecraft_server_status"]


# MANUAL BUILD:

# build docker image, save in tar, remove image so only tar remains
# docker build -t "9-fs/minecraft_server_status:latest" --no-cache . && docker save "9-fs/minecraft_server_status:latest" > "docker-image.tar" && docker rmi "9-fs/minecraft_server_status:latest"

# on deployment environment load docker image from tar file
# docker load < "/mnt/user/appdata/docker-image.tar"