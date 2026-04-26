# S3 CLI Cheatsheet

Examples use

- **Base Directory:** `/workspaces/climatology`  
- **Working Directory for Commands:** `./output/barotropic_stirring-T85`  
- **Bucket:** `s3://atmos` (I used idrive e2)

### Basic Navigation

| Action | Command |
| :--- | :--- |
| **List Top-level** | `aws s3 ls s3://atmos` |
| **List Recursively** | `aws s3 ls s3://atmos --recursive --human-readable` |
| **Check Remote Size** | `aws s3 ls s3://atmos/barotropic_stirring-T85 --recursive --summarize` |

### Uploading (Local to S3)

| Action | Command |
| :--- | :--- |
| **Upload Single File** | `aws s3 cp output/barotropic_stirring-T85/checkpoint.pt s3://atmos/checkpoints/` |
| **Upload Full Directory** | `aws s3 cp output/barotropic_stirring-T85/ s3://atmos/barotropic_stirring-T85/ --recursive` |
| **Sync (Upload New/Changed)** | `aws s3 sync output/barotropic_stirring-T85/ s3://atmos/barotropic_stirring-T85/` |

### Downloading (S3 to Local)

| Action | Command |
| :--- | :--- |
| **Download Single File** | `aws s3 cp s3://atmos/barotropic_stirring-T85/results.nc output/barotropic_stirring-T85/` |
| **Download Full Directory** | `aws s3 cp s3://atmos/barotropic_stirring-T85/ output/barotropic_stirring-T85/ --recursive` |
| **Sync (Download Missing)** | `aws s3 sync s3://atmos/barotropic_stirring-T85/ output/barotropic_stirring-T85/` |

### Advanced Operations

| Action | Command |
| :--- | :--- |
| **Dry Run (Preview)** | `aws s3 sync output/barotropic_stirring-T85/ s3://atmos/barotropic_stirring-T85/ --dryrun` |
| **Filter by Extension** | `aws s3 sync output/barotropic_stirring-T85/ s3://atmos/ --exclude "*" --include "*.nc"` |
| **Remove from S3** | `aws s3 rm s3://atmos/barotropic_stirring-T85/ --recursive` |

---

### Efficiency Tips for T85 Data

* **Size-Only Sync:** Skips MD5 checksums; essential for fast overhead on large datasets.
    * `aws s3 sync output/barotropic_stirring-T85/ s3://atmos/path --size-only`
* **Performance Tuning:** Increase concurrency for parallel file transfers.
    * `aws configure set s3.max_concurrent_requests 20`
* **Large File Handling:** Optimize for high-resolution spectral tensors.
    * `aws configure set s3.multipart_threshold 64MB`
    * `aws configure set s3.multipart_chunksize 16MB`