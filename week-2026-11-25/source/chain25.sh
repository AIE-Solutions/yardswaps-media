cd "$(dirname "$0")"
until grep -q RECDONE25 ../rec/rec25.log; do sleep 15; done
grep "frames" ../rec/rec25.log
for n in riq3khm rsfmh3l n100 n101 n102 n103 n104; do python3 -I mkdemo5.py ${n}s 2>&1 | tail -2; done
bash batch18.sh riq3khms rsfmh3ls n100s n101s n102s n103s n104s 2>&1 | tail -40
echo CHAIN25DONE
