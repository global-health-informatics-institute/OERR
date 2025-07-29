For Laptop
1. get ip address
   ```bash
      hostname -I
   ```

2. create central git repo
   ```bash
   mkdir -p /home/ghii/Desktop/GHII/OERR_Reference/OERR_Central_repo.git
   cd /home/ghii/Desktop/GHII/OERR_Reference/OERR_Central_repo.git
   git init --bare
   ```

3. set origin
   ```bash
      cd ~/Desktop/GHII/OERR_Reference/OERR_Central_repo
      git remote remove origin 
      git remote add origin ghii@<192.168.1.42>:/home/ghii/Desktop/GHII/OERR_Reference/OERR_Central_repo.git
      git push origin oerr_central_branch
   ```




---
For cartop
1. Resolve changes and switch branch
   ```bash
      git add . && git commit -m "resolve uncommited" && git switch -c lan_workflow
   ```



2. set origin
   ```bash
      cd OERR
      git remote remove origin
      git remote add origin ghii@10.40.3.83:~/OERR_Central_repo.git
   ```

3. protect files
   ```bash
      git ls-files config/* logs/* uwsgi.ini requirements.txt .gitignore | xargs git update-index --skip-worktree
   ```

4. remove brocken stash
   ```bash
   rm .git/refs/stash
   ```

5. fetch objects
   ```bash
   git fetch
   ```

6. check ourt app.py
   ```bash
   # get branch which is likely to cause conflicts
   git checkout origin/oerr_central_branch  -- app.py
   ```

7. get all changes
   ```bash
    git pull origin main --rebase=false
    ```

8. get correct ward configs
   ```bash
   cat wards.config.example > config/wards.config
   ```