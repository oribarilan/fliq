from fliq import q

seq = (q(range(100)).
       where(lambda x: x > 50).
       select(lambda x: x / 2).
       first_or_default(lambda x: x > 100, default=5))

print(seq)
