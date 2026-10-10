# Experiment 2 - Containerization
Aim: package this Streamlit irrigation prototype consistently. Tools: Docker Desktop (Linux containers), Docker Hub, Python.

```powershell
docker build -t sugarcane-irrigation .
docker run -d --name canewise-demo -p 8501:8501 -v canewise-data:/app/data sugarcane-irrigation
docker ps
docker logs canewise-demo
docker inspect canewise-demo
```
Open http://localhost:8501. The non-root image includes a health check at /_stcore/health. The volume preserves SQLite and dataset files; remove the volume only if you deliberately want to reset data.

Docker Hub publication (manual, not performed):
```powershell
docker login
docker tag sugarcane-irrigation YOUR_USERNAME/sugarcane-irrigation:1.0
docker push YOUR_USERNAME/sugarcane-irrigation:1.0
```
Evidence: screenshot Docker image list, healthy running container, logs, browser dashboard and advisory saved confirmation. Preserve actual command output in docs/evidence. No Hub publication is claimed without a successful push. Record build duration, image ID, host and access result. Conclusion must use observed results.

To show newly generated results in a future Docker demo, add a read-only bind mount when creating the container:
```powershell
$benchmarkResults = (Resolve-Path cloud/results).Path
docker run -d --name canewise-demo -p 8501:8501 -v canewise-data:/app/data --mount "type=bind,source=$benchmarkResults,target=/app/cloud/results,readonly" sugarcane-irrigation
```
Use this as the alternative run command after benchmarks exist; a previous container with the same name must be stopped/removed first. Preserve the canewise-data volume.
