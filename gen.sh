source ~/.bashrc
python3 mod_parser.py $GIT_PATH > test.txt && gen_graph test.txt && open out.svg
