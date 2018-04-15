for i in {1..300}
do
    python tester.py 0 4 --generate_file --train_learner
    python tester.py 1 4 --generate_file --train_learner
    python tester.py 2 4 --generate_file --train_learner
    python tester.py 3 4 --generate_file --train_learner
done
