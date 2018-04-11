for i in {1..70}
do
    python tester.py 0 4 --generate_file --learning_iteration 0
    python tester.py 1 4 --generate_file --learning_iteration 1
    python tester.py 2 4 --generate_file --learning_iteration 2
    python tester.py 3 4 --generate_file --learning_iteration 3
done
