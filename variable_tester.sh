for i in {1..50}
do
    python tester.py 0 0 --generate_file --variable_demand
    python tester.py 0 1 --variable_demand
    python tester.py 0 2 --variable_demand
    python tester.py 0 3 --variable_demand
    python tester.py 0 4 --variable_demand
done
