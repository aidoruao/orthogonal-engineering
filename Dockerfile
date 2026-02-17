FROM python:3.11-slim

WORKDIR /workspace

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install PyYAML for generators
RUN pip install --no-cache-dir pyyaml

# Copy project files
COPY . .

# Default entry point for 1B LOC verification
# Can be overridden with: docker run <image> python <script>
ENTRYPOINT ["python"]
CMD ["generators/verify_1b_loc.py"]
