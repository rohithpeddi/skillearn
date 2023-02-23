# skillearn

### Redis
#### Ubuntu
- sudo apt-get update
- sudo apt-get install redis-server
- sudo systemctl start redis-server
- sudo systemctl status redis-server

#### Windows
- Setup docker 
- docker pull redis
- docker run --name=redis-devel --publish=6379:6379 --hostname=redis --restart=on-failure --detach redis:latest


### Frontend
##### Install 
- git clone https://github.com/rohithpeddi/skillearn.git
- cd datacollection/error/frontend
- npm install
##### Run
- Close google chrome app
- Run the command in terminal:
  - open /Applications/Google\ Chrome.app --args --user-data-dir="/var/tmp/chrome-dev-disabled-security" --disable-web-security --disable-site-isolation-trials
- Run the below command above changed directory 
  - npm start
  - (The above should automatically start localhost:3000 in google chrome)

