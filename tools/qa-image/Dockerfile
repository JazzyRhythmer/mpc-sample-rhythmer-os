# The native update checker uses unzip as on the stock MPC. Keep this QA
# dependency in the SSD-backed VM rather than installing host tools.
FROM rhythmer-upstream-builder
RUN apt-get update && apt-get install -y --no-install-recommends unzip && rm -rf /var/lib/apt/lists/*
