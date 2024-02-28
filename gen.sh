source ~/.bashrc
python3 $GIT_PATH/dependency-parser/mod_parser.py $GIT_PATH > test.txt && gen_graph test.txt && rm test.txt && open out.svg
