# PR #18 Test Data

This directory contains comprehensive test data files for testing the PR #18 verification system. The test data includes mock repository data, audit trails, dependency graphs, and performance metrics totaling approximately 200,000 lines of code.

## Directory Structure

```
tests/pr18_test_data/
├── README.md (this file)
├── mock_repository_files_1.json
├── mock_repository_commits_2.json
├── mock_repository_branches_3.json
├── mock_repository_prs_issues_4.json
├── audit_trail_file_operations_1.jsonl
├── audit_trail_api_operations_2.jsonl
├── audit_trail_security_events_3.jsonl
├── dependency_graph_npm_1.json
├── dependency_graph_python_2.json
├── performance_benchmarks.csv
├── stress_test_results.csv
└── resource_utilization_metrics.csv
```

## File Descriptions

### Mock Repository Data (~80,000 lines)

#### 1. `mock_repository_files_1.json` (~20k lines)
**Purpose**: Simulates a complete file listing for a repository scan.

**Contents**:
- 5,000 mock file entries
- File paths, sizes, checksums (SHA-256)
- Modification timestamps
- File permissions and types
- Line counts for code files
- Metadata including author, commit hash, and branch

**Use Cases**:
- Testing file system scanning logic
- Validating checksum verification
- Testing file metadata processing
- Simulating large repository scans

**Data Structure**:
```json
{
  "repository": "orthogonal-engineering/test-repo",
  "scan_timestamp": "2026-01-26T10:00:00Z",
  "total_files": 5000,
  "files": [
    {
      "path": "src/utils_42.py",
      "size": 12345,
      "sha256": "abc123...",
      "modified": "2025-06-15T14:30:00",
      "permissions": "644",
      "type": "file",
      "line_count": 154,
      "is_executable": false,
      "is_symlink": false,
      "metadata": {
        "author": "user1",
        "last_commit": "a1b2c3d4",
        "branch": "main"
      }
    }
  ]
}
```

#### 2. `mock_repository_commits_2.json` (~20k lines)
**Purpose**: Simulates a complete commit history for a repository.

**Contents**:
- 5,000 commit entries
- Full commit metadata (SHA, parent, author, committer)
- Commit messages following conventional commit format
- Statistics (additions, deletions, files changed)
- GPG signature verification status

**Use Cases**:
- Testing commit history analysis
- Validating commit chain integrity
- Testing commit statistics aggregation
- Simulating repository history

**Data Structure**:
```json
{
  "repository": "orthogonal-engineering/test-repo",
  "branch": "main",
  "total_commits": 5000,
  "commits": [
    {
      "sha": "abc123...",
      "parent": "def456...",
      "author": {
        "name": "Alice Developer",
        "email": "alice@example.com",
        "date": "2025-03-15T10:30:00"
      },
      "message": "feat: add new feature",
      "stats": {
        "additions": 250,
        "deletions": 50,
        "total": 300
      },
      "verified": true
    }
  ]
}
```

#### 3. `mock_repository_branches_3.json` (~20k lines)
**Purpose**: Simulates branch and tag structures.

**Contents**:
- 3,000 branch entries
- 2,000 tag entries
- Branch protection status
- Ahead/behind statistics
- Tag annotations and signatures

**Use Cases**:
- Testing branch management logic
- Validating tag processing
- Testing branch protection rules
- Simulating multi-branch workflows

**Data Structure**:
```json
{
  "repository": "orthogonal-engineering/test-repo",
  "total_branches": 3000,
  "total_tags": 2000,
  "branches": [
    {
      "name": "feature/auth-42",
      "commit": "abc123...",
      "protected": false,
      "behind": 15,
      "ahead": 3
    }
  ],
  "tags": [
    {
      "name": "v1.2.3",
      "commit": "def456...",
      "verified": true,
      "type": "annotated"
    }
  ]
}
```

#### 4. `mock_repository_prs_issues_4.json` (~20k lines)
**Purpose**: Simulates pull requests and issues.

**Contents**:
- 2,500 pull request entries
- 2,500 issue entries
- Full PR/issue metadata
- Review and comment counts
- Labels and milestones

**Use Cases**:
- Testing PR processing logic
- Validating issue tracking
- Testing merge status detection
- Simulating collaborative workflows

### Test Fixtures for Verification (~60,000 lines)

#### 5. `audit_trail_file_operations_1.jsonl` (~20k lines)
**Purpose**: Audit trail for file system operations.

**Contents**:
- 20,000 file operation log entries (JSONL format)
- Operations: create, read, update, delete, move, copy, chmod, chown
- Checksums before and after operations
- Success/failure status with error codes
- Session tracking and IP addresses

**Use Cases**:
- Testing audit log processing
- Validating checksum verification workflows
- Testing error handling
- Simulating file operation monitoring

**Data Structure** (one JSON object per line):
```json
{"timestamp": "2025-06-15T14:30:00", "operation": "update", "resource": "src/core/file.py", "user": "alice", "success": true, "checksum_before": "abc123...", "checksum_after": "def456...", "duration_ms": 250}
```

#### 6. `audit_trail_api_operations_2.jsonl` (~20k lines)
**Purpose**: Audit trail for API operations.

**Contents**:
- 20,000 API request log entries (JSONL format)
- HTTP methods, endpoints, status codes
- Request/response sizes
- Rate limiting information
- Cache hit statistics

**Use Cases**:
- Testing API monitoring
- Validating rate limit enforcement
- Testing performance metrics collection
- Simulating API usage patterns

**Data Structure**:
```json
{"timestamp": "2025-06-15T14:30:00", "request_id": "abc123", "method": "GET", "endpoint": "/api/v1/repos", "status_code": 200, "duration_ms": 45, "cache_hit": true, "rate_limit_remaining": 4500}
```

#### 7. `audit_trail_security_events_3.jsonl` (~20k lines)
**Purpose**: Audit trail for security events.

**Contents**:
- 20,000 security event log entries (JSONL format)
- Login attempts, authentication events
- Permission changes
- Suspicious activity detection
- Risk scoring and alerting

**Use Cases**:
- Testing security monitoring
- Validating threat detection
- Testing MFA enforcement
- Simulating security incident response

**Data Structure**:
```json
{"timestamp": "2025-06-15T14:30:00", "event_type": "login_success", "severity": "info", "user": "alice", "ip_address": "192.168.1.100", "mfa_used": true, "risk_score": 15, "alert_sent": false}
```

### Dependency Graph Test Data (~40,000 lines)

#### 8. `dependency_graph_npm_1.json` (~20k lines)
**Purpose**: Simulates npm/JavaScript dependency graph with edge cases.

**Contents**:
- 5,000 npm package entries
- Regular dependencies and dev dependencies
- **Circular dependency test cases** (marked with `"circular": true`)
- **Missing dependency scenarios** (marked with `"resolved": false`)
- Vulnerability and deprecation flags

**Use Cases**:
- Testing dependency resolution
- Validating circular dependency detection
- Testing missing dependency handling
- Simulating npm ecosystem

**Key Features**:
- ~1% of dependencies are circular
- ~2% of dependencies are missing
- Includes version ranges and integrity hashes
- Simulates real-world package structures

#### 9. `dependency_graph_python_2.json` (~20k lines)
**Purpose**: Simulates Python/PyPI dependency graph with conflicts.

**Contents**:
- 5,000 Python package entries
- Complex version specifiers
- **Circular dependencies** (~0.5%)
- **Missing packages** (~1%)
- **Version conflicts** (~1%)
- Extras and optional dependencies

**Use Cases**:
- Testing Python dependency resolution
- Validating version conflict detection
- Testing extras handling
- Simulating PyPI ecosystem

**Key Features**:
- Realistic version specifiers (==, >=, ~=, ranges)
- Package extras (dev, test, docs, async)
- Security advisories
- Yanked package versions

### Performance Test Datasets (~20,000 lines)

#### 10. `performance_benchmarks.csv` (~10k lines)
**Purpose**: Benchmark data for various operations.

**Contents**:
- 10,000 benchmark entries
- Operations: file I/O, API requests, database queries, caching, hashing
- Performance metrics: duration, CPU usage, memory usage
- Dataset size variations (100 to 1,000,000 items)
- Concurrency levels (1 to 32 threads)

**Use Cases**:
- Testing performance analysis
- Validating benchmark processing
- Testing metric aggregation
- Simulating load testing

**Columns**:
```
timestamp, test_run_id, operation, dataset_size, duration_ms, cpu_usage_percent,
memory_usage_mb, io_operations, cache_hits, cache_misses, success, error_code,
concurrency_level, iterations
```

#### 11. `stress_test_results.csv` (~5k lines)
**Purpose**: Stress test results with detailed metrics.

**Contents**:
- 5,000 stress test entries
- Scenarios: concurrent reads/writes, API floods, memory/CPU/IO stress
- User simulation (10 to 10,000 users)
- Response time percentiles (p50, p95, p99)
- Resource utilization peaks

**Use Cases**:
- Testing stress test analysis
- Validating performance degradation detection
- Testing percentile calculations
- Simulating high-load scenarios

**Columns**:
```
timestamp, test_scenario, users_simulated, requests_per_second, total_requests,
successful_requests, failed_requests, timeout_requests, avg_response_time_ms,
p50_response_time_ms, p95_response_time_ms, p99_response_time_ms, throughput_mbps,
error_rate_percent, cpu_peak_percent, memory_peak_mb, disk_io_read_mbps, ...
```

#### 12. `resource_utilization_metrics.csv` (~5k lines)
**Purpose**: System resource utilization over time.

**Contents**:
- 5,000 resource metric entries
- Multiple services (API server, database, cache, workers, etc.)
- Comprehensive metrics: CPU, memory, disk, network
- Process-level details (threads, connections, file descriptors)
- Time-series data for trend analysis

**Use Cases**:
- Testing resource monitoring
- Validating capacity planning
- Testing anomaly detection
- Simulating production metrics

**Columns**:
```
timestamp, service, host, cpu_percent, memory_used_mb, memory_available_mb,
disk_used_gb, disk_available_gb, network_in_mbps, network_out_mbps,
active_connections, thread_count, process_count, file_descriptors, ...
```

## Usage in Tests

### Loading JSON Data

```python
import json

# Load mock repository files
with open('tests/pr18_test_data/mock_repository_files_1.json', 'r') as f:
    file_data = json.load(f)
    
print(f"Total files: {file_data['total_files']}")
for file in file_data['files']:
    print(f"Processing {file['path']} - SHA256: {file['sha256']}")
```

### Loading JSONL Data

```python
import json

# Load audit trail (JSONL format - one JSON object per line)
audit_entries = []
with open('tests/pr18_test_data/audit_trail_file_operations_1.jsonl', 'r') as f:
    for line in f:
        audit_entries.append(json.loads(line))

print(f"Total audit entries: {len(audit_entries)}")
```

### Loading CSV Data

```python
import csv

# Load performance benchmarks
with open('tests/pr18_test_data/performance_benchmarks.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"Operation: {row['operation']}, Duration: {row['duration_ms']}ms")
```

### Testing Circular Dependencies

```python
import json

with open('tests/pr18_test_data/dependency_graph_npm_1.json', 'r') as f:
    dep_graph = json.load(f)

# Find circular dependencies
for package in dep_graph['packages']:
    circular_deps = [d for d in package['dependencies'] if d.get('circular', False)]
    if circular_deps:
        print(f"Package {package['name']} has circular dependency: {circular_deps[0]['name']}")
```

### Testing Missing Dependencies

```python
import json

with open('tests/pr18_test_data/dependency_graph_python_2.json', 'r') as f:
    dep_graph = json.load(f)

# Find missing dependencies
for package in dep_graph['packages']:
    missing_deps = [d for d in package['dependencies'] if not d.get('resolved', True)]
    if missing_deps:
        print(f"Package {package['name']} has missing dependency: {missing_deps[0]['name']}")
        print(f"Error: {missing_deps[0].get('error')}")
```

### Testing Version Conflicts

```python
import json

with open('tests/pr18_test_data/dependency_graph_python_2.json', 'r') as f:
    dep_graph = json.load(f)

# Find version conflicts
for package in dep_graph['packages']:
    conflicts = [d for d in package['dependencies'] if 'conflicts_with' in d]
    if conflicts:
        print(f"Version conflict in {package['name']}")
        print(f"Requires {conflicts[0]['name']} {conflicts[0]['specifier']}")
        print(f"Conflicts with {conflicts[0]['conflicts_with']}")
```

## Data Generation

All test data was generated deterministically using Python scripts with fixed random seeds where appropriate. The data is:

- **Realistic**: Mimics real-world repository and system data
- **Comprehensive**: Covers normal cases and edge cases
- **Valid**: All JSON, JSONL, and CSV files are properly formatted
- **Reproducible**: Can be regenerated with the same parameters
- **Large-scale**: ~200,000 lines total to test performance at scale

## Test Data Characteristics

### Mock Repository Data
- Simulates a large, active repository
- Multiple file types and extensions
- Realistic commit history
- Various branch naming conventions
- Comprehensive PR/issue metadata

### Audit Trails
- Time-series data spanning up to 1 year
- Mix of successful and failed operations
- Realistic error patterns
- Session and IP tracking
- Security event severity levels

### Dependency Graphs
- Multiple ecosystems (npm, PyPI)
- Edge cases: circular deps, missing deps, version conflicts
- Vulnerability and deprecation data
- Realistic package naming and versioning

### Performance Data
- Multiple test scenarios
- Varying dataset sizes
- Concurrency levels from 1 to 32
- Response time percentiles
- Resource utilization metrics

## Extending the Test Data

To add more test data:

1. Follow the existing data structures
2. Ensure JSON/JSONL/CSV validity
3. Add realistic edge cases
4. Update this README with new file descriptions
5. Maintain deterministic generation for reproducibility

## License

This test data is part of the orthogonal-engineering project and follows the same license.

## Line Count Summary

| File | Format | Lines | Purpose |
|------|--------|-------|---------|
| mock_repository_files_1.json | JSON | ~20,000 | File listings |
| mock_repository_commits_2.json | JSON | ~20,000 | Commit history |
| mock_repository_branches_3.json | JSON | ~20,000 | Branches & tags |
| mock_repository_prs_issues_4.json | JSON | ~20,000 | PRs & issues |
| audit_trail_file_operations_1.jsonl | JSONL | 20,000 | File ops audit |
| audit_trail_api_operations_2.jsonl | JSONL | 20,000 | API ops audit |
| audit_trail_security_events_3.jsonl | JSONL | 20,000 | Security audit |
| dependency_graph_npm_1.json | JSON | ~20,000 | npm dependencies |
| dependency_graph_python_2.json | JSON | ~20,000 | PyPI dependencies |
| performance_benchmarks.csv | CSV | 10,001 | Benchmarks |
| stress_test_results.csv | CSV | 5,001 | Stress tests |
| resource_utilization_metrics.csv | CSV | 5,001 | Resource metrics |
| **TOTAL** | | **~200,000** | |
