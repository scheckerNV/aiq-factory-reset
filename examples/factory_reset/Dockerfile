FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy the entire repo
COPY . /workspace/

# Set version for setuptools-scm to match what factory_reset expects
ENV SETUPTOOLS_SCM_PRETEND_VERSION=1.2.0

# Fix the dependency issue by temporarily removing the version constraint
RUN sed -i 's/aiqtoolkit~=1.2/aiqtoolkit/g' /workspace/examples/factory_reset/pyproject.toml

# Install AIQ toolkit from source first (without extras to avoid conflicts)
RUN pip install -e "."

# Install langchain plugin separately
RUN pip install -e "./packages/aiqtoolkit_langchain"

# Install factory reset package
RUN pip install -e "/workspace/examples/factory_reset"

# Set environment
ENV AIQ_CONFIG_FILE=/workspace/examples/factory_reset/src/aiq_dgx_factory_reset/configs/simple_network.yml

EXPOSE 8000

ENTRYPOINT ["aiq"]
CMD ["serve", "--config_file", "/workspace/examples/factory_reset/src/aiq_dgx_factory_reset/configs/simple_network.yml", "--port", "8000", "--host", "0.0.0.0"]
