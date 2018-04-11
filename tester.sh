for d in {0..3}
do
    for i in {1..50}
    do
        python tester.py $d 0 --generate_file
        python tester.py $d 1
        python tester.py $d 2
        python tester.py $d 3
        python tester.py $d 4
    done
done
