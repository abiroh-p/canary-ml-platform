# ---- builder ----
FROM golang:1.26 AS builder

WORKDIR /build
COPY go.mod go.sum* ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /build/gateway ./cmd/gateway

# ---- runtime ----
FROM gcr.io/distroless/static-debian12

COPY --from=builder /build/gateway /gateway

EXPOSE 8080 8081

USER nonroot:nonroot

ENTRYPOINT ["/gateway"]
