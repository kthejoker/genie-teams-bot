cd simple-host-bot
python3 -m venv hostbot
source hostbot/bin/activate

pip install -r requirements.txt
if [ $# -eq 0 ]
    then
        python3 app.py prod $BOT_PREFIX
    else
        python3 app.py $1 $BOT_PREFIX  
fi