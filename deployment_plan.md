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
      cd ~/Desktop/GHII/OERR_Reference/OERR_Central_repo  <! -- the dirs are different, one ends with .git-->
      git remote remove origin 
      git remote add central ghii@192.168.1.42:/home/ghii/Desktop/GHII/OERR_Reference/OERR_Central_repo.git
      git push --all central
      git push --tags central
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
      git remote add origin ghii@192.168.1.42:/home/ghii/Desktop/GHII/OERR_Reference/OERR_Central_repo.git
   ```

3. protect files
   ```bash
      git ls-files config/* logs/* uwsgi.ini requirements.txt .gitignore | xargs git update-index --skip-worktree
   ```

4. get all changes
   ```bash
    git pull origin main --rebase=false
    ```

5. get correct ward configs
   ```bash
   cat wards.config.example > config/wards.config
   ```