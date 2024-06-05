source ~/.bashrc
out="$GIT_PATH/dependency-parser/out.svg"
python3 $GIT_PATH/dependency-parser/mod_parser.py $GIT_PATH
